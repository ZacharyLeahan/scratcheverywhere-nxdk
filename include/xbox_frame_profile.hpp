#pragma once
#ifdef SE_XBOX_PROFILE_FRAMES
#include <timer.hpp>
#include <log.hpp>
#include <algorithm>
#include <array>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
namespace XboxFrameProfile {
inline Timer interval;
inline std::array<double, 120> periods{};
inline unsigned count = 0;
inline double inputSum = 0, scriptSum = 0, renderSum = 0, pollSum = 0;
inline double drawSum = 0, presentSum = 0, pollMax = 0;
inline unsigned renderPhases = 0, slowPolls = 0;
inline unsigned passes = 0;
inline unsigned previousReportUs = 0;
struct ThreadCost { double ms = 0; unsigned calls = 0; };
inline std::map<std::string, ThreadCost> threads;
inline std::map<std::string, ThreadCost> nativeCosts;
struct NativeScope {
    const std::string &name;
    Timer timer;
    explicit NativeScope(const std::string &value) : name(value) {}
    ~NativeScope() {
        auto &cost = nativeCosts[name];
        cost.ms += timer.getTimeMsDouble(); ++cost.calls;
    }
};
inline void thread(const std::string &name, double ms, bool legacy) {
    auto &cost = threads[(legacy ? "legacy:" : "bytecode:") + name];
    cost.ms += ms; ++cost.calls;
}
inline void poll(double ms) {
    pollSum += ms;
    pollMax = std::max(pollMax, ms);
    if (ms >= 1000.0 / 60.0) ++slowPolls;
}
// Draw measures preparation/queueing, including native NV2A beginFrame waits.
// Present measures the backend's submission/completion/presentation waits;
// neither phase is a GPU-only measurement.
inline void render(double draw, double present) {
    drawSum += draw;
    presentSum += present;
    ++renderPhases;
}
inline void work(double input, double scripts) {
    inputSum += input; scriptSum += scripts; ++passes;
}
inline void sample(double render) {
    const double period = interval.getTimeMsDouble();
    interval.start();
    periods[count++] = period;
    renderSum += render;
    if (count != periods.size()) return;
    Timer reporting;
    auto sorted = periods;
    std::sort(sorted.begin(), sorted.end());
    double total = 0;
    for (double value : periods) total += value;
    const unsigned over50 = std::count_if(periods.begin(), periods.end(), [](double ms) { return ms > 50; });
    const unsigned over67 = std::count_if(periods.begin(), periods.end(), [](double ms) { return ms > 67; });
    char line[640];
    // NXDK's default printf omits floating-point conversions.
    snprintf(line, sizeof(line), "FrameProfile frames=120 fps_x100=%u mean_us=%u p50_us=%u p95_us=%u max_us=%u input_us=%u scripts_us=%u render_us=%u poll_us=%u passes=%u previous_report_us=%u draw_us=%u present_us=%u render_phases=%u poll_max_us=%u slow_polls=%u over_50ms=%u over_67ms=%u",
        (unsigned)(12000000.0 / total), (unsigned)(total*1000/120),
        (unsigned)(sorted[60]*1000), (unsigned)(sorted[114]*1000), (unsigned)(sorted[119]*1000),
        (unsigned)(inputSum*1000/120), (unsigned)(scriptSum*1000/120), (unsigned)(renderSum*1000/120), (unsigned)(pollSum*1000/120), passes, previousReportUs,
        (unsigned)(drawSum*1000/120), (unsigned)(presentSum*1000/120), renderPhases,
        (unsigned)(pollMax*1000), slowPolls, over50, over67);
    Log::log(line);
#ifdef SE_XBOX_PROFILE_THREADS
    std::vector<std::pair<std::string, ThreadCost>> sortedThreads(threads.begin(), threads.end());
    std::sort(sortedThreads.begin(), sortedThreads.end(), [](const auto &a, const auto &b) { return a.second.ms > b.second.ms; });
    for (unsigned i = 0; i < std::min<size_t>(6, sortedThreads.size()); ++i) {
        const auto &cost = sortedThreads[i];
        snprintf(line, sizeof(line), "ThreadProfile name=%s frame_us=%u calls=%u", cost.first.c_str(), (unsigned)(cost.second.ms * 1000 / 120), cost.second.calls);
        Log::log(line);
    }
    std::vector<std::pair<std::string, ThreadCost>> nativeSorted(nativeCosts.begin(), nativeCosts.end());
    std::sort(nativeSorted.begin(), nativeSorted.end(), [](const auto &a, const auto &b) { return a.second.ms > b.second.ms; });
    for (unsigned i = 0; i < std::min<size_t>(8, nativeSorted.size()); ++i) {
        const auto &cost = nativeSorted[i];
        snprintf(line, sizeof(line), "NativeProfile opcode=%s frame_us=%u calls=%u", cost.first.c_str(), (unsigned)(cost.second.ms * 1000 / 120), cost.second.calls);
        Log::log(line);
    }
    nativeCosts.clear();
    threads.clear();
#endif
    count = passes = 0; inputSum = scriptSum = renderSum = pollSum = 0;
    drawSum = presentSum = pollMax = 0; renderPhases = slowPolls = 0;
    // Diagnostic disk/console output is absent in normal builds. Account for
    // it separately rather than attributing the report itself to gameplay.
    previousReportUs = static_cast<unsigned>(reporting.getTimeMsDouble() * 1000);
    interval.start();
}
}
#endif
