#!/usr/bin/env python3
"""Exercise the patched SDL command queue with the real XGU batching loop.

GPU submission/wait/reset services are mocked; this is not a pixel or hardware
test. The negative control removes the queue guard and must overflow.
"""
from pathlib import Path
import argparse
import re
import subprocess
import tempfile


root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--driver-source", type=Path)
args = parser.parse_args()
driver = args.driver_source
if driver is None:
    cache = (root / "build-xbox/CMakeCache.txt").read_text()
    match = re.search(r"^SDL3Wrapper_SOURCE_DIR:[^=]+=(.+)$", cache, re.M)
    if not match:
        raise SystemExit("Build Xbox first or provide --driver-source")
    driver = Path(match[1]) / "nxdk_glue/render/SDL_render_xgu.c"
source = driver.read_text()
xgu = (driver.parent / "xgu/xgux.h").read_text()


def function(text, name):
    for match in re.finditer(r"\b" + name + r"\s*\(", text):
        brace = text.find("{", match.end())
        if brace < 0 or ";" in text[match.end():brace]:
            continue
        start = text.rfind("\n", 0, match.start()) + 1
        end, depth = brace + 1, 1
        while depth:
            depth += (text[end] == "{") - (text[end] == "}")
            end += 1
        return text[start:end] + "\n"
    raise AssertionError("Missing function: " + name)


guard = function(source, "ensure_pushbuffer_space")
queue = function(source, "XBOX_RunCommandQueue")
# Replace only the platform-specific barrier in this host fixture.
queue = queue.replace('__asm__ __volatile__ ("sfence" ::: "memory");',
                      "std::atomic_signal_fence(std::memory_order_seq_cst);")
batch = function(xgu, "xgux_draw_arrays")
reserve = re.search(r"#define SDL_XGU_COMMAND_RESERVE_BYTES \\\n[^\n]+", source)
assert reserve
assert "ensure_pushbuffer_space(renderer);" in function(source, "XBOX_SetRenderTarget")

prefix = r'''
#include <atomic>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
using Uint8 = uint8_t;
using XguPrimitiveType = int;
constexpr int XGU_TRIANGLES=0, XGU_POINTS=1, XGU_LINE_STRIP=2;
#define SDL_XGU_MAYBE_UNUSED
#define SDL_XGU_VERTEX_BUFFER_SIZE (4 * 1024 * 1024)
#define PBKIT_PUSHBUFFER_SIZE (512 * 1024)
#define MAX_BATCH 120
#define MIN(a,b) ((a)<(b)?(a):(b))
struct xgu_point_t { float pos[2]; };
struct xgu_render_data_t {
    uint32_t *pushbuffer_head;
    int frame_index=2, vertex_arena_offset=12345, active_render_target=71;
};
struct SDL_Renderer { void *internal; };
enum {
    SDL_RENDERCMD_SETVIEWPORT, SDL_RENDERCMD_SETCLIPRECT,
    SDL_RENDERCMD_SETDRAWCOLOR, SDL_RENDERCMD_CLEAR,
    SDL_RENDERCMD_DRAW_POINTS, SDL_RENDERCMD_DRAW_LINES,
    SDL_RENDERCMD_GEOMETRY, SDL_RENDERCMD_FILL_RECTS,
    SDL_RENDERCMD_COPY, SDL_RENDERCMD_COPY_EX, SDL_RENDERCMD_NO_OP
};
struct SDL_RenderCommand {
    int command;
    SDL_RenderCommand *next;
    struct { struct { size_t first=0, count=6; } draw; } data;
};
static constexpr size_t words=PBKIT_PUSHBUFFER_SIZE/4;
static std::vector<uint32_t> storage(words+64, 0xdecafbad);
static uint32_t *cursor=storage.data();
static bool in_pair=false;
static int pending_gpu=0, resets=0, waits=0, processed=0;
static size_t submitted_words=0;
static void require(bool value, const char *message) {
    if (!value) throw std::runtime_error(message);
}
static uint32_t *pb_begin() {
    require(!in_pair,"nested pb_begin"); in_pair=true; return cursor;
}
static void pb_end(uint32_t *end) {
    require(in_pair,"unpaired pb_end");
    require(end>=cursor && end<=storage.data()+words,"pushbuffer overflow");
    if(end!=cursor) pending_gpu=2;
    submitted_words+=end-cursor; cursor=end; in_pair=false;
}
static int pb_busy() { if(pending_gpu) { --pending_gpu; return 1; } return 0; }
static void Sleep(int) { ++waits; }
static void pb_reset() {
    require(!in_pair,"reset inside begin/end");
    require(!pending_gpu,"reset before GPU idle");
    ++resets; cursor=storage.data();
}
static uint32_t *emit(uint32_t *p,size_t count) {
    for(size_t i=0;i<count;++i) {
        require(p<storage.data()+words,"pushbuffer overflow"); *p++=0x12345678;
    }
    return p;
}
static uint32_t *xgu_begin(uint32_t *p,int) { return emit(p,2); }
static uint32_t *xgu_draw_arrays(uint32_t *p,unsigned,unsigned) { return emit(p,2); }
static uint32_t *xgu_end(uint32_t *p) { return emit(p,2); }
'''
stubs = r'''
static void state_command() { auto *p=pb_begin(); pb_end(emit(p,8)); ++processed; }
static void XBOX_RenderSetViewPort(SDL_Renderer*,SDL_RenderCommand*) { state_command(); }
static void XBOX_RenderSetClipRect(SDL_Renderer*,SDL_RenderCommand*) { state_command(); }
static void XBOX_RenderSetDrawColor(SDL_Renderer*,SDL_RenderCommand*) { state_command(); }
static void XBOX_RenderClear(SDL_Renderer*,SDL_RenderCommand*) { state_command(); }
static void draw(SDL_RenderCommand *cmd,int type) {
    auto *p=pb_begin(); pb_end(emit(p,32));
    xgux_draw_arrays(type,0,cmd->data.draw.count); ++processed;
}
static void XBOX_RenderPoints(SDL_Renderer*,void*,SDL_RenderCommand *c) { draw(c,XGU_POINTS); }
static void XBOX_RenderLines(SDL_Renderer*,void*,SDL_RenderCommand *c) { draw(c,XGU_LINE_STRIP); }
static void XBOX_RenderGeometry(SDL_Renderer*,void*,SDL_RenderCommand *c) { draw(c,XGU_TRIANGLES); }
'''
main = r'''
int main() {
 try {
    xgu_render_data_t data; data.pushbuffer_head=storage.data();
    SDL_Renderer renderer{&data}; uint8_t vertices[16]{};
    std::vector<SDL_RenderCommand> commands(30000);
    for(size_t i=0;i<commands.size();++i) {
        commands[i].command=i%7;
        commands[i].next=i+1<commands.size()?&commands[i+1]:nullptr;
        if(i%1000==4) commands[i].data.draw.count=SDL_XGU_VERTEX_BUFFER_SIZE/sizeof(xgu_point_t);
    }
    require(XBOX_RunCommandQueue(&renderer,commands.data(),vertices,sizeof(vertices)),"queue failed");
    require(processed==int(commands.size()),"commands were dropped");
    require(resets>3 && waits>0,"large queue did not drain and wrap");
    require(submitted_words>words*3,"fixture did not exceed several buffers");
    require(data.frame_index==2 && data.vertex_arena_offset==12345 &&
            data.active_render_target==71,"mid-frame state was changed");
    for(size_t i=words;i<storage.size();++i) require(storage[i]==0xdecafbad,"canary changed");
    // At the reserve boundary the largest possible point command must fit.
    const int before=resets; pending_gpu=2;
    cursor=storage.data()+(PBKIT_PUSHBUFFER_SIZE-SDL_XGU_COMMAND_RESERVE_BYTES)/4;
    SDL_RenderCommand largest{}; largest.command=SDL_RENDERCMD_DRAW_POINTS;
    largest.next=nullptr; largest.data.draw.count=SDL_XGU_VERTEX_BUFFER_SIZE/sizeof(xgu_point_t);
    require(XBOX_RunCommandQueue(&renderer,&largest,vertices,sizeof(vertices)),"largest command failed");
    require(resets==before+1,"reserve boundary did not wrap");
    require(!in_pair,"begin/end left open");
    std::cout<<"PASS: 30000 commands, maximum XGU point batches, GPU-idle wraps, retained frame state and paired begin/end\n";
    return 0;
 } catch(const std::exception &e) { std::cerr<<e.what()<<"\n"; return 1; }
}
'''

with tempfile.TemporaryDirectory(prefix="xbox-sdl-pushbuffer-") as tmp:
    directory = Path(tmp)
    for label, body in [("fixed", queue), ("unguarded", queue.replace(
            "        ensure_pushbuffer_space(renderer);\n", ""))]:
        path = directory / (label + ".cpp")
        path.write_text(prefix + reserve[0] + "\n" + guard + batch + stubs + body + main)
        binary = directory / label
        subprocess.run(["c++", "-std=c++17", "-O2", str(path), "-o", str(binary)], check=True)
        result = subprocess.run([str(binary)], capture_output=True, text=True)
        if label == "fixed":
            assert result.returncode == 0, result.stderr
            print(result.stdout.strip())
        else:
            assert result.returncode != 0 and "pushbuffer overflow" in result.stderr, result
            print("PASS: removing the actual queue guard reproduces overflow")
