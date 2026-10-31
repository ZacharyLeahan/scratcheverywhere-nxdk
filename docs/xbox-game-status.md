# Xbox game status — October 31, 2026

[Main](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/tree/main) is the
place to find current code. This page summarizes what we have actually tested;
the [hardware checklist](xbox-game-qualification.md) and linked game notes keep
the detailed evidence. **The 21-game hardware qualification is incomplete.**

The physical console has **128 MB RAM**. A separate normal build of main now
passes native NV2A browser selection and gameplay checks for Catch Apples,
Appel and PacMan, with three clean returns to the game list. Catch also passes
ending/replay/steering. Native startup reliability and remaining gameplay, audio
and handoff checks stay open; see the
[physical backend follow-up](xbox-native-hardware-followup.md). The installed
primary dashboard launcher still uses the older SDL Xbox renderer. Merging code
does not replace it, game archives or saved renderer preferences. Retail 64 MB
support is unverified.

## Gameplay coverage

All 21 normal games pass native-emulator browser selection → actual archive
load → pause → Exit, with zero game sprites and the exact 21-game list after
each return. Some launches stop at a title screen. **That common check does not
prove full gameplay, smoothness or audio.** “Launch cycle” below means this
limited check; larger emulator objectives are listed separately.

After the October 30 upstream sync, normal main build `eb3492c2…` repeats all
21 native-emulator launch/pause/Exit cycles in one snapshot guest, with the exact
21-game/42-button browser and zero game sprites after every return. This is the
[same limited check](xbox-upstream-nv2a-integration.md#current-main-launch-regression--october-30),
not a new physical or complete-gameplay pass.

The October 31 [color-boundary correction](xbox-color-self-alpha.md) passes
58-case native/SDL regressions, 21 eventual browser returns and a full maze/replay.
The initial native Mario pause observation was too short: a later single-tap test
confirms delivery during the intro, followed by delayed pause. See the
[Back timing investigation](xbox-native-back-taps.md#pause-before-the-next-game-frame--october-31-2026).
Extended gameplay results below retain the builds identified in their notes;
this common cycle does not repeat every full-game objective.

| Game / detailed notes | Real Xbox result | Extended emulator result | Open gameplay / quality checks |
| --- | --- | --- | --- |
| [Spider Adventure](xbox-spider-adventure.md) | Level 6; Score 7,516; death, replay and relaunch | All 10 levels / 100 spiders; Score 14,110; victory replay | Full hardware victory; longer audio/listening |
| [Hopper Heros](xbox-hopper.md) | Movement/jump; Score 8; loss/replay and relaunch | Launch cycle | Sustained progression; early short Start sometimes missed; audio |
| [Ultra Bird](xbox-ultra-bird.md) | Six pipes / Score 6; loss/replay; repeated launch/exit | Launch cycle | Controller delivery; no authored sound |
| [Catch Apples](xbox-catch-apples.md) | Score 22 / timer expiry; replay; special-apple scores repaired; current main native Score 14 ending, replay, both D-pad directions and clean Exit | Native timer ending, replay, steering and return | Further repeated native handoff checks; historical Exit → 2048; audio |
| [Maze Starter](xbox-maze-replay.md) | Complete maze, wall blocking, repeated clean replay; current requested-native full win/wall check, then HDMI/controller loss | Current native full win, two-minute winning scene, exact-image replay, movement and clean return | Current native replay/Exit after HDMI loss; retrieved log has no explicit crash; shared browser/controller handoff; no authored sound |
| [Snake](xbox-snake.md) | Score 225 tail-collision ending; blade shrink, clock slowdown/restoration; replay | Launch cycle | Latest second Exit interrupted by adapter disconnects; active audio |
| [Appel](xbox-appel.md) | Normal play to 21/35 apples, checkpoints/death; earlier diagnostic Level 1 win; TV music reported clean; current native menu/terrain/walk/jump to two apples and clean Exit | Normal v4 Level 1 win: 17 apples / 1:07.8; complete authored replay; Try Again | Movement smoothness; normal-v4 physical win/replay; later levels; audio continuity |
| [Tetris](xbox-tetris.md) | Ten-line/level-up runs; later four-line objective at 1,200; top-out/replay | Independent ordinary four-line run; cap ending checked with seeded diagnostic | Subjective audio; initial capture anomaly; cap is not a natural full playthrough |
| [Frogger](xbox-frogger.md) | Six pads in one round; all seven positions across rounds; replay/relaunch | All seven in one native round; visible Win, replay and ordinary loss | Hardware seven-pad win/replay; audio. Emulator ending has internal alive=0 despite authored Win |
| [Breakout](xbox-breakout-controller.md) | Final prepared copy clears board at 1,940; replay and fresh-launch/exit checks | Native board clear at 1,920 / three lives; replay | KVM paddle delivery; faint scaled boundary line; no authored playback |
| [PacMan](xbox-pacman.md) | Turns/walls/scoring; power pellet +100 and blue ghosts; loss/replay; current native turn/Score 40 and clean Exit | All 92 collectibles plus one ghost: 1,380; visible Win; Win/loss replay | Hardware full board/ghost; original final High Score gap; optional prepared repair passes ending probes and natural loss/replay, not installed |
| [Space Invaders](xbox-space-invaders.md) | Score 1,230; shield/life loss, replay/relaunch | Native full wave: 55 → 0 → fresh 55, Score 990 / three lives; wave-two recovery | Hardware full wave; complete audio/listening |
| Asteroids ([checklist](xbox-game-qualification.md)) | Thrust/turn/fire; Score 9,200; Game Over/replay/relaunch | Launch cycle | Further level progression; audio |
| [Sokoban](xbox-sokoban.md) | Puzzles 1–3; repaired puzzle 10 complete; restart/relaunch | Optional full-set copy: all 13 puzzles, 2,728 moves / 628 pushes, natural wrap; SDL renderer | Full-set copy not installed on hardware; physical full set and native gameplay/audio |
| [2048](xbox-2048.md) | Natural 2048 win / Score 20,264; continue, loss/replay and repeated exits | Launch cycle | KVM missed/duplicate input and held-confirmation handoff; no authored playback |
| [Retro Racing](xbox-retro-racing.md) | 108 MPH, braking/steering/off-road slowdown; pause/replay | Current native full lap 02:02.00, Y pause, deliberate drift/smoke, off-road slowdown, replay and two clean returns | Hardware full lap/drift/traffic visuals; audio. Traffic collision is not authored |
| [Hill Climb Racing](xbox-hill-climb.md) | Jeep 1,000; motorcycle 420; fuel pickup, airtime/crash, vehicle swap/replay | Launch cycle | Extended terrain; precise brake/air control; audio |
| [Mario](xbox-mario.md) | Four opening pipes; Goomba/pit death and automatic recovery; replay/relaunch | Current native full level without deaths; flagpole/fireworks/fade, natural replay, Green Flag and two clean returns; short intro Back taps | Hardware full level/native Back behavior; subjective audio and performance |
| Doodle Jump ([checklist](xbox-game-qualification.md)) | At least 1,044 m; both edge wraps; fall/replay/relaunch | Launch cycle | Monsters, longer play and audio |
| [Jumper](xbox-jumper.md) | Levels 1–4; lava death, restart/replay; readiness-guard exits | Current native `c7c0a9d9…` clears all 20 courses on both installed and timer-fixed archives; visible win/stopped timer, fixed post-win Y+Black clock restart, Green Flag replay, renewed jumping/Black restart and clean browser return | Timer-fixed archive needs Xbox installation and later-level/victory/replay tests; historical second-Exit handoff; audio |
| Connect Four ([checklist](xbox-game-qualification.md)) | Both players; horizontal/vertical/diagonal wins; full-column rejection/replay | Launch cycle | One unexplained initial mouse-mode launch; no authored playback |

## Performance and audio

The measured Appel comparison on the real 128 MB Xbox at 480p ran about
**27–28 FPS** in short wall-walking loops. Baseline/cache pairs were
27.79/28.46 FPS, then 28.04/27.55 FPS on the repeated controller route.
The apparent gain reversed; the [transform-cache experiment, PR 35](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/35)
remains unmerged. Window-p95 frame times were near 53 ms, with occasional 168–186 ms delays
in those samples. This is not a whole-level benchmark or native-NV2A measurement.
There is no measured per-game FPS result for the other twenty games on this page.

A separate current-main [matched backend sample](xbox-appel.md#matched-nativelegacy-hardware-timing--october-30-2026)
measures **29.50 FPS native / 29.00 FPS legacy**, each over 720 rendered frames
in the same opening-ground walking plan, with Xbox audio/music and the same
project/executable. Median window p95 is about 51 ms for both. This single pair
does not establish a repeatable speed gain or full-level smoothness; the primary
launcher and saved settings are not promoted from it.

Native-emulator frame budgets and debugger replay durations are not FPS results.
Source-matched audio samples establish selected cues only. The Appel TV report
is useful subjective evidence; KVM recordings have lost samples, so their
crackles/dropouts alone do not prove an Xbox playback defect. Longer listening
and continuity checks remain open where the table says audio.

## Shared issues and how to add games

- KVM controller adapters have intermittently gone offline or delivered
  late/duplicate input. The latest session uses the documented direct S3 HTTP
  route: the main KVM firmware has wireless-controller routing disabled.
  XBMC navigation, three games and reset work on that route. The console log
  enumerates three controllers; physical port assignment and single-controller
  isolation are not established, and this is not a four-player retest.
- Native startup has shown purple in short captures. A longer capture also
  reaches the browser on unchanged main, so neither a permanent freeze nor a
  renderer fix is established by those early images. Repeated, adequately
  observed starts remain open; see the [follow-up](xbox-native-hardware-followup.md).
- Return to launcher, short Start replay of stopped projects, and
  **Start + Back + both triggers held two seconds** are implemented. The reset
  requests Xbox reboot while the game loop responds. A three-second test hold
  recovered to XBMC; an earlier hold exactly at the two-second threshold did not.
  It cannot guarantee recovery from a hard hang or disconnected adapter. Native
  Back taps are retained across slow polls. The runtime checks Back before the
  next script/render batch, but work already in progress can still delay it.
  The [SDL USB-read repair](xbox-sdl-back-taps.md) also retains short Back taps
  across slow frames and passes 21 emulator menu cycles plus virtual USB
  removal/reconnect. Physical confirmation remains open.
- The original PacMan can miss its final High Score update. An optional
  [prepared-project repair](xbox-pacman.md#optional-final-high-score-repair--october-30-2026)
  now passes isolated ending probes and normal loss/replay in xemu; the physical
  archive is unchanged. Numeric monitor decimal tails have a separate
  [formatter fix](xbox-monitor-number-formatting.md); pre-existing JSON
  number-loading precision is still unresolved.
- There is a local game browser, but no in-app Scratch search/download/add flow.
  Projects and any control sidecars must be downloaded externally and FTP'd to
  `E:\ScratchEverywhere\` while XBMC provides FTP, then opened from the game list.
  That transfer/setup step is what makes adding games cumbersome. Game archives
  are not bundled with this repository.

## Changes available in main

- [PR 55](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/55),
  [SDL Back-tap repair](xbox-sdl-back-taps.md): continuous Xbox USB reads and
  one-shot console-menu requests; live gameplay/confirmation remains unchanged.
  SDL menu/replay/reset and virtual hotplug checks pass; hardware is pending.

- [PR 54](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/54): Xbox
  pause before another script/render batch; 21 native menu cycles, gated Green
  Flag replay, SDL longer-hold menu controls and reset checks. Physical testing
  remains open; the separate SDL tap gap is addressed by PR 55 above.

- [Xbox color-boundary correction](xbox-color-self-alpha.md): `touching color?`
  checks the subject's rendered alpha rather than an expanded collision-grid
  edge. Native/SDL diagnostics and normal-game checks pass; hardware is pending.

- [PR 43](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/43): upstream
  Xbox integration, native graphics/input fixes and Appel controller-menu updates;
  [limited native hardware follow-up](xbox-native-hardware-followup.md) now exists;
  **full physical native-backend acceptance remains open**.
- [PR 41](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/41): shared
  numeric monitor formatter repair, verified with Xbox compiler flags and paired
  emulator probes; physical confirmation remains open.
- [PR 34](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/34): optional
  Sokoban `--all-puzzles` preparation and independently verified routes. Default
  preparation stays identical to the installed level-ten repair; hardware
  full-set deployment is a separate task.

Xbox graphics/input/audio changes are platform-specific. Monitor formatting and
some upstream runtime/SVG changes affect the shared core; controller menus and
Sokoban repairs are explicit prepared-project changes. The linked PRs and game
notes identify each scope. Mike's separate recap stays on its feature branch.
