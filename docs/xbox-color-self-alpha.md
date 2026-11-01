# Xbox color sensing at fractional sprite edges

Xbox's `touching color?` reporter used a reduced alpha collision grid for the
subject sprite, while `color touching color?` used its actual source texels.
The grid could count contact beyond a fractional image edge. This matters for
small sprites and tight passages; it does not establish why any particular
Jumper attempt failed.

The Xbox path now checks the subject's source alpha through the same sampler
as masked color sensing. Its alpha-only mode skips RGB restoration and color
transformation. Sprite-to-sprite collision masks and other platforms' behavior
are unchanged. This is an **Xbox-specific runtime correction**, with no Scratch
project, physics-rule or controller-profile changes.

## Reproduction and checks — October 31, 2026

The [regression generator](../examples/make-color-sensing-test.py) retains the
previous 38 color/pen/culling cases and adds twenty fractional-edge checks.
An opaque white 16×16 SVG sits below a red backdrop row at stage Y=8. At subject
Y=-0.5 and -0.25, the row lies beyond the image: both reporters should return
false. Because every opaque subject pixel is white, the plain and white-masked
reporters must agree. Positions inside the edge provide positive controls.

| Run | Result |
| --- | --- |
| Frozen normal `eb3492c2…`, native NV2A | 56/58; two false positives in the plain reporter |
| Candidate `a66ca892…`, native NV2A/window | 58/58; zero errors |
| Same candidate, Xbox SDL/SDL3 window | 58/58; zero errors |
| Native diagnostic with expanded graphics limits explicitly enabled | 58/58; zero errors |
| Independent host color/brightness reference | 1,756 cases; maximum channel difference 1/255 |

The guests have 128 MB of emulated RAM, verified through QMP, and matching
symbols. The normal guest reports `OS::isExpanded=false`, selecting the
compatibility graphics limits. A separate fixture-only diagnostic sets that
capability flag to true before renderer initialization, exercising expanded
graphics limits; it is not normal expanded-kernel gameplay or physical testing. The fixture
is identical across the baseline and candidate at the project/asset level. Its
initial DVD-root path and renderer are selected by the diagnostic GDB harness;
no fixture variables or expected results are written by the debugger. Build
options match the normal frozen baseline; obsolete lwmem cache entries are not
current build options. Tracing and profiling are disabled.

The direct-load diagnostic harness is separate from normal browser gameplay.
Its attempted controller returns did not reach the browser and are excluded
from gameplay evidence; normal browser checks use a separate fresh boot.
A separate cold-browser guest loads all 21 archives and returns to the exact
21-game/42-button list with zero game sprites after each exit. The initial
Mario pause observations were too short. A later cold single-tap test confirms
Back delivery during the intro and eventual pause after another 120 neutral
video frames, without another press. The earlier attempts remain recorded;
they do not establish lost taps. See the [timing follow-up](xbox-native-back-taps.md#pause-before-the-next-game-frame--october-31-2026).

A normal controller maze run also passes wall blocking, the complete visible
win, 7,200 further neutral video frames, Green Flag replay and renewed movement,
then held-A Exit. The replay image exactly matches the fresh loaded image.
No gameplay state is written by the debugger in these normal-game checks.

Physical Xbox, per-game performance and full-game acceptance remain open.
Jumper's final-stage victory is still unverified.

Private evidence: ignored `build-xbox/color-self-alpha-20261031/`, including
`baseline-result.json`, both candidate renderer results, screenshots, matching
build/symbol receipts and retained failed harness attempts. The original Jumper
run remains paused separately; this diagnostic does not alter its game state.
