"""Compare the production cell-overlap helper with an independent rectangle oracle."""
from pathlib import Path
import random
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = r'''
#include "collision_grid.hpp"
#include <iostream>
#include <vector>
int main() {
    CollisionGrid::View a,b;
    while (std::cin >> a.width >> a.height >> a.x >> a.y >> a.stepX >> a.stepY
                    >> b.width >> b.height >> b.x >> b.y >> b.stepX >> b.stepY) {
        std::vector<int> aa(a.width*a.height),bb(b.width*b.height);
        for (auto &v:aa) std::cin >> v;
        for (auto &v:bb) std::cin >> v;
        auto ra=[&](int x,int y){return aa.at(y*a.width+x);};
        auto rb=[&](int x,int y){return bb.at(y*b.width+x);};
        std::cout << CollisionGrid::intersects(a,ra,b,rb) << ' '
                  << CollisionGrid::intersects(b,rb,a,ra) << '\n';
    }
}
'''


def oracle(a, aa, b, bb):
    def cells(view, pixels):
        w, h, x, y, dx, dy = view
        for j in range(h):
            for i in range(w):
                if pixels[j*w+i]:
                    cx, cy = x+i*dx, y+j*dy
                    yield cx-abs(dx)/2, cx+abs(dx)/2, cy-abs(dy)/2, cy+abs(dy)/2
    ac, bc = list(cells(a, aa)), list(cells(b, bb))
    return any(max(x0, u0) < min(x1, u1) and max(y0, v0) < min(y1, v1)
               for x0, x1, y0, y1 in ac for u0, u1, v0, v1 in bc)


cases = []
# Narrow overlap, an exact shared edge, separation, a transparent hole and a flip.
for x in [0.999, 1, 1.001]:
    cases.append(((1, 1, 0, 0, 1, -1), [1], (1, 1, x, 0, 1, -1), [1]))
cases.append(((3, 1, 0, 0, 1, -1), [1, 0, 1], (1, 1, 1, 0, 1, -1), [1]))
cases.append(((3, 1, 0, 0, -1, -1), [0, 0, 1], (1, 1, -2, 0, 1, -1), [1]))
# Geometric reproduction of the measured Xbox hitbox/hazard query. Only the
# overlapping rectangular cells are needed; no game artwork or archive is used.
pixel = 1/.20000001788139343
fire = (10, 29, 93.43062591552734+(pixel*.5-23.842119170654943)*.15,
        -143.55934143066406-(pixel*.5-53.50000090977564)*.15, pixel*.15, -pixel*.15)
pixel = 1/1.3333333730697632
hazard = (71, 102, 59.62499999999992+pixel*.5, -85.49829598350001-pixel*.5, pixel, -pixel)
alpha = [int(y >= 95 and x >= 23) for y in range(102) for x in range(71)]
cases.append((fire, [1]*290, hazard, alpha))
cases.append(((fire[0], fire[1], fire[2]-150, *fire[3:]), [1]*290, hazard, alpha))
rng = random.Random(571560558)
for _ in range(1500):
    views, masks = [], []
    for _ in range(2):
        w, h = rng.randrange(1, 9), rng.randrange(1, 9)
        views.append((w, h, rng.uniform(-8, 8), rng.uniform(-8, 8),
                      rng.choice([-1, 1])*rng.uniform(.1, 4),
                      rng.choice([-1, 1])*rng.uniform(.1, 4)))
        masks.append([int(rng.random() < .35) for _ in range(w*h)])
    cases.append((views[0], masks[0], views[1], masks[1]))
expected = [oracle(*case) for case in cases]
assert expected[5] and not expected[6]
with tempfile.TemporaryDirectory(prefix='collision-grid-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.cpp').write_text(source)
    subprocess.run(['c++', '-std=c++17', '-O2', '-fsanitize=address,undefined',
                    '-I', str(root/'include/runtime'), str(tmp/'test.cpp'),
                    '-o', str(tmp/'test')], check=True)
    data = ''.join(' '.join(map(str, [*a, *b, *aa, *bb]))+'\n' for a, aa, b, bb in cases)
    result = subprocess.run([str(tmp/'test')], input=data, text=True, capture_output=True, check=True)
    actual = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    assert len(actual) == len(cases)
    for i, (got, want) in enumerate(zip(actual, expected)):
        assert got == (int(want), int(want)), (i, cases[i], got, want)
print(f'PASS: {len(cases)} independent overlap cases, both argument orders, ASan/UBSan')
