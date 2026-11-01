# Xbox texture retirement

Rapid costume changes could leave missing or partial pen stamps. Sokoban's
logical map and submitted geometry were correct even when its board was not.
SDL flushes queued drawing before destroying a texture, but the nxdk renderer
freed the texture's contiguous memory while submitted GPU commands could still
read it. The allocator could reuse that memory for the next costume.

The Xbox SDL patch now waits for `pb_busy()` to clear before freeing texture
storage, using the same completion check as the driver's present/readback paths.
This is an Xbox driver change; project scripts and shared Scratch execution
are unchanged. It can wait for unrelated pending GPU work too. Performance
across costume-heavy games still needs checking; no FPS improvement is claimed.

The Xbox SDL recipe also includes the local patch hash in its source-cache
path. Catalog otherwise reuses a repository/ref checkout after a patch edit,
which can silently leave the compiled driver unchanged. Patch edits now also
trigger CMake reconfiguration. A fresh normal build was inspected to verify
that it compiled the guarded free, without private tracing.

## Small reproduction

Generate the standalone diagnostic using Python 3's standard library:

```sh
python3 examples/make-xbox-texture-lifetime-test.py /tmp/texture-retirement.sb2
```

Load it like any other project. Expect 48 colored, black-bordered tiles in an
8-by-6 board. Press the Scratch R or A key to redraw; DRAWS increments each time.
On Xbox, map a controller button to `r` in the project's controls sidecar. The
board must remain unchanged. The generator refuses an existing output file
and produces byte-identical archives on repeated runs. It is a diagnostic,
not one of the twenty-one qualification games.

## Validation on October 28, 2026

| Check | Unmodified control | Fixed normal build |
| --- | --- | --- |
| Standalone diagnostic in 128MB xemu | Redraw 4 lost a tile; 3,306 board pixels differed | 100 draws; all 116,624 compared board pixels unchanged; 48 tile centers correct |
| Delayed level-eight Sokoban fixture in xemu | Repeated redraws reproduced partial/missing stamps | 100 captured redraws; all 174,936 compared board pixels unchanged |
| Existing native color/pen regression | Previously established 38 passes | 38 passes, zero errors |

The debugger supplied ordinary R inputs only and restored its borrowed input
vector afterwards. It did not write project maps, positions, scores, or state.
These deliberately selected fixtures do not establish a full Sokoban playthrough.
A metadata-only lifetime control observed 207 frees with pending GPU work and
193 same-frame reallocations after such frees. The paired diagnostic fix
waited in 1,245 busy-at-entry release cases and passed 100 Sokoban redraws.
`pb_busy()` describes GPU work generally, not which exact texture it uses.

The production candidate XBE is SHA-256
`78cb682a2546e6411086bcdcb28ad6764d91525c28199f7ad58598759274ccc8`.
A separate physical test app was installed with full temporary/final FTP
readbacks. The primary Games launcher remains `b75e9beb...`.
The 128MB Xbox launched the candidate through its normal browser and displayed
the explicit level-eight fixture. Twenty Black/R restart commands and all
21 settled board captures showed no corruption: none of 232,518 compared board
pixels differed by more than 35 in any RGB channel from the initial JPEG.
That tolerance accommodates capture noise; the xemu checks above are exact.
Pause and Return to game list also returned to the populated browser.
The standalone diagnostic then retained an unchanged board across another
21 captures (155,520 board pixels each), but its HUD advanced from DRAWS 1
to 20 after twenty commands. Capture 10 repeated the previous counter value.
The original visual-only oracle passed; manual review of every HUD crop keeps
the controller-delivery gate open. A missed input versus delayed capture has
not been isolated. This is targeted rendering evidence, not full game, audio,
controller-delivery, or 64MB acceptance.

Appel also passed a physical normal-build smoke check: title and level picker,
level-one terrain, two rightward jump sequences with scrolling and collection
from zero to two apples, then a clean Return to game list. This is limited
gameplay/cleanup evidence; it does not establish full-level completion or FPS.
The retrieved normal log confirms project cleanup, browser activation and the
controller dashboard-reset chord. The two added diagnostic archives and their
profiles were hash-checked, backed up locally and removed after testing. Full
readbacks reconfirmed the primary `b75e9beb...` launcher, prior `ac3142d7...`
normal app and canonical `efdbc005...` Sokoban archive were unchanged. The
separate candidate remains installed; the console was returned to XBMC.

Raw matching binaries, source/build receipts, native images and controller/video
records are retained locally under ignored `build-xbox/sokoban-texture-lifetime-20261028`,
`build-xbox/texture-lifetime-fixture-20261028`,
`build-xbox/texture-retirement-color-regression-20261028` and
`build-xbox/hardware/texture-retirement-20261028`.

A further physical Snake run on the normal candidate rendered the board/tail,
collected fruit after Green Flag replay and later showed Score 125. Its planned
self-collision did not reach the tail, and controller connectivity subsequently
became unavailable across all four adapters. These are limited compatibility
observations; see the [input-delivery evidence](xbox-kvm-input-delivery.md).


## Full thirteen-puzzle replay (October 29, 2026)

The same normal `78cb682a...` build completed the separate full-set prepared
candidate `8253ed9a...` from an ordinary level-one start: 2,728 moves and
628 pushes, all thirteen puzzle completions, and the natural wrap back to
level one. No level selector or project-state writes were used. The debugger
supplied ordinary direction keys before native hat dispatch and restored its
borrowed input vector afterwards.

An independent audit rechecked every recorded player position and map cell
against the saved routes and counted all 628 pushes from actual crate-cell
changes. All 796 initial-board cell-center samples matched, and all thirteen
initial images were visually reviewed. The wrapped level-one playfield matched
its initial image exactly across 197,574 pixels, excluding the HUD. The earlier
whole-board level-ten reference comparison also remained exact. This is not a
claim of thirteen full-image pixel comparisons.

This full-set archive is the candidate from
[PR 34](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/34), not the
older level-ten-only repair installed on the Xbox. The result establishes the
normal SDL rendering fix's emulator compatibility across the complete set.
It does not close physical full-set/controller, audio, FPS, 64MB, or native NV2A
qualification. The roughly 2.55-hour run includes debugger overhead and is not
an ordinary-play performance measurement. Original images, complete move
history, restored-input check and `completion-audit.json` are retained under
ignored `build-xbox/sokoban-texture-fullset-20261028/`.
