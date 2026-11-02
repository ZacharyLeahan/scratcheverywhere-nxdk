#!/usr/bin/env python3
"""Exercise the production Xbox tile builder with upload-failure injection.

SDL allocation/upload services are mocked. The checks cover retained RGBA pixel
content, fallback after failed uploads, and cleanup; they do not qualify GPU output.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--expect-broken", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = (root / "source/renderers/xbox/image_xbox.cpp").read_text()
start = source.index("nonstd::expected<void, std::string> Image_Xbox::buildTiles()")
brace = source.index("{", start)
end, depth = brace + 1, 1
while depth:
    depth += (source[end] == "{") - (source[end] == "}")
    end += 1
body = source[start:end]
prefix = r'''
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
using Uint8 = uint8_t;
using SDL_PixelFormat = int;
constexpr int SDL_PIXELFORMAT_RGBA32=1, SDL_PIXELFORMAT_RGB565=2;
constexpr int SDL_PIXELFORMAT_ARGB1555=3, SDL_PIXELFORMAT_ARGB4444=4;
constexpr int SDL_TEXTUREACCESS_STATIC=0, SDL_BLENDMODE_BLEND=1;
constexpr int SDL_SCALEMODE_PIXELART=1, TILE_SIZE=256;
constexpr uint32_t CODEC_DXT1=5, CODEC_DXT5=6;
static const int ditherMatrix[2][2]={{0,0},{0,0}};
static void require(bool b, const char *s) { if(!b) throw std::runtime_error(s); }
namespace nonstd {
struct unexpected { std::string error; };
inline unexpected make_unexpected(std::string s) { return {s}; }
template<typename T,typename E> struct expected;
template<typename E> struct expected<void,E> {
    bool ok=true;
    expected()=default;
    expected(unexpected):ok(false){}
    bool has_value() const { return ok; }
};
}
struct SDL_Renderer {};
struct SDL_Texture {
    int format, w, h;
    bool live=true;
    std::vector<uint8_t> uploaded;
};
static std::vector<std::unique_ptr<SDL_Texture>> allocated;
static bool enhanced=true, failCompression=false;
static size_t available=64*1024*1024;
static int uploads=0, failUpload=0, destroyed=0, compressed=0;
static void reset() {
    allocated.clear(); enhanced=true; failCompression=false;
    available=64*1024*1024; uploads=failUpload=destroyed=compressed=0;
}
namespace OS { static bool isEnhancedPlatform() { return enhanced; } }
static size_t getAvailablePhysicalMemory() { return available; }
namespace Scratch { static void freeUnusedCostumeImages() {} }
namespace Log { static void logError(std::string) {} static void logWarning(std::string) {} }
static const char *SDL_GetError() { return "injected allocation failure"; }
static bool lastSDLErrorWasOOM() { return failCompression; }
static std::string freeMemKB() { return "test"; }
static SDL_Texture *SDL_CreateTexture(SDL_Renderer*, int fmt, int, int w, int h) {
    auto t=std::make_unique<SDL_Texture>(); t->format=fmt; t->w=w; t->h=h;
    auto *p=t.get(); allocated.push_back(std::move(t)); return p;
}
static void SDL_SetTextureBlendMode(SDL_Texture*,int) {}
static void SDL_SetTextureScaleMode(SDL_Texture*,int) {}
static bool SDL_UpdateTexture(SDL_Texture *t, void*, const void *data, int pitch) {
    require(t->live,"upload after destroy"); ++uploads;
    if(uploads==failUpload) return false;
    const int bpp=t->format==SDL_PIXELFORMAT_RGBA32?4:2;
    t->uploaded.resize(size_t(t->w)*t->h*bpp);
    for(int y=0;y<t->h;++y)
        memcpy(t->uploaded.data()+size_t(y)*t->w*bpp,
               static_cast<const uint8_t*>(data)+size_t(y)*pitch,t->w*bpp);
    return true; // SDL3's success contract.
}
static void safeDestroyTexture(SDL_Texture *&t) {
    if(t) { require(t->live,"double destroy"); t->live=false; ++destroyed; t=nullptr; }
}
static std::vector<uint8_t> encodeRegionDXT(const uint8_t*,int,int,int,int,int,int,int,uint32_t,bool,bool) {
    ++compressed; return {0};
}
static SDL_Texture *createDXTTexture(SDL_Renderer *r,int w,int h,uint32_t codec,const uint8_t*) {
    return failCompression?nullptr:SDL_CreateTexture(r,codec,0,w,h);
}
struct Image_Xbox {
    struct Tile { SDL_Texture *texture=nullptr; int x=0,y=0,w=0,h=0; };
    struct { int width=0,height=0,pitch=0; void *pixels=nullptr; } imgData;
    SDL_Renderer *sdlRenderer=nullptr;
    std::vector<Tile> tiles;
    void destroyTiles() { for(auto &t:tiles) safeDestroyTexture(t.texture); tiles.clear(); }
    nonstd::expected<void,std::string> buildTiles();
};
'''
checks = r'''
static std::vector<uint8_t> pixels() {
    std::vector<uint8_t> data(517*259*4);
    for(int y=0;y<259;++y) for(int x=0;x<517;++x) {
        auto *p=data.data()+(size_t(y)*517+x)*4;
        p[0]=(x*7+y)%256; p[1]=(x+y*13)%256; p[2]=(x*17+y*3)%256;
        p[3]=(x+y)%5?255:128;
    }
    return data;
}
static Image_Xbox image(std::vector<uint8_t> &data) {
    Image_Xbox im; im.imgData={517,259,517*4,data.data()}; return im;
}
static void rgbaMatches(const Image_Xbox &im,const std::vector<uint8_t> &data) {
    for(const auto &tile:im.tiles) {
        require(tile.texture->live,"retained destroyed texture");
        if(tile.texture->format!=SDL_PIXELFORMAT_RGBA32) continue;
        require(tile.texture->uploaded.size()==size_t(tile.w)*tile.h*4,"retained failed upload");
        for(int y=0;y<tile.h;++y) for(int x=0;x<tile.w;++x)
            require(memcmp(tile.texture->uploaded.data()+(size_t(y)*tile.w+x)*4,
                           data.data()+(size_t(tile.y+y)*517+tile.x+x)*4,4)==0,
                    "RGBA tile does not match source pixels");
    }
}
int main() {
 try {
    auto data=pixels();
    reset(); auto im=image(data);
    require(im.buildTiles().has_value(),"successful upload returned error");
    require(im.tiles.size()==6,"missing partial edge tiles");
    require(compressed==0 && destroyed==0,"successful RGBA upload fell back");
    require(uploads==6,"RGBA tiles were not uploaded once each");
    rgbaMatches(im,data); im.destroyTiles(); require(destroyed==6,"RGBA cleanup leaked textures");

    reset(); failUpload=1; im=image(data);
    require(im.buildTiles().has_value(),"failed upload did not fall back");
    require(im.tiles.size()==6 && compressed==1 && destroyed==1,"failed upload cleanup/fallback mismatch");
    require(im.tiles.front().texture->format==CODEC_DXT5,"failed RGBA upload was retained");
    rgbaMatches(im,data); im.destroyTiles(); require(destroyed==7,"mixed cleanup leaked textures");

    for(int mode=0;mode<2;++mode) {
        reset(); if(mode==0) enhanced=false; else available=20*1024*1024;
        im=image(data); require(im.buildTiles().has_value(),"compressed path failed");
        require(uploads==0 && compressed==6,"limited-memory path tried RGBA");
        im.destroyTiles(); require(destroyed==6,"compressed cleanup leaked textures");
    }

    reset(); failUpload=1; failCompression=true; im=image(data);
    require(!im.buildTiles().has_value(),"failed upload plus OOM was reported as success");
    require(im.tiles.empty() && destroyed==1,"failed build retained an unusable texture");
    for(const auto &t:allocated) require(!t->live,"failed build leaked a texture");
    std::cout<<"PASS: RGBA source pixels/partial tiles, failed-upload fallback, memory policy and OOM cleanup\n";
 } catch(const std::exception &e) { std::cerr<<e.what()<<'\n'; return 1; }
}
'''


def run(directory, label, implementation):
    path = directory / (label + ".cpp")
    path.write_text(prefix + implementation + checks)
    binary = directory / label
    subprocess.run(["c++", "-std=c++17", "-O1", "-g",
                    "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                    str(path), "-o", str(binary)], check=True)
    return subprocess.run([str(binary)], capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix="xbox-rgba-upload-") as tmp:
    directory = Path(tmp)
    result = run(directory, "production", body)
    if args.expect_broken:
        assert result.returncode != 0 and "successful RGBA upload fell back" in result.stderr, result
        print("REPRODUCED: production discards successful RGBA uploads")
    else:
        assert result.returncode == 0, result.stderr
        print(result.stdout.strip())
        positive = "if (SDL_UpdateTexture(tile.texture, nullptr, scratch32.data(), tile.w * 4))"
        assert body.count(positive) == 1
        negative = body.replace(positive, positive.replace("if (", "if (!"))
        result = run(directory, "inverted-result", negative)
        assert result.returncode != 0 and "successful RGBA upload fell back" in result.stderr, result
        print("PASS: inverted-result negative control reproduces discarded uploads")
