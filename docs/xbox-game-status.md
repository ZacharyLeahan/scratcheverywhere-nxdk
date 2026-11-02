# Xbox game status — November 2, 2026

[Main](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/tree/main) is the
place to find current code. This page summarizes what we have actually tested;
the [hardware checklist](xbox-game-qualification.md) and linked game notes keep
the detailed evidence. **Thirty games are installed; full hardware qualification
is incomplete.** The original 21 and the nine additions below retain separate
test results; installation is not a pass count.

The physical console has **128 MB RAM**. A separate normal build of main now
passes native NV2A browser selection and gameplay checks for Catch Apples,
Appel and PacMan, with three clean returns to the game list. Catch also passes
ending/replay/steering. Current build `c7c0a9d9…` also passes a native Maze win,
post-win replay, fresh launch and two clean returns on hardware. The installed
full-set Sokoban copy also completes native puzzles 1–11 with every board checked;
the round is deliberately paused after six moves in twelve.
Native startup reliability and remaining gameplay, audio and handoff checks
stay open; see the
[physical backend follow-up](xbox-native-hardware-followup.md). Retail 64 MB
support is unverified.

## Current dashboard installation

The regular `F:/Games/ScratchEverywhere/default.xbe` now uses the ordinary
`092ca5ff…` build, whose runtime matches merged main `5ef65aaf`. It includes
upstream 1.3 and the fork's merged scheduler, RGBA upload and source-alpha
collision fixes. Profiling, input/state traces and UDP logging are disabled.
This installation uses the Xbox renderer with SDL3 window/audio; it does not
qualify the native window/audio path.

The prior `b75e9beb…` executable is preserved as
`default-before-main-5ef65aaf.fixture`. Staged upload, final executable and
backup passed full FTP readback; settings and all 30 project archives were
preserved. One regular-path start reached the populated browser. Beach
Volleyball, Bouncy Heroes and Mushroom Valley then passed selected launches,
gameplay, replay and clean browser returns. Repeated startup, the other games on
this installation and the quality checks below remain open.

The same ordinary executable previously cleared Fireboy Level 1 with all seven
gems and both exits, started its earned Level 2, and passed Appel opening
movement/terrain and Ninja course 1 → 2 with death/respawn. Those checks used a
separate test path before this promotion. See the
[collision evidence and measured cost](xbox-alpha-collision.md).

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
| [Maze Starter](xbox-maze-replay.md) | Complete maze and wall blocking; current native `c7c0a9d9…` full win, post-win Green Flag, renewed movement, fresh browser launch, two clean returns and dashboard reset | Current native full win, two-minute winning scene, exact-image replay, movement and clean return | Repeated-start reliability and shared controller/browser handoffs; no authored sound |
| [Snake](xbox-snake.md) | Score 225 tail-collision ending; blade shrink, clock slowdown/restoration; replay | Launch cycle | Latest second Exit interrupted by adapter disconnects; active audio |
| [Appel](xbox-appel.md) | Normal play to 21/35 apples, checkpoints/death; earlier diagnostic Level 1 win; TV music reported clean; current native menu/terrain/walk/jump to two apples and clean Exit | Normal v4 Level 1 win: 17 apples / 1:07.8; complete authored replay; Try Again | Movement smoothness; normal-v4 physical win/replay; later levels; audio continuity |
| [Tetris](xbox-tetris.md) | Ten-line/level-up runs; later four-line objective at 1,200; top-out/replay | Independent ordinary four-line run; cap ending checked with seeded diagnostic | Subjective audio; initial capture anomaly; cap is not a natural full playthrough |
| [Frogger](xbox-frogger.md) | Six pads in one round; all seven positions across rounds; replay/relaunch | All seven in one native round; visible Win, replay and ordinary loss | Hardware seven-pad win/replay; audio. Emulator ending has internal alive=0 despite authored Win |
| [Breakout](xbox-breakout-controller.md) | Final prepared copy clears board at 1,940; replay and fresh-launch/exit checks | Native board clear at 1,920 / three lives; replay | KVM paddle delivery; faint scaled boundary line; no authored playback |
| [PacMan](xbox-pacman.md) | Turns/walls/scoring; power pellet +100 and blue ghosts; loss/replay; current native turn/Score 40 and clean Exit | All 92 collectibles plus one ghost: 1,380; visible Win; Win/loss replay | Hardware full board/ghost; original final High Score gap; optional prepared repair passes ending probes and natural loss/replay, not installed |
| [Space Invaders](xbox-space-invaders.md) | Score 1,230; shield/life loss, replay/relaunch | Native full wave: 55 → 0 → fresh 55, Score 990 / three lives; wave-two recovery | Hardware full wave; complete audio/listening |
| Asteroids ([checklist](xbox-game-qualification.md)) | Thrust/turn/fire; Score 9,200; Game Over/replay/relaunch | Launch cycle | Further level progression; audio |
| [Sokoban](xbox-sokoban.md) | Puzzles 1–3; repaired puzzle 10 complete; restart/relaunch; full-set archive now installed and current native build completes puzzles 1–11, 2,188 route moves / 487 pushes; deliberate checkpoint in twelve; twelve Black restarts/every board checked | SDL and current native graphics: all 13 puzzles, 2,728 moves / 628 pushes, natural wrap; native Green Flag/Black restart, fresh launch and two clean returns; source-matched 10s SDL3 APU music | Physical full-set puzzles 12–13, wrap/replay/Exit, audio/listening and FPS |
| [2048](xbox-2048.md) | Natural 2048 win / Score 20,264; continue, loss/replay and repeated exits | Launch cycle | KVM missed/duplicate input and held-confirmation handoff; no authored playback |
| [Retro Racing](xbox-retro-racing.md) | 108 MPH, braking/steering/off-road slowdown; pause/replay | Current native full lap 02:02.00, Y pause, deliberate drift/smoke, off-road slowdown, replay and two clean returns | Hardware full lap/drift/traffic visuals; audio. Traffic collision is not authored |
| [Hill Climb Racing](xbox-hill-climb.md) | Jeep 1,000; motorcycle 420; fuel pickup, airtime/crash, vehicle swap/replay | Launch cycle | Extended terrain; precise brake/air control; audio |
| [Mario](xbox-mario.md) | Four opening pipes; Goomba/pit death and automatic recovery; replay/relaunch | Current native full level without deaths; flagpole/fireworks/fade, natural replay, Green Flag and two clean returns; short intro Back taps | Hardware full level/native Back behavior; subjective audio and performance |
| Doodle Jump ([checklist](xbox-game-qualification.md)) | At least 1,044 m; both edge wraps; fall/replay/relaunch | Launch cycle | Monsters, longer play and audio |
| [Jumper](xbox-jumper.md) | Levels 1–4; lava death, restart/replay; readiness-guard exits | Current native `c7c0a9d9…` clears all 20 courses on both installed and timer-fixed archives; visible win/stopped timer, fixed post-win Y+Black clock restart, Green Flag replay, renewed jumping/Black restart and clean browser return | Timer-fixed archive needs Xbox installation and later-level/victory/replay tests; historical second-Exit handoff; audio |
| Connect Four ([checklist](xbox-game-qualification.md)) | Both players; horizontal/vertical/diagonal wins; full-column rejection/replay | Launch cycle | One unexplained initial mouse-mode launch; no authored playback |

The [November 1 upstream 1.3 sync](xbox-upstream-1.3.md) passes the normal Xbox
build, native/SDL diagnostics, GPU fixtures and another 21-game native-emulator
launch/Exit cycle. The current combined runtime now has the bounded physical
checks above. Earlier physical results retain their identified executables.

## Nine additions: target pack of 30

These are physical Xbox results, not complete-game passes. **B** means real
gameplay works but important checks remain; **C** means playable with
significant limitations. Neither grade establishes smoothness. All nine still
need longer sessions and audio/frame-pacing checks. Independent two-pad binding
remains unverified. No grade is raised merely for launching or clearing an early
level.

| Game                                                                 | Playability / tested objective                                                                                                                                     | Changes that enable it                                                              | Still open                                                                                                                                                                                                              |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Beach Volleyball](https://scratch.mit.edu/projects/333452181/)      | **B:** X starts Easy CPU; directions/A jump; natural 2–5 loss, automatic title return/X replay, browser return. Ordinary current dashboard build repeats the loop. | Prepared copy adds CPU shortcut/hint; original gameplay and assets preserved.       | Player win, independent two-player controls, longer matches and quality. Short Start is not its ending replay.                                                                                                          |
| [GlowBall](https://scratch.mit.edu/projects/112176502/)              | **B:** CPU match, Score 2–5 loss, title/X replay and browser return.                                                                                               | Prepared CPU shortcut/hint and controller profile.                                  | Player win, independent two-player controls, current dashboard-build repeat and quality.                                                                                                                                |
| [Level EATEN!](https://scratch.mit.edu/projects/704676520/)          | **C:** Ordinary RGBA-fix build clears Levels 1–2, earns Level 3 and passes Y reset/browser/launcher return.                                                        | Xbox RGBA tile-upload repair; existing keys mapped in a profile.                    | Later levels, repeated startup, quality and the complete loop on the promoted combined build.                                                                                                                           |
| [Fireboy and Watergirl](https://scratch.mit.edu/projects/571560558/) | **C:** Ordinary combined build clears Level 1/all seven gems/both exits; B Menu → earned Level 2 start → browser. Time medal missed.                               | Xbox source-alpha collision/RGBA repairs; prepared selector/results shortcuts.      | Later levels, independent two-pad controls, repeated startup and quality.                                                                                                                                               |
| [Paint the Maze](https://scratch.mit.edu/projects/314731988/)        | **B:** First three puzzles won; Y reset, B Home/A resume and browser return.                                                                                       | Prepared A Play/B Home shortcuts reuse authored click handlers; profile maps reset. | Later puzzles, controller Save/Load, current dashboard-build repeat and quality.                                                                                                                                        |
| [Candy Caves](https://scratch.mit.edu/projects/1385416673/)          | **B:** Mining earns candy; natural Game Over, A replay/new map, renewed mining and browser return.                                                                 | Prepared map-clone initialization workaround; original assets/credits preserved.    | Original-project engine compatibility, upgrades/later progression, current dashboard-build repeat and quality. Original loads in official Scratch; retained xemu guest reports only 64 MB and faults during allocation. |
| [Bouncy Heroes](https://scratch.mit.edu/projects/173918262/)         | **B:** Ordinary current dashboard build: directions/A dash/B slam, Score 10, natural Game Over, A title/new round, renewed combat and browser return.              | Controller profile only; original project unchanged.                                | Characters/menu coverage, longer runs and quality.                                                                                                                                                                      |
| [Ninja Climb](https://scratch.mit.edu/projects/404349977/)           | **B:** First course clear → earned course 2, spike death/respawn, Green Flag replay and browser return on ordinary combined build.                                 | Shared scheduler repair; original project unchanged, controller profile.            | Later courses, current dashboard-path repeat and quality.                                                                                                                                                               |
| [Mushroom Valley](https://scratch.mit.edu/projects/285730673/)       | **B:** Ordinary current dashboard build: charged jumps, Score 14/natural loss, A retry to zero, renewed Score 1 jump and browser return.                           | Prepared copy adds A to the original mouse-only Retry gate and an ending hint.      | Longer runs, repeated handoffs and quality. Retry randomly changes the character in the original project.                                                                                                               |

Project helpers are
[merged in PR #65](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/65);
they create separate copies rather than patching the engine or changing physics.
The
[shared scheduler repair (#66)](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/66)
enables Ninja progression. Xbox graphics repairs are
[RGBA uploads (#72)](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/72)
and
[source-alpha collision (#71)](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/71).

Private controller scenarios and unmodified capture evidence are retained under
the shared rig's `observations/scratch-pack30-20261101/`. The November 2 regular
launcher checks use the `primary-…-144` run names and a reversible installation
receipt. Generic runner completion is reviewed against actual video before any
gameplay result is recorded.

## Performance and audio

The measured Appel comparison on the real 128 MB Xbox at 480p ran about
**27–28 FPS** in short wall-walking loops. Baseline/cache pairs were
27.79/28.46 FPS, then 28.04/27.55 FPS on the repeated controller route.
The apparent gain reversed; the [transform-cache experiment, PR 35](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/35)
remains unmerged. Window-p95 frame times were near 53 ms, with occasional 168–186 ms delays
in those samples. This is not a whole-level benchmark or native-NV2A measurement.
The newer [paired collision-fix sample](xbox-alpha-collision.md#bounded-hardware-performance--november-2-2026)
measures Fireboy's stationary spawn at 29.84/29.89 FPS and Appel movement at
27.03/26.54 FPS (baseline/fix). Script time rises about 0.8/0.7 ms per frame.
These bounded samples do not establish whole-game smoothness or a performance
improvement; the correctness repair has a measured cost.

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
  late/duplicate input. The November 2 runs use the advertised P4 Player Two
  route to S3 `192.168.1.243`; actual game input and neutral release are checked.
  Earlier direct-S3 checks used a different firmware configuration. No firmware
  or routing changes are part of the new game tests, and they do not qualify
  independent multiplayer binding or every physical port.
- Returning to responsive XBMC has occasionally left FTP unavailable. One
  verified XBMC software Reboot restored it in each of two recent cases. This
  network handoff remains open; a responding KVM alone does not prove game
  liveness, and the cause is not assigned to a graphics fix.
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
