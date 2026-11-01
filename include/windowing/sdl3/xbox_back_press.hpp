#pragma once
#include <array>
#include <cstdint>

namespace XboxSDLInput {
class BackPresses {
    struct Pad {
        uint32_t id = 0;
        bool pressed = false;
    };
    std::array<Pad, 4> pads{};

  public:
    void connect(uint32_t id) {
        if (!id) return;
        for (const auto &pad : pads)
            if (pad.id == id) return;
        for (auto &pad : pads)
            if (!pad.id) {
                pad.id = id;
                return;
            }
    }
    void disconnect(uint32_t id) {
        for (auto &pad : pads)
            if (pad.id == id) pad = {};
    }
    void press(uint32_t id) {
        for (auto &pad : pads)
            if (id && pad.id == id) pad.pressed = true;
    }
    bool consume() {
        bool pressed = false;
        for (auto &pad : pads) {
            pressed |= pad.pressed;
            pad.pressed = false;
        }
        return pressed;
    }
    void clear() { pads = {}; }
};
} // namespace XboxSDLInput
