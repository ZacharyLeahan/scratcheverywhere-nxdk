#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>

namespace CollisionGrid {
// World-space centers and signed spacing of axis-aligned alpha pixels.
// A pixel covers half a cell on either side of its center.
struct View {
    int width, height;
    double x, y, stepX, stepY;
};

struct Range {
    int first = 0, last = -1;
    bool empty() const { return first > last; }
    int count() const { return empty() ? 0 : last - first + 1; }
};

inline Range intersectingCells(double low, double high, double origin, double step, int count) {
    if (count <= 0 || !std::isfinite(step) || step == 0 || !(low < high)) return {};
    double a = (low - origin) / step, b = (high - origin) / step;
    if (a > b) std::swap(a, b);
    if (!std::isfinite(a) || !std::isfinite(b) || b <= -0.5 || a >= count - 0.5) return {};
    // Strict overlap: two cells that only share an edge do not intersect.
    return {static_cast<int>(std::floor(std::max(-0.5, a) - 0.5)) + 1,
            static_cast<int>(std::ceil(std::min(count - 0.5, b) + 0.5)) - 1};
}

inline void bounds(double origin, double step, int count, double &low, double &high) {
    low = origin - step * 0.5;
    high = origin + step * (count - 0.5);
    if (low > high) std::swap(low, high);
}

template <typename ReadA, typename ReadB>
bool scan(const View &a, ReadA readA, const View &b, ReadB readB, Range xs, Range ys) {
    const double halfX = std::abs(a.stepX) * 0.5, halfY = std::abs(a.stepY) * 0.5;
    for (int y = ys.first; y <= ys.last; ++y) {
        const double cy = a.y + y * a.stepY;
        const auto by = intersectingCells(cy - halfY, cy + halfY, b.y, b.stepY, b.height);
        if (by.empty()) continue;
        for (int x = xs.first; x <= xs.last; ++x) {
            if (!readA(x, y)) continue;
            const double cx = a.x + x * a.stepX;
            const auto bx = intersectingCells(cx - halfX, cx + halfX, b.x, b.stepX, b.width);
            for (int j = by.first; j <= by.last; ++j)
                for (int i = bx.first; i <= bx.last; ++i)
                    if (readB(i, j)) return true;
        }
    }
    return false;
}

template <typename ReadA, typename ReadB>
bool intersects(const View &a, ReadA readA, const View &b, ReadB readB) {
    if (a.width <= 0 || a.height <= 0 || b.width <= 0 || b.height <= 0) return false;
    double ax0, ax1, ay0, ay1, bx0, bx1, by0, by1;
    bounds(a.x, a.stepX, a.width, ax0, ax1);
    bounds(a.y, a.stepY, a.height, ay0, ay1);
    bounds(b.x, b.stepX, b.width, bx0, bx1);
    bounds(b.y, b.stepY, b.height, by0, by1);
    const auto ax = intersectingCells(bx0, bx1, a.x, a.stepX, a.width);
    const auto ay = intersectingCells(by0, by1, a.y, a.stepY, a.height);
    const auto bx = intersectingCells(ax0, ax1, b.x, b.stepX, b.width);
    const auto by = intersectingCells(ay0, ay1, b.y, b.stepY, b.height);
    if (ax.empty() || ay.empty() || bx.empty() || by.empty()) return false;
    // Work in the smaller clipped mask, rather than sampling its world-space circle.
    if (int64_t(ax.count()) * ay.count() <= int64_t(bx.count()) * by.count())
        return scan(a, readA, b, readB, ax, ay);
    return scan(b, readB, a, readA, bx, by);
}
} // namespace CollisionGrid
