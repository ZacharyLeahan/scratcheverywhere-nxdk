#pragma once
#include <array>
#include <cstddef>
#include <cstdint>

// USB callbacks and readers synchronize outside this platform-independent state.
namespace XboxNativeInput {
inline constexpr int deadzoneX = 10000;
inline constexpr int deadzoneY = 18000;
inline constexpr int buttonThreshold = 30;
using Report = std::array<uint8_t, 20>;
inline int16_t axis(const Report &report, size_t offset) {
    const unsigned value = unsigned(report[offset]) | (unsigned(report[offset + 1]) << 8);
    return static_cast<int16_t>(value >= 0x8000 ? int(value) - 0x10000 : int(value));
}
inline uint32_t activity(const Report &report) {
    uint32_t bits = report[2];
    for (size_t i = 4; i < 12; ++i) if (report[i] > buttonThreshold) bits |= 1u << (i + 4);
    for (size_t i = 0; i < 4; ++i) {
        const int value = axis(report, 12 + i * 2);
        const int threshold = (i & 1) ? deadzoneY : deadzoneX;
        if (value > threshold) bits |= 1u << (16 + i * 2);
        if (value < -threshold) bits |= 1u << (17 + i * 2);
    }
    return bits;
}
inline bool resetChord(const Report &report) {
    return (report[2] & 0x30) == 0x30 && report[10] > 191 && report[11] > 191;
}
class Controllers {
    struct Pad {
        Report report{};
        uint32_t activity = 0, resetSince = 0;
        bool connected = false, valid = false, resetting = false, backPressed = false;
    };
    std::array<Pad, 4> pads{};
    int active = -1;
  public:
    void connect(size_t index) {
        if (index >= pads.size()) return;
        pads[index] = Pad{};
        pads[index].connected = true;
        if (active == int(index)) active = -1;
    }
    void invalidate(size_t index) {
        if (index >= pads.size()) return;
        pads[index].valid = pads[index].resetting = false;
        pads[index].activity = 0;
        pads[index].backPressed = false;
        pads[index].report = Report{};
        if (active == int(index)) active = -1;
    }
    void disconnect(size_t index) {
        invalidate(index);
        if (index < pads.size()) pads[index].connected = false;
    }
    bool submit(size_t index, const uint8_t *bytes, size_t length, uint32_t now) {
        if (index >= pads.size() || !pads[index].connected) return false;
        if (!bytes || length < Report{}.size() || bytes[0] != 0 || bytes[1] != Report{}.size()) {
            invalidate(index);
            return false;
        }
        auto &pad = pads[index];
        // Back is reserved for the console menu. Retain its rising edge when a
        // slow game frame spans an entire tap; gameplay stays a live snapshot.
        if ((bytes[2] & 0x20) && !(pad.report[2] & 0x20)) pad.backPressed = true;
        for (size_t i = 0; i < pad.report.size(); ++i) pad.report[i] = bytes[i];
        const uint32_t next = activity(pad.report);
        // Held or neutral reports from another pad must not steal control back.
        if ((next & ~pad.activity) || activeIndex() < 0) active = int(index);
        pad.activity = next;
        pad.valid = true;
        if (!resetChord(pad.report)) pad.resetting = false;
        else if (!pad.resetting) { pad.resetSince = now; pad.resetting = true; }
        return true;
    }
    int activeIndex() const {
        if (active >= 0 && pads[active].connected && pads[active].valid) return active;
        for (size_t i = 0; i < pads.size(); ++i)
            if (pads[i].connected && pads[i].valid) return int(i);
        return -1;
    }
    bool copyActive(Report &report) const {
        const int index = activeIndex();
        report = index < 0 ? Report{} : pads[index].report;
        return index >= 0;
    }
    bool consumeBackPress() {
        bool pressed = false;
        for (auto &pad : pads) {
            pressed |= pad.connected && pad.valid && pad.backPressed;
            pad.backPressed = false;
        }
        return pressed;
    }
    bool resetRequested(uint32_t now) const {
        for (const auto &pad : pads)
            if (pad.connected && pad.valid && pad.resetting && uint32_t(now - pad.resetSince) >= 2000) return true;
        return false;
    }
};
}
