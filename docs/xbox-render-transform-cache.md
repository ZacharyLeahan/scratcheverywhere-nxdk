# Xbox sprite transform cache — candidate

The Xbox transform calculation invalidated rotation after computing size, then
invalidated size after computing rotation. Even an unchanged sprite therefore
repeated both calculations on its next render. A probe of the pre-change
function counted 1,000 angle conversions across 1,000 unchanged calls.

This candidate separates size, rotation and position invalidation. It tracks
rotation style, image dimensions and rotation center, bitmap resolution/quality,
SVG selection, viewport/project dimensions, render mode and global scale.
Same-index image reloads and SVG crop changes therefore still update position.
The position cache retains the source double coordinates instead of rounding
its keys to floats. An explicit validity flag also handles a first position
that happens to equal the old sentinel value.

This is **Xbox-specific**, although its guarded code lives in the shared
renderer and `RenderInfo` files. The other-platform preprocessed transform
function is unchanged. Game scripts, update rate, physics and the transform
formulas are unchanged. The compiled Xbox `RenderInfo` grows from 44 to 120
bytes: 76 additional bytes per sprite for the explicit cache keys.

## Validation

```sh
python3 tests/xbox_render_transform_cache_test.py
```

The test compiles the actual function and Xbox `RenderInfo` under ASan/UBSan.
It compares cached results with forced recomputation across 30,000 mixed
changes, including rotation styles, same-index image geometry changes,
viewport/quality changes, fractional coordinates and copied clones. Known
position/flip cases check the formula independently. Unchanged and scrolling
calls reuse the angle calculation, while rotation/style changes and explicit
invalidation still refresh it. The non-Xbox path also compiles.

An optional `--reference /path/to/previous-renderer.cpp` comparison checks the
same cases against the pre-change function. This passed with commit
`89e186b9`; its old sentinel collision is explicitly excluded because the
candidate intentionally fixes that first-render case. Separately preprocessing
both versions without `__XBOX__` produces identical function tokens.

Normal and enhanced-profile NXDK Release builds pass. The normal executable
contains no frame-profile format string. The enhanced profile can separate
CPU drawing/queueing from SDL presentation and count long event polls; see the
[Appel pacing notes](xbox-appel.md#next-pacing-diagnostic).

A private xemu guest passed the prepared Appel menus, walking, jump ascent,
first-apple collection, ground landing, solid-wall blocking, ledge clearance,
second-apple collection and ledge landing. The normal candidate was used with
exact installed v3 project JSON and nonaudio assets; 45 audio files were omitted
only for the guest BIOS RAM limit. GDB supplied input keys while native input
and key-hat functions executed. Game variables, positions and scores were only
read, and native input ownership was restored before detaching. Checks waited
for bounded gameplay events; debugger input-poll counts are not FPS evidence.
Original framebuffer images confirm the player and terrain rendering.

## Physical comparison — October 28

The 128 MB Xbox ran both profiling executables at forced 480p with the same
prepared Appel v3 archive (`117188ba…`) and controller profile. Separate test
folders and full FTP readbacks preserve executable identity; the primary Games
launcher remains `b75e9beb…`. Each build reached Level 1, walked to the first
wall with one apple, and ran two identical 28-second left/right loops. Bounded
video captures finished before each timed action and confirmed the expected
wall/one-apple endpoints afterwards.

Every complete 120-frame window enclosed by an action is included; partial
boundary windows are excluded. Diagnostic packet sequences have no gaps in
the timed intervals. FPS derives from device frame periods. Each route has
equal sampled frame counts for both builds: 1,320 on Player Two and 1,440 on
Player Three.

| Route | Baseline FPS | Cache FPS | Baseline frames over 50 ms | Cache frames over 50 ms |
| --- | ---: | ---: | ---: | ---: |
| Player Two | 27.79 | 28.46 | 18.64% | 12.05% |
| Player Three repeat | 28.04 | 27.55 | 15.63% | 18.82% |

The initial apparent gain did not repeat. Both routes still have median
window-p95 frame times near 53 ms and individual frames around 168–186 ms.
**No repeatable hardware speedup is established; keep this experiment draft.**
The known-good normal `ac3142d7…` build is restored for play. These short loops
do not establish whole-level performance, subjective TV smoothness, Mac-like
pacing or retail 64 MB support.

Controller delivery limits the comparison. Every sampled active adapter
reported USB configured and its completion counters advanced, but Player Two
had redundant UDP send errors and late reported directions. Player Three had
substantially fewer send errors (24 across baseline trials, zero across cache
trials), although control acknowledgements still varied. Its reversed result
does not by itself prove a cache regression; it prevents promoting the earlier
small gain as a reliable improvement.

The optional `draw_us`, `present_us` and `render_phases` fields are zero in both
builds. `cmake/platforms/xbox.cmake` applies the profiling definition to runtime
sources but omits `source/renderers/xbox/renderer_xbox.cpp`. These zeros are not
CPU/GPU measurements. Fix that wiring before using the phase breakdown to
locate the remaining pauses; overall frame-period measurements remain valid.

Original logs, controller receipts, image hashes, build manifests and analysis
are under ignored `build-xbox/appel-transform-cache-20261027/`, including
`comparison-report-20261028.json`, both `comparison-results*-20261028.json`
files and `hardware-comparison-install-20261028.json`.
