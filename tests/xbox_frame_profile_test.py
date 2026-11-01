#!/usr/bin/env python3
"""Verify diagnostic totals include multiple scheduler passes per frame."""
from pathlib import Path
import subprocess
import json
import re
import tempfile
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='xbox-frame-profile-') as tmp:
    tmp = Path(tmp)
    (tmp / 'timer.hpp').write_text('''#pragma once
class Timer { double startTime = 0; public:
inline static double now = 0;
void start() { startTime = now; }
double getTimeMsDouble() { return now - startTime; }
};
''')
    (tmp / 'log.hpp').write_text('''#pragma once
#include <string>
#include <vector>
namespace Log { inline std::vector<std::string> lines; inline void log(std::string s) { lines.push_back(s); } }
''')
    (tmp / 'render.cpp').write_text('''#define SE_XBOX_PROFILE_FRAMES
#define SE_XBOX_PROFILE_THREADS
#include "xbox_frame_profile.hpp"
void renderFrame(double draw, double present) { XboxFrameProfile::render(draw, present); }
''')
    (tmp / 'test.cpp').write_text('''#define SE_XBOX_PROFILE_FRAMES
#define SE_XBOX_PROFILE_THREADS
#include "xbox_frame_profile.hpp"
#include <cassert>
void renderFrame(double, double);
int main() {
for (int i=0;i<120;++i) {
    XboxFrameProfile::poll(.1);
    XboxFrameProfile::work(.2,4.5);
    XboxFrameProfile::work(0,1.5);
    XboxFrameProfile::thread("Player",6,false);
    renderFrame(2,5);
    Timer::now += 40;
    XboxFrameProfile::sample(7);
}
assert(Log::lines.size()==2);
const auto &s=Log::lines[0];
for (const auto *expected : {"fps_x100=2500", "mean_us=40000", "p95_us=40000", "input_us=199", "scripts_us=6000", "render_us=7000", "poll_us=99", "passes=240"}) {
    // Sub-microsecond floating-point rounding is allowed for fractional totals.
    if (std::string(expected)=="input_us=199") assert(s.find("input_us=199")!=s.npos || s.find("input_us=200")!=s.npos);
    else if (std::string(expected)=="poll_us=99") assert(s.find("poll_us=99")!=s.npos || s.find("poll_us=100")!=s.npos);
    else assert(s.find(expected)!=s.npos);
}
assert(Log::lines[1].find("frame_us=6000 calls=120")!=std::string::npos);
for (const auto *expected : {"draw_us=2000", "present_us=5000", "render_phases=120", "slow_polls=0", "over_50ms=0", "over_67ms=0"})
    assert(s.find(expected)!=s.npos);
assert(XboxFrameProfile::count==0 && XboxFrameProfile::passes==0 && XboxFrameProfile::threads.empty());
assert(XboxFrameProfile::renderPhases==0 && XboxFrameProfile::drawSum==0 && XboxFrameProfile::presentSum==0);
for (int i=0;i<120;++i) {
    XboxFrameProfile::poll(i==0 ? 18 : .1);
    XboxFrameProfile::poll(2); // Multiple polls per rendered frame must count.
    XboxFrameProfile::work(0,1);
    Timer::now += i==0 ? 60 : i==1 ? 80 : 40;
    XboxFrameProfile::sample(7);
}
assert(Log::lines.size()==3);
const auto &next=Log::lines[2];
for (const auto *expected : {"mean_us=40500", "draw_us=0", "present_us=0", "render_phases=0", "poll_max_us=18000", "slow_polls=1", "over_50ms=2", "over_67ms=1"})
    assert(next.find(expected)!=next.npos);
assert(XboxFrameProfile::slowPolls==0 && XboxFrameProfile::pollMax==0);
}
''')
    subprocess.run(['c++', '-std=c++17', '-I'+str(tmp), '-I'+str(root/'include'), str(tmp/'test.cpp'), str(tmp/'render.cpp'), '-o', str(tmp/'test')], check=True)
    subprocess.run([str(tmp/'test')], check=True)
print('PASS: integer timing units, percentiles, scheduler totals, sprite costs, draw/present phases, slow polls, hitch counts, window reset')

# Configure the real platform file rather than duplicating its list of enabled
# sources. Any future profiler call site must also be wired into the build.
profile_sources = sorted(p.relative_to(root) for p in (root / 'source').rglob('*.cpp')
                         if 'XboxFrameProfile::' in p.read_text())
assert profile_sources, 'No real profiler call sites found'
with tempfile.TemporaryDirectory(prefix='xbox-profile-cmake-') as tmp:
    tmp = Path(tmp)
    # Populate each platform optimization glob, so the actual CMake include can
    # run without NXDK dependencies. Only configure; do not compile Xbox flags
    # using the host compiler.
    fixture_sources = sorted(set(profile_sources + [Path('source/menus/pauseMenu.cpp'),
                                                   Path('source/runtime/collision.cpp')]))
    for source in fixture_sources:
        path = tmp / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('int fixture_' + re.sub('[^a-zA-Z0-9]', '_', str(source)) + ';\n')
    (tmp / 'CMakeLists.txt').write_text(
        'cmake_minimum_required(VERSION 3.20)\n'
        'project(ProfileWiring CXX)\n'
        'set(CMAKE_EXPORT_COMPILE_COMMANDS ON)\n'
        'include("' + (root / 'cmake/platforms/xbox.cmake').as_posix() + '")\n'
        'add_library(probe OBJECT\n' + '\n'.join(str(s) for s in fixture_sources) + '\n)\n')
    for enabled, threads in ((False, False), (True, False), (True, True)):
        build = tmp / ('enabled' if enabled else 'disabled') / ('threads' if threads else 'frames')
        result = subprocess.run(['cmake', '-S', str(tmp), '-B', str(build),
                                 '-DSE_XBOX_PROFILE_FRAMES=' + ('ON' if enabled else 'OFF'),
                                 '-DSE_XBOX_PROFILE_THREADS=' + ('ON' if threads else 'OFF')],
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert result.returncode == 0, result.stdout
        commands = {Path(row['file']).relative_to(tmp): row['command']
                    for row in json.loads((build / 'compile_commands.json').read_text())}
        for source in fixture_sources:
            defined = bool(re.search(r'(?:^|\s)-DSE_XBOX_PROFILE_FRAMES(?:=1)?(?:\s|$)', commands[source]))
            assert defined == (enabled and source in profile_sources), (source, enabled, commands[source])
            detailed = bool(re.search(r'(?:^|\s)-DSE_XBOX_PROFILE_THREADS(?:=1)?(?:\s|$)', commands[source]))
            assert detailed == (threads and source in profile_sources), (source, threads, commands[source])
print('PASS: actual Xbox CMake enables every profiler call site only in profiling builds')
