# Sokoban puzzle repairs

Latest status (October 31): the full prepared set now passes both the earlier
SDL run and a [current native-graphics controller run](#native-full-set-controller-run-october-31-2026)
from level one through thirteen and natural wrap, with 2,728 moves and 628 pushes
checked. The installed Xbox archive remains the level-ten-only repair; full-set
physical/controller and audio qualification are still open.

Gammastr20's [Sokoban](https://scratch.mit.edu/projects/24490009/) has passed
puzzles one through three on the Xbox. The downloaded tenth puzzle contains
a crate at zero-based `(12, 2)` with inaccessible cells immediately right and
below it. The player cannot stand on those cells to push left or up, and cannot
push right or down into them. This is an authored map problem, independent of
Xbox rendering or controller input.

Another crate at `(8, 4)` requires access to its left support cell `(7, 4)`.
That support cell is enclosed by inaccessible cells and the crate itself.

## Separate prepared copy

```sh
python3 scripts/prepare-sokoban.py ORIGINAL.sb2 PREPARED.sb2
python3 scripts/verify-sokoban-solution.py PREPARED.sb2 examples/sokoban-level10-solution.json
```

The default preparation accepts only the tested original archive and refuses an
existing output or replacement of its source. It opens three floor cells:

- `(12, 3)` and `(12, 4)` provide a downward escape for the corner crate.
- `(7, 5)` gives the player access to the other crate's left support cell.

Coordinates start at the upper-left corner. X increases right and Y increases
down. The repair retains the 15-by-8 dimensions, player start, all eleven
crates, all eleven goals, the other twelve puzzles, every script and all nine
asset files. Reverting these three digits restores the original project JSON
exactly. Repeated preparation produced byte-identical archives; wrong-source
and overwrite attempts were rejected.

Original SHA-256:
`6b2ea446a14651efe37bc6589172a05309371d1c8db1d9ce8a267848827e5013`.
Prepared SHA-256:
`efdbc0055c6c97f1c525e4e5dd5273066e88f043127fb1c81d5276196df97f64`.

## Independent solution check

A backward pull search generated the saved route. A separate forward replay
then checked ordinary walking and pushing, without pulling, against every
inaccessible cell and occupied destination. The route takes 698 moves and
171 pushes and fills all eleven goals. The checked-in read-only verifier
repeats that forward check directly from the prepared archive. On the original
archive, the same route fails at step three when Down tries to push the trapped
crate. A failed route alone would not establish impossibility; the original
corner geometry above establishes that crate cannot reach a goal.

Earlier candidate searches that exhausted their time/state limits are retained
as incomplete results. They are not proofs that those candidates are impossible.

## Runtime qualification

An isolated xemu test uses the normal diagnostics-off executable and a separate fixture with
an explicitly added delayed level-ten selection script. That script is absent
from the distributable prepared archive. This is a targeted puzzle test, not
a playthrough of the preceding nine puzzles.

Earlier failed debugger input harnesses are excluded from completion evidence.
The corrected input-poll bypass verified every player position and all 120 map
cells across 698 moves and 171 pushes, filling all eleven goals. The runtime
then advanced naturally to level eleven. After an earlier 78-move prefix,
the original R key restored the initial player position and every crate/map
cell; the cumulative move counter correctly remained 83, including five
preceding walks. No player positions, maps, scores or goals were written by
the debugger.

The backward-search route originally included thirteen unnecessary walks after
all goals were filled. The runtime correctly advanced during that tail, causing
the old assertion at step 699. The saved route now ends at first completion;
the independent verifier rejects trailing moves after completion. The original
assertion and all 698 preceding matched states remain in the evidence, alongside
the completed level-ten state and the level-eleven framebuffer capture.

## Physical Xbox qualification

The separate level-ten fixture passed on the 128MB Xbox using the normal
upstream-synchronized `e332255e` executable, with renderer/game/menu tracing
disabled. Only controller inputs were supplied. After twenty verified moves,
Black restored the original player position and every crate/map cell. A fresh
698-move route then matched every observed player position and all 120 cells,
filled all eleven goals, and advanced naturally to level eleven. The final
physical screen showed level 11 / moves 718 (20 before restart plus 698 after).
The full route took about 64 minutes. This is a targeted tenth-puzzle test,
not a playthrough of puzzles one through nine.

Start-hold pause and a short A confirmation returned to the populated browser.
After the controller dashboard reset, the prepared archive was installed as
`E:\ScratchEverywhere\Sokoban-Gammastr20.sb2`. Temporary upload, final archive
and original-backup readbacks all matched. The original is retained as
`sokoban-original-6b2ea446.fixture`; the existing controller profile is unchanged
(SHA-256 `7bf8c7b14210d9d1fc3ebeaf232f7265db7d0815e048f1de5b7e9d2d6d77dac3`).
The temporary level-ten project and profile were removed, restoring twenty
games plus XboxTest in the browser. The regular Games launcher remains the
preceding `2b8b5778` executable.

The installed prepared archive then passed ordinary browser selection,
puzzles one through three, Black restart and a short-confirmation Exit.
A fresh browser launch showed level one / moves zero; a crate push and Black
restart again matched the complete first-puzzle map and player position.
A repeated short-confirmation Exit returned to the populated browser.
Later puzzles, complete normal playthrough, and subjective audio remain open.

An eight-second music capture contained one full-scale stereo frame at index
zero, followed by normal levels (peak 0.06983); the raw file is retained.
A repeat eight-second capture had peak 0.04514 and no full-scale frames.
The initial capture-frame anomaly remains a shared audio-capture investigation,
not a claimed music or decoder failure. The earlier 120-second source-matched
loop check uses the same unchanged music asset.

Local preparation, solver, archive-comparison and runtime evidence is in ignored
`build-xbox/hardware/sokoban-*` and `build-xbox/xemu-sokoban-level10/`.

## Optional complete puzzle set — candidate

The default command and its `efdbc005…` archive remain unchanged. Add
`--all-puzzles` to prepare the additional authored-project repairs:

```sh
python3 scripts/prepare-sokoban.py --all-puzzles ORIGINAL.sb2 FULL.sb2
python3 scripts/verify-sokoban-solution.py FULL.sb2 examples/sokoban-all-puzzles-solutions.json
python3 tests/sokoban_all_puzzles_test.py ORIGINAL.sb2
```

This option still starts from the tested original `6b2ea446…` archive. It keeps
the puzzle-ten access repair and adds:

- **Completed-goal scan:** the authored loop increments its index before reading
  a tile. Starting at one skips the first cell and reads past the end. Starting
  at zero makes it visit cells one through N. Puzzles nine and twelve have a
  goal in that first cell: the previous loop counts nine of ten and three of
  four completed goals, respectively.
- **Puzzle twelve height:** its header declares nine rows of seven cells, while
  its data contains ten rows. Height ten draws every existing row. All seventy
  tiles, crates and goals are retained.
- **Puzzle thirteen start:** `(9, 7)` is an inaccessible tile. The player starts
  one cell up at `(9, 6)`, on existing floor. Its map, crates and goals are retained.

These are Scratch project adaptations, with no engine or Xbox-only code change.
The optional copy changes three puzzle records and one loop initializer; all
nine assets and every other project value are preserved. Reversing those four
edits restores the original parsed project. The candidate SHA-256 is
`8253ed9a8dc8106525d1121880549bfa24de969223f0a360e4cc331ec880d05b`.

The saved thirteen routes independently replay **2,728 moves / 628 pushes**.
The verifier checks complete, unique puzzle coverage, legal walking/pushing,
first completion and archive identity. Its existing single-puzzle command is
preserved. The regression check also interprets the actual finite goal-count
loop, verifies corrected counts on every solved map, checks asset/project
preservation and rejects overwrite and wrong-source attempts.

An ordinary level-one start in the private xemu guest completed **all thirteen
puzzles and the natural wrap to puzzle one**. A separate audit replayed all
**2,728 moves / 628 pushes**, comparing every recorded player position, map
cell, solved puzzle and natural transition with independent routes. This
includes puzzle nine and twelve recognition after filling their previously
skipped first-cell goals, and the corrected puzzle-thirteen start. A final
read-only check verified the live first-puzzle map and player with the
cumulative counter at 2,728; its original framebuffer shows Level 1 / Moves 2728
and independently matches all 25 tiles and the player.

Testing used the normal `ac3142d7…` Xbox executable from the runtime improvement
now merged in PR #33, with profiling off. GDB supplied keys before native
key-hat dispatch; project variables, maps, scores, RNG and positions were only
read. The same guest and verified prefix were retained across two bounded
debugger segments. Native input was restored before detaching. Debugger pacing
and private host audio output do not establish FPS or sound quality.

**An emulator visual issue remains open.** Pixel classification of the thirteen
initial framebuffers matched 793 of 796 cells and every player. Three samples
in the puzzle-ten image differed from its correct logical map. A separate
explicit delayed-puzzle-ten fixture on the same executable matched all 120
cells and the player in five captures, including a frozen repeat and later
native input polls. A second explicitly prepared pre-win-puzzle-nine fixture
used one ordinary Left move to advance naturally to ten; all six captured
maps/players matched (696 sampled cells). Both targeted probes use the same
executable and retain all assets. These clean results do not explain the earlier
mismatch or establish a visually clean full run. All original images are
preserved. The disposable guests and debuggers are closed.

### October 28 rendering follow-up

A fresh, unseeded repeat used the same candidate archive and normal executable.
The observer now waits for both level initialization and the authored drawing
flag to finish before settling and capturing. The first seven boards' sampled centers matched;
puzzle eight's initial image missed two floor cells (265 of 267 sampled cells
across eight boards matched). The repeat was stopped after **169 verified
moves**, at puzzle eight, to investigate this earlier reproduction. It did not
repeat the complete thirteen-puzzle run.

With input restored to neutral, a read-only debugger check matched the complete
logical map and player against the independent route. Initialization and drawing
were both complete. Two identical, settled framebuffer captures still disagreed
with four cells. A separate read-only dump of the pen render target contained
the same four wrong cells: three were transparent and one showed floor instead
of a goal. The defect therefore exists in the drawing surface before final
screen composition; the exact cause remains open.

An ordinary R restart produced a clean 72-cell board. A subsequent bounded
restart probe reproduced a missing floor tile on its second captured restart: 71 of 72
cells matched, with the logical map and player still correct. Extra tracing
changes timing, so a clean traced redraw does not establish a fix.

A fresh private guest then reproduced the problem with the same normal
executable and a separate fixture containing only one added script: select
puzzle eight after a one-second delay. All assets and the remaining project
were verified unchanged. Tile-center checks passed the first fourteen captured
restarts, then found two missing floor cells on capture fifteen. A stronger
comparison of all **174,936 board pixels**, against a visually reviewed clean
reference, also found smaller defects on captures six and fourteen. Center
samples alone therefore undercount the visual failures. The fixture SHA-256 is
`ef1678b2f5918608f37e6df23a6b8795c79d401f194bd254ae5bd394872c9650`.

A separate current-main experiment invalidated the GPU vertex buffer cache
before each geometry draw. The changed dependency source and compiled command
were verified; matching symbols supplied all debugger addresses. Its first
restart still had a correct logical map/player but 4,212 differing board pixels
and a missing floor sample. **That experiment was rejected and its source
change reverted.** It was neither merged nor installed on the Xbox. The short
reproduction makes further investigation possible without another multi-hour
playthrough; the actual rendering fix remains open.

A separate **unmodified current-main control** also reproduced partial tile
corruption on its third captured restart: all 72 tile centers matched, but
619 board pixels differed. This confirms that the defect is still relevant to
current main, and reinforces the need for complete-image comparison. The
control and experimental guests were closed after restoring native input;
one earlier failing guest is retained paused for further inspection.

These are private emulator findings, not physical controller, performance or
audio acceptance. Original images, logical states, direct pen-surface bytes,
compiled Xbox structure-layout offsets and input-restoration receipts are in
ignored `build-xbox/sokoban-visual-repeat-20261028/` in the primary checkout.
The short fixture and full-image comparisons are under
`build-xbox/sokoban-level8-restarts-20261028/`; the rejected experiment and
current-main control are under `build-xbox/sokoban-cache-candidate-20261028/`
and `build-xbox/sokoban-current-main-control-20261028/` respectively.
The physical Xbox's installed archive and executable were not changed.

**This candidate has not been installed or tested on the physical Xbox.** The
installed default prepared archive remains `efdbc005…`. A complete physical
playthrough, full-set visual acceptance and audio qualification remain open. Local source,
independent replay and completed runtime evidence are under ignored
`build-xbox/sokoban-full-20261027/` in the primary checkout; the separate visual
probe is under `build-xbox/sokoban-stamp-forensics-20261027/`.

### Texture-lifetime repair candidate

[Merged PR #42](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/42)
localizes the redraw defect to texture storage freed before GPU reads finish.
A standalone offline diagnostic loses a tile on draw four with unmodified main;
the normal fixed build passes 100 unchanged draws. The selected-level-eight
Sokoban fixture also passes 100 complete-image comparisons in xemu and twenty
physical controller restart commands with 21 clean settled board captures.
This is rendering evidence for the separate runtime fix, not physical testing
of this full-set archive. Native color/pen regression still reports 38 passes.

A fresh full-set replay of archive `8253ed9a...` ran from normal level
one on fixed XBE `78cb682a...`; every map/player transition and each initial
board's tile centers were checked. Its completed result is recorded below. The complete
image checks remain the stronger oracle for partial-tile corruption; initial
center samples alone do not establish pixel-perfect boards. All earlier owned
forensic guests have been closed. The installed canonical archive remains
`efdbc005...`; full-set hardware and audio gates remain open.

### Fixed-build natural transition to puzzle ten

The fresh `78cb682a...` replay completed puzzles one through nine naturally,
reaching ten at cumulative move 1,312. All 120 initial tile centers matched.
The settled initial image and diagnostic polls four/twelve/thirty also match
a separately captured clean board exactly across the complete padded board
rectangle: **0 differing pixels out of 105,910**. The first transition probe
still displays the completed level-nine screen; it is retained separately,
not treated as a settled level-ten failure or acceptance image. The full
thirteen-puzzle run now completes as recorded below; physical full-set testing is open.

A separate check of the [original official Scratch player](https://scratch.mit.edu/projects/24490009/)
produced two upward moves from a requested 400 ms key hold on level one
(the UI call took 458 ms). The source's `g_mT` repeat counter advances per
authored Tick call, not elapsed time. This reference check does not measure
normal Xbox repeat speed; multi-hour debugger replay wall time is not a game
pacing/FPS benchmark. No source or project timing was changed. Original browser
images/action receipts are under ignored `build-xbox/sokoban-reference-player-20261028/`;
the complete-board comparison is `level10-complete-board-audit.json` under
`build-xbox/sokoban-texture-fullset-20261028/` in the primary checkout.


## Texture reuse during redraws (October 28, 2026)

A separate runtime defect could leave partial or missing board stamps while
Sokoban's map and submitted geometry were correct. The [Xbox texture-retirement
fix](xbox-texture-retirement.md) waits for submitted GPU reads before freeing
costume storage. The normal candidate passed 100 exact-pixel level-eight
redraws in xemu and twenty controller restart commands with 21 clean settled
board captures on the physical 128MB Xbox, followed by a clean browser return.
Those selected fixtures alone do not establish a complete playthrough. The
full-set prepared-copy hardware gate remains open; the later emulator replay
is described below.


## Full-set emulator follow-up (October 29, 2026)

The separate `8253ed9a...` full-set candidate from
[PR 34](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/34) now
passes an ordinary level-one start through all thirteen puzzles and natural
wrap to level one on the normal texture-retirement build `78cb682a...`.
All 2,728 moves and 628 pushes were checked against independent expected
player/map states. All thirteen initial boards passed 796 cell-center samples
and visual review; the wrapped level-one playfield was pixel-identical across
197,574 pixels, excluding its updated move counter. Inputs were restored.
See the [rendering-fix validation](xbox-texture-retirement.md).

The physical Xbox still has the earlier `efdbc005...` level-ten-only repair.
This emulator result neither changes that installation nor proves controller
transport, audio, FPS, all-thirteen full-image pixel equality, or 64MB support.

## Native full-set controller run (October 31, 2026)

Normal runtime `c7c0a9d9…` completes the same `8253ed9a…` prepared archive in
one fresh xemu process, using native NV2A graphics/windowing and **SDL3 audio**.
The guest is configured for 128MB. Inputs use the emulated USB controller;
no game state or input vector is written.

- All thirteen puzzles complete naturally, including the repaired goal scans,
  and wrap to level one at **2,728 moves / 628 pushes**. Every player/map state
  matches the independent route.
- All 2,715 nonfinal moves pass settled tile-center checks. Thirteen initial /
  Black-restart pairs are identical across the complete image. Another 2,717
  comparisons find no unexpected RGB changes outside changed/player cells
  (with a four-pixel margin) and the monitor sidebar; this does not establish
  complete expected-frame equality.
- The wrapped playfield matches the first board across 755,136 pixels,
  excluding the updated move counter. Green Flag restores the exact initial
  screen; another Up push and Black restart work. A fresh browser relaunch
  repeats the initial image and push, followed by a second clean, stable return
  to the exact 21-game browser.

A 10.037-second APU music excerpt matches the unchanged authored song at
correlation 0.99487, without pitch/time fitting, clipping or zero 256-frame
blocks. This checks the SDL3 audio path, not native XboxAudio, HDMI/TV listening
or long-run continuity. Paused emulator observations are not FPS measurements.

Early scanout, a short counter-observation deadline and an unavailable debugger
field produced retained observer failures; later read-only observations verified
progress and correct images without changing runtime code. Private evidence is
under ignored `build-xbox/sokoban-native-fullset-20261031/`, summarized in
`final-review.json`. The owned guest is closed and its private base disk is
unchanged. The physical full-set installation/playthrough remains open; this
run adds no physical, expanded-graphics or retail-64MB acceptance.
