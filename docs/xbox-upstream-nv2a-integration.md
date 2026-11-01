# Upstream Xbox integration

The latest synchronization is the [November 1 release 1.3 integration](xbox-upstream-1.3.md).
The original integration and its separately identified tests follow.

This work integrates upstream through
[`ec2400eb`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/ec2400ebca42b7060795ff2c3d426c63a0c89687),
including [PR 816](https://github.com/ScratchEverywhere/ScratchEverywhere/pull/816):
the native NV2A renderer/window, dedicated Xbox audio, and runtime/memory improvements.
The subsequent Halloween menu assets are included too. Source integration in
the fork is separate from deployment; native hardware qualification is still pending.
See the [current game status and known issues](xbox-game-status.md).

## Fork behavior retained

- Back opens the console menu; games keep their Start bindings. A short Start
  press replays a stopped project.
- Return to the game list, release-before-confirmation, pointer help, and the
  Exit / System menu remain available.
- The native input backend accepts all four controllers. A new button/direction
  can take control; another pad's neutral, drift, or repeated held reports do not
  steal it back. Disconnects, read errors and malformed reports release its state.
- Start + Back + both triggers for two seconds requests the configured Xbox
  reboot. The menu/game loop must still be responsive to process this shortcut.
- Authored Xbox project lists remain intact, including large terrain maps.
  Existing costume bookkeeping and frame/thread profiling remain enabled by
  their respective options.
- The legacy SDL renderer retains the reviewed GPU texture-retirement fix from
  [PR 42](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/42).
  Native NV2A has its own retirement mechanism and needs its own visual tests.

Native report snapshots use NXDK's DPC-level synchronization, following its SDL
joystick driver. Reports must contain all 20 bytes before any axes are read.
The new controller regression test covers handoff, drift, hotplug, short reports,
axis signs, reset cancellation, separate-pad chords, and tick-count wraparound.

## Validation and limits

The normal and debug-symbol NXDK builds succeed at 480p with expanded RAM enabled.
Affected host checks pass for list indices/VM stacks, typed arithmetic, Value
conversion/cache reuse, hats/broadcasts, costume cache/lifetime, Scratch 2 SVG
bounds/text, bitmap layers, color transforms, audio resampling, Xbox clocks,
variable tracing, native controllers, and frame/profile build definitions.

A private emulator test uses
[xemu-macos v0.16.4](https://github.com/MichaelJSr/xemu-macos/releases/tag/v0.16.4),
with the release archive checked against GitHub's asset SHA-256. GDB confirms
NV2A renderer/window IDs 3/0; all four emulated USB controller ports move the
launcher selection. Catch Apples launches, Back opens the console menu, and
Return to game list completes without launching another project. These are
emulator checks, not physical Xbox acceptance or an all-games pass. A separately
verified Catch run steers both ways with the left stick, reaches Score 12 /
Timer 0, restarts on short Start at Score 0 / Timer 29, and returns to the browser.
The earlier incorrectly selected Breakout run is retained separately and does
not supply this Catch evidence. Audio remains an open check.

A controlled Catch Game Over comparison isolates rough SVG lettering to nearest
magnification. Switching only the native backdrop sampler to linear smooths the
text; restoring it reproduces the original frame exactly (zero differing pixels),
with identical uploaded texture bytes. Native SVG drawing now uses linear
sampling across normal, tiled, mosaic, deformed and nine-slice paths. Bitmap
textures retain their selected filtering; explicit pixelate effects use nearest.

The compiled sampler candidate `c94ba467...` reaches the original Catch archive's
natural ending at Score 11 / Timer 0. Its 175,500-pixel lettering crop matches the
controlled linear result exactly; the backdrop texture hash is unchanged. A
read-only trace observes 32 recognized SVG binds, all linear. Short Start replays
at Score 0 / Timer 29, the left stick steers both ways, and Back / Return to game
list redraws the browser. These Catch checks exercise ordinary SVG drawing; broader artwork and sampling
quality still need review beyond the solid-color checks below.
Both comparison guests report the standard-memory policy despite the emulator's
128MB configuration: the backdrop raster is 334×249 in a 16-bit texture. This
neither qualifies a retail 64MB Xbox nor proves title-visible expanded RAM.

Native brightness now adds a signed RGB offset and clamps before transparency,
in one draw pass. It retains the shared 96-step hue cache. Pen compositing uses
its stored premultiplied color without applying transparency a second time.

The compiled brightness candidate `ab2481f2...` passes **107/107** independent
samples in the unchanged [color/pen fixture](../examples/make-color-effects-test.py)
(maximum channel error 7, tolerance 9), with PASSES=5 / ERRORS=0 / CYCLES=40.
The preceding builds passed 98/107, with identical colors before and after the
SVG fix, establishing that these errors predated that change.

The new [brightness draw-path fixture](../examples/make-nv2a-brightness-test.py)
also passes **60/60** solid-center checks with standard memory policy and again
with an explicit expanded-renderer-policy override (maximum errors 9 and 2).
A bounded read-only trace confirms mosaic wrap/grid, pixelate and deformed paths;
the expanded-policy run additionally executes tiled stage/bitmap draws, including
brightness -50, +50, -100 and +100. The standard-policy guest downsizes the large
bitmap, so it does not establish tiled coverage. The override changes only the
disposable guest's renderer policy; it does not validate RAM detection or physical
128MB hardware. Back / Return to game list redraws the menu/browser without a
brightness tint afterwards. Physical rendering, pen/sensing and audio acceptance
remain open.

The native backend now implements the fork's original-color restoration and
pen-query hooks. Color sensing decodes the authored asset when CPU pixels have
been freed, preserving the existing texture dimensions and GPU resources. Pen
queries synchronize queued strokes/stamps and cache only the queried rectangle;
drawing, clearing and cleanup invalidate that cache.

The compiled sensing candidate `2dd1b385...` improves the unchanged
[38-case regression](../examples/make-color-sensing-test.py) from **19 passes /
19 errors** to **38 passes / 0 errors**. The same scripts/assets also pass with
only the ordinary `hq=true` project comment added; GDB verifies a 640×480 pen
canvas at scale 4/3. A frame-paced Start press reaches the actual Green Flag
handler and the following result is again 38/0; both pen modes return cleanly to
the browser. The latest binary retains **107/107** color-effect samples and
PASSES=5 / ERRORS=0 / CYCLES=40. These are emulator checks; physical pen/collision
acceptance and game-specific behavior still need testing.

An ordinary native USB-controller [Breakout run](xbox-breakout-controller.md)
now clears the final prepared archive at Score 1920 with three lives. Three
captures contain no remaining brick colors, and the score stays fixed across
960 additional video frames while the ball crosses the empty field. Natural
Game Over, menu Green Flag replay to observed Score 0 / three lives / restored
bricks, renewed steering and a separately verified fresh-launch browser exit
also pass. These use the frozen sensing candidate and a read-only observer;
physical full-board and normal-browser selection of that final archive remain
open.

The final post-theme XBE `f79fcd52...` also reaches the native launcher twice,
once after the controller reboot. A 90-video-frame reset hold does not reboot;
release cancels it, and a fresh full hold reaches `XReboot` after 122 frames.
The app starts again and the native launcher redraws correctly. This emulator's
inserted DVD launches the app again; it does not establish physical dashboard
recovery or recovery from a blocked game loop. Inputs were neutral afterwards.

The installed stock Mac xemu cannot provide Vulkan and falls back to OpenGL.
Its earlier startup used the legacy Xbox renderer (IDs 4/1), so it does not count
as native NV2A evidence. The private Vulkan test explicitly selects NV2A,
equivalent to the app's `--nv2a` option. Existing saved renderer preferences are
respected; installing a build alone does not change a saved `Xbox` preference.

The copied emulator disk has not been audited against the current physical
installation. Catch's initial D-pad probe leaves its basket stationary, consistent
with the older missing-sidecar case documented in [Catch Apples](xbox-catch-apples.md).
Do not count that probe as steering acceptance or assume its archives/profiles
match the final Xbox copies.

Original evidence is ignored under `build-xbox/upstream-nv2a-20261029/` in the
primary checkout. No physical XBE, game archive, controller firmware, or KVM
settings were changed by this integration. The separate frozen Sokoban replay
continues against its original binary and full-set prepared archive.

## Appel SVG growth and complete-project checks

Appel's animated menu exposed a separate Xbox image-cache defect: AUDIO ON and
EDITOR were first rasterized at 20x5 pixels (scale 0.133), then stretched after
the animation reached full size. Xbox frees parsed SVG trees after rasterizing,
so the existing resize path silently skipped growth. Images now retain their
source location and reload the original SVG when a larger raster is requested.
Parsed trees are still released; temporary decode failures retain the previous
pixels/geometry, and failed texture uploads remain retryable.

The complete controller-menu v3 archive (`117188ba...`) retains all 460 original
assets, including 45 audio files. Native candidate `0f04b4ec...` displays readable
title and level-picker labels; the corresponding cached buttons are 216x57,
with no retained SVG document. Actual emulated USB inputs enter Level One, move
both ways, jump, collect four apples and activate the first checkpoint. A spike
collision shows the authored death particles and respawns at that checkpoint;
read-only observation confirms PLAY, four apples and a nonzero spawn index.
Green Flag from the console menu returns to the readable title; a subsequent
Back / Return to game list redraws the populated browser.

A ten-second APU capture has no clipped samples or fully silent 256-sample
blocks. Aligning it with the original music asset gives 0.999990 correlation.
This checks emulated output, not physical TV sound, all game sounds or performance.
The NXDK build and existing costume-cache, cache-lifetime, Scratch 2 text and
real SVG bounds/pixels checks pass. Thin terrain seams, a full Level One clear,
physical smoothness and the remaining game/hardware gates are still open.

## Filtered texture edges

Appel's thin internal terrain lines expose zero-filled padding in native
swizzled textures. A 62x62 SVG rasterizes to 82x82 opaque pixels inside a 128x128
GPU allocation. Linear filtering can sample the transparent black padding;
GPU clamp applies to the allocation, beyond the image's smaller UV extent.
Native uploads now duplicate one texel at the right and bottom edges, including
the corner, to cover the bilinear filter footprint. The ordinary and allocation-
fallback upload paths share this operation. Image dimensions, UVs, original
pixels and authored terrain are unchanged.

Candidate `807d1928...` removes the observed title-terrain lines and remains
clean in the captured walking/jumping scenes. Read-only GPU dumps confirm that
both checked terrain textures retain byte-identical interiors, with the new
border matching the last original row/column. A static 74,094-pixel title crop
has 216 dark line pixels before and zero afterwards; these are separate guest
runs, not a same-frame reversal experiment. The unchanged color/pen fixture
still passes 107/107 samples (maximum channel error 7), with PASSES=5 / ERRORS=0 /
CYCLES=40. The upload helper passes 27 shape/format combinations with ASan/UBSan,
including row pitches, one-dimensional images, repeated updates and guards.
Hardware artwork and performance qualification remain pending.

## Appel extended native playthrough — October 29

The unchanged `807d1928...` executable and complete controller-menu archive
`117188ba...` now finish Level One with **21/35 apples** and the authored victory
menu. Read-only inspection confirms WIN, LEVEL #=2 (the author's Level One),
X=5809.36, Y=557.01 and SPAWN IDX=1249. Ordinary emulated USB controller actions
cross both lifts, the spike tower, roof enemies and lower spikes; checkpoint
three activates and a later death respawns there with all sixteen apples retained.
The later route drops to the ledge beneath the spiked block, crosses underneath,
jumps back onto its clear right side, then crosses the isolated platforms and
final gap. No game-state writes, altered collision rules or input-poll bypass
were used; read-only position observations helped time takeoffs.

Controller mouse mode (White + D-pad, then White + RT) activates the authored
**Try Again** button. The fresh round shows 0/35 and 0:00.0; Right/A restore
walking and jumping, and read-only inspection confirms PLAY with no checkpoint.
Back / Return to game list redraws the populated browser. That v3 copy requires mouse mode
for the victory menu; its title and level-picker already support D-pad/A.

The 3.883-second emulated APU capture across completion contains no clipped
samples or zero 256-sample blocks. The full original completion cue matches
at correlation 0.943; this bounded comparison does not establish every cue or
physical TV sound. A fresh browser launch also reaches Appel's title and exits,
but that private HDD fixture lacks the controller-menu variables and is excluded
from prepared-copy relaunch acceptance. The later fixture refresh below closes
that emulator-only relaunch gap. Physical Level One/replay, pacing, audio and
the other hardware qualification gates remain open.

## Appel victory controller menus

The project preparer now adds victory focus for Continue, Try Again, Level Select
and Replay. Up/down cycle the choices; left/right cross the bottom row. A runs
the selected button's original `show menu` procedure on release. Moving focus
while holding A cancels the old selection. White reserves pointer control,
because native input sends arrow events during White + D-pad mouse movement.
This is an Appel preparation change; no C++ runtime changes are needed.

Compared with v3, the normal v4 archive `6ccd3f17...` preserves all 460 asset
files, including 45 sound files, every stage gameplay script and all other targets. Focus/hover
routing changes only the in-game menu and adds one stage focus variable; its
authored actions remain intact. Host checks cover preservation, navigation,
release/recheck guards, single-clone activation and pointer isolation.

On native `807d1928...`, a separate full-project **diagnostic fixture** opens the
victory menu from PLAY. It verifies all four focus choices, wrap and bottom-row
navigation, pointer fallback, cancellation, A hold/release, real Try Again reset
and renewed jumping, Level Select, Continue to the next level, Replay activation
and launcher return. It seeds WIN for this bounded menu test and does not prove
a natural v4 victory or complete recorded-run playback. The earlier 21-apple
natural victory belongs to the unchanged v3 archive. Physical v4 deployment
and controller/menu acceptance remain pending.

## Refreshed 21-game emulator fixtures — October 29

A new private HDD copy now contains all 21 normal games, with current prepared
copies and 20 controller sidecars; Ultra Bird uses the default controls. All 41
files pass full FTP readback. Appel uses the normal v4 `6ccd3f17...` candidate,
not the WIN-seeded fixture. Sokoban retains installed `efdbc005...`; the separate
full-set candidate is not substituted. Backups use `.fixture` extensions.

On unchanged native `807d1928...`, Appel passes two controller-only browser →
title → level picker → Level One → browser cycles, including Right/A movement,
jumping and the first apple. Read-only inspection confirms the prepared menu
variables. Spider Adventure is selectable as game 21, reaches natural Game Over,
accepts Y replay and Right/A jumping, and returns to the populated browser.
These short checks do not establish Spider's ten-level victory.

Read-only browser inspection matches all 21 manifest names and 42 game/settings
buttons, with renderer/window 3/0. A separate cold-started snapshot guest repeats
that exact list check and leaves the saved HDD byte-identical. Evidence is in
`build-xbox/emulator-game-refresh-20261029/review.json` and its linked receipts
and captures. Both guests exit cleanly with neutral controls. This refresh changes
only the private emulator fixtures. The later full v4 run below closes the
emulator victory/replay gap; physical installation, pacing/audio and every open
hardware gate remain pending.

## Spider Adventure full native playthrough — October 29

The unchanged original project now completes all ten levels through normal
emulated USB play on `807d1928...`: all 100 spiders, Score 14,110, Best combo 8,
one life and authored YOU WIN. Life-loss recovery, Y victory replay to zero
with retained high score, renewed movement/jumping, a fresh browser launch and
repeated exits pass; cleanup leaves zero game sprites and all 21 browser entries.
Full-source announcement, hurt, loss-mixture and win-mixture audio comparisons
exceed 0.999 correlation in their bounded captures. See the
[scoped gameplay/audio evidence](xbox-spider-adventure.md#native-emulator-full-run--october-29-2026).
This closes the earlier short emulator run's ten-level gap, while physical
victory, listening, pacing and all hardware qualification gates remain open.

## Appel v4 natural victory and full replay — October 29

The normal v4 archive `6ccd3f17...`, with all 460 assets and 45 sounds present,
now finishes Level One on unchanged native `807d1928...` in the private 128 MB
Vulkan xemu guest. The ordinary controller run reaches **17/35 apples, 1:07.8**
and the authored WIN menu. It crosses both lifts, the spike tower, hidden
passage, roof enemies and final platforms, with deaths/checkpoint recovery
preserving collected apples. Read-only position checks guide takeoffs; no
WIN seeding, gameplay-state writes, input-poll bypass or collision edits are used.

D-pad navigation selects Replay and A/release activates it. With all external
controls then neutral, the game's own complete recording reproduces the run,
including its deaths and recoveries, and reaches WIN with the same apples,
time and final X=5807.3594/Y=557.01. The 308-value BLACK BOX recording remains
identical before and after playback. Its canonical JSON SHA-256 is
`513f995a4a9898468a13b63e9ba3eb1adbc93ca0985a38221e73aac92557e06b`.
This is a naturally recorded full replay, separate from the earlier seeded menu
fixture and v3 victory.

Try Again, selected with D-pad/A after replay, restores zero apples and no
checkpoint; walking/jumping resume. Exit redraws the populated browser.
Read-only inspection confirms zero game sprites, all 21 projects/42 buttons,
and renderer/window 3/0. A fresh browser launch again reaches the title,
controller level picker and moving/jumping Level One player; the second Exit
repeats the zero-sprite/21-project/42-button check. The snapshot guest exits
cleanly and the saved shared HDD stays byte-identical. No source or project
changes were needed in this run.

Ignored evidence is in `build-xbox/appel-v4-native-fullrun-20261029/review.json`,
`natural-level-one-finish-full-recording.json`, `authored-replay-review.json`,
the linked original screenshots/QMP receipts, and `browser-live-list.json`.
Physical v4 deployment/victory/replay, TV movement acceptance, pacing, audio,
lwmem and 64 MB support remain open. Emulator frame budgets are not FPS results.

## Frogger native full round — October 29

The unchanged normal prepared Frogger archive `6c747a92...` reaches all seven
pads in one unseeded round through actual emulated USB controls on native
`807d1928...`. The authored You Win display appears; Green Flag clears the
pads/score, all four directions work, and a later traffic death shows only
Game Over. Fresh browser launch and two exits pass, each leaving zero game
sprites and all 21 projects/42 buttons. The guest closes cleanly with the saved
HDD unchanged. No engine or project changes were needed.

The final point leaves internal `alive=0`, which initially stops the helper's
strict check; the actual victory and replay still pass. The authored ending
suppresses loss UI/sound at score seven. See the [full-round evidence and
caveat](xbox-frogger.md#native-emulator-full-round--october-29-2026).
Physical seven-pad victory/replay, audio, pacing and 64 MB gates remain open.

## All 21 native browser launch/exit checks — October 29

One private snapshot guest on unchanged native `807d1928...` selects and loads
all 21 normal manifest entries through emulated USB D-pad/A input. Read-only
checks match each selected entry to the actual loaded archive path. Each game
subsequently pauses and exits; all 21 returns leave zero game sprites, the exact
21-file browser list and 42 game/settings buttons, with renderer/window 3/0.
No wrong-game launch, guest reboot or save-state restore occurs in this cycle.
Some loaded captures are title screens; this is launcher coverage, not complete
gameplay qualification.

Mario's first short Back press during the Will_Wam intro does **not** open pause.
After another 600 neutral video frames, its controls scene appears; the same
short Back press then opens pause and Exit succeeds. The missed early press is
retained in the original results, not dismissed as a crash or counted as
uniform first-attempt pause success. The Back-tap fix below addresses the lost
input; frame-pacing acceptance remains separate. The helper's earlier loading-flag
and empty-string observation errors are also retained; neither required an
engine or project change.

Evidence is in `build-xbox/native-browser-all21-20261029/review.json`, the per-entry
selected/loaded/pause/returned receipts and screenshots, and the QMP logs.
The guest exits cleanly; all 41 normal source files and the saved shared HDD
remain byte-identical. Physical controls/handoff, full gameplay, audio, pacing
and retail 64 MB acceptance remain open.

## Native Back-tap retention — October 29

Read-only USB/poll tracing localizes Mario's startup miss: a complete Back tap
arrives between game input polls and is replaced by neutral before the next
poll. Candidate `4ef49719...` retains only reserved Back edges until the existing
atomic input snapshot consumes them. Gameplay/confirmation state and reset
hold timing remain live and unchanged. ASan/UBSan controller checks and the
NXDK debug-symbol build pass. Actual USB-path comparisons accept the tap after
release, repeated menu toggles and held Exit/fresh-game checks pass, and the
reset chord reaches `XReboot` and fresh application startup. A slow render can
still delay pause; physical recovery and performance are not established.
See [the reproduction, delayed third result and validation scope](xbox-native-back-taps.md).

## Space Invaders native full wave — October 29

The original `09e3816b...` project clears all 55 invaders on native `4ef49719...`
through ordinary emulated USB play, with every remaining count down to zero
observed and a fresh 55 appearing at Score 990/all three lives. Wave two
continues to 1,370 with normal life-loss recovery. Green Flag, renewed controls,
a fresh browser launch and two held Exits pass; cleanup leaves zero sprites
and all 21 games/42 buttons. Selected whole-source audio matches come from an
uninterrupted 20.037-second unclipped APU capture; other cues and continuity
are not accepted. No runtime or game changes were needed in this batch.
See [the full-wave proof, failed host strategies and exact scope](xbox-space-invaders.md#native-emulator-full-wave--october-29-2026).
Physical full-wave/audio, pacing and 64 MB gates remain open.

## PacMan native full board — October 29

Original `283feafd…` on native `4ef49719…` collects all 92 dots/bonuses and eats
one frightened ghost for **Score 1,380**, with visible You Won. Short Start from
Win and ordinary Game Over, renewed controls, fresh actual-archive browser launch
and two held Exits pass; both cleanups leave zero sprites and the exact 21-game /
42-button list. The saved HDD and all manifest sources remain unchanged. No
runtime or game changes were needed. High Score lags at **1,370** and remains an
open issue; settled-Win silence adds no active-play audio acceptance.
See [the same-round evidence, host corrections and exact limits](xbox-pacman.md#native-emulator-full-board--october-29-2026).
Physical full-board/ghost, pacing and 64 MB gates remain open.

Hardware follow-up: verify the native backend and the intended saved renderer choice
on the Xbox, repeat launcher/game/replay/exit and reset tests, check audio and
texture/pen behavior, and continue every open gate in the
[21-game qualification matrix](xbox-game-qualification.md).

## Current main launch regression — October 30

Following the upstream sync in PR 46, the normal dual-backend main executable
`eb3492c2b7149a14200d02486a5d12b95cf886ebdb26655c255ac5f738a24535`
passes all 21 normal browser → actual archive → pause → Exit cycles with native
renderer/window 3/0 in one 128 MB snapshot xemu guest. Every return has zero game
sprites, an empty project path, the exact 21-game list and 42 browser buttons.
Loaded screenshots were reviewed; some show title screens or automatic endings.
This is loading/cleanup coverage, not full gameplay, audio, FPS or 64 MB acceptance.
Mario is allowed to advance past its intro before pause; early-intro input is
not newly qualified.

All 41 manifest archive/profile source files and the shared base HDD remain
byte-identical. The XBE has no renderer/input/game tracing or frame/thread
profiling. GDB selects the native backend at initialization; game state and RNG
are not changed. The guest closes after acknowledged quit.

The existing primary ISO was stale because its build cache had disc packaging
disabled. That first boot is excluded. A fresh disc was built from the frozen
current XBE, and the complete embedded `default.xbe` was read back and matched
before these checks. See the [build note](xbox-fork-build.md#checking-the-disc-image-used-for-testing).

The separately tested [optional PacMan ending repair](xbox-pacman.md#optional-final-high-score-repair--october-30-2026)
does not alter the original PacMan used in this 21-game batch. Its six diagnostic
ending probes and three normal full-project loads are recorded separately.

The IP-KVM observation script reports no physical Xbox HDMI signal during this
batch; dashboard FTP is unavailable. No hardware input, upload or acceptance is
claimed. The all-21-game physical goal remains incomplete. Private evidence:
`build-xbox/native-qualification-20261030/normal-all21-review.json`,
`all21-loaded-contact-sheet.jpg`, `current-disc-receipt.json` and
`final-review.json`.
