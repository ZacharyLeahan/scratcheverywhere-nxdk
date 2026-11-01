# Jumper on Xbox

[Jumper by Depicklator](https://scratch.mit.edu/projects/103069687/) has prior
physical-Xbox checks through levels 1–4, with level 5 rendered, lava death and
respawn, Black level restart, Y+Black full restart, Green Flag replay and browser
return. The controller-ready prepared copy maps A to Play/Up and preserves the
original gameplay and assets; see `scripts/prepare-jumper.py`.

## Native emulator progress — October 31, 2026

Normal main XBE `eb3492c2…`, native NV2A graphics and a 128 MB snapshot guest
clear **courses 1–19 and reach the final stage, course 20**. This is ordinary
controller play guided by read-only observations. It covers jumps, wall jumps,
magenta boosts, water ascent/descent, narrow passages, platform landings and
natural lava deaths/respawns. The only debugger write selects the native
renderer before loading the project. No position, level, collision or velocity
state is written, and no saved gameplay state is loaded.

The final stage's opening two ledges and lower underpass/floor-lava running jump
also pass. Its next narrow lava gap remains unfinished. **Victory, the stopped
timer and post-victory replay are unverified.** There are twenty playable courses;
the twenty-first platform costume is the authored “You Win!!!” scene.

Failed routes remain in the evidence. A short jump request missed once; a longer
A press is confirmed in both the emulator input state and subsequent movement.
Backing up, wall jumping and adding a running start cleared later obstacles.
No game or engine repair was needed for this progress. Some early death
verifiers also mistook the authored next-level position reset for a death before
the level handler completed; no exact total death count is claimed.

The shared emulator disk initially contained the original Jumper archive and
profile. A private disk copy was updated from the physical-console backups,
with old-hash guards and full FTP readback:

| Fixture | SHA-256 |
| --- | --- |
| Installed prepared Jumper archive | `48f4577fa315e8f915c7713f36dfa0dab859b16f987871f6cc3fd57ef351a62e` |
| Installed controller profile | `454f1e88c619982febbd146a10301255c2ef7f2833758a3b1124474b44c7aa5a` |

Provisioning used a separate maintenance guest, which was closed before the
normal snapshot run. The shared disk and private gameplay base retain their
before-run hashes. This fixture correction changes neither the physical console
nor game code. Other projects' extended results retain their documented fixtures.

Private evidence: ignored `build-xbox/jumper-native-fullrun-20261031/`, especially
`fixture-install-receipt.json`, `review-progress.json`, controller/QMP histories,
original screenshots and failed-route reviews.

### Current-build full run

The normal current-main build, XBE `c7c0a9d9…` from the code merged through
[PR 55](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/55), also
clears **all twenty courses** with native graphics/windowing. This fresh run starts
from the browser with the same prepared archive and controller profile above;
it includes the [color-boundary correction](xbox-color-self-alpha.md).
The final route uses wall jumps to reach the left column's black cap, jumps over
the upper lava, lands in a safe gap and walks under the last obstacle. The visible
**“You Win!!!”** scene settles at level 21. Its authored timer stays at 90.8 during
a separate 240-frame neutral observation; this is not a performance measurement.

Natural deaths, wall-jump recovery and failed routes are retained. Read-only
thread inspection identifies completed movement loops for controller feedback;
an input change arriving one loop late stops the planned sequence. Neither host
route predictions nor intermediate collision probes count as gameplay passes.
No game-state writes, saved-state loading or engine repair were used to win.

After the restart issue below, the pause menu's held-A Green Flag confirmation
returns to Play. A starts a new game, its timer advances, jumping works and Black
restarts the level. Held-A Exit returns to exactly 21 browser entries / 42 buttons
with zero project sprites, and another neutral interval leaves that browser stable.

Private evidence: `build-xbox/jumper-c7-fullrun-20261031/`, including
`receipt.json`, `checkpoint.json`, per-course reviews and `end-state-audit.json`.
The completed current-build guest closes with controls released; the earlier
baseline run remains paused. This adds no physical-console, audio, smoothness or
frame-rate qualification.

### Post-victory restart timer

On the installed prepared copy, Y+Black after winning returns to course 1 but
leaves Timer at zero. The original `Text1` victory branch permanently stops its
clock; the authored Restart handler only resets its value. This is project logic,
not an Xbox runtime or input defect. Green Flag replay restores the clock.

`scripts/prepare-jumper.py` now replaces that one victory stop with a wait until
the level leaves 21. It keeps the existing single clock alive without starting a
second timer on ordinary restarts. Movement, assets, credits and the controller
profile are unchanged. The generated archive is SHA-256
`cb9ff89903dffd3899e07b483ce24b29fc498ebdee0f4adeb7bedcea01e76a3f`;
the profile retains `454f1e88…` above. Existing installations need the regenerated
archive copied over; updating the executable alone does not apply this repair.

Four archive-integrity/revision-guard tests pass. Separate old/fixed clock fixtures
run under the unchanged normal native executable: the old script reproduces the
failure; the fixed script passes victory freeze, post-win restart, three ordinary
restart cycles at a single-clock rate, and a second win/restart. These authored
diagnostic transitions do not substitute for playing the regenerated game to victory.

The regenerated full game also passes A-to-play, movement/jumping, Black and
Y+Black restart before victory, held-A Green Flag replay, and two fresh launch/exit
cycles on the private disk. Private evidence is in
`build-xbox/jumper-victory-timer-20261031/`, especially `clock-comparison-review.json`,
`fixed-jumper-smoke-review.json` and `archive-delta-audit.json`.

#### Full timer-fixed playthrough

A subsequent fresh native run of archive `cb9ff899…` clears all twenty courses
through ordinary controller play and reaches the visible win. The timer remains
stopped across a separate neutral observation. **Y+Black directly after this win
returns to course 1 with a running timer**, advancing from 1.2 to 3.0 in the next
observation. This verifies the repair in the full game as well as the clock fixture.

The run includes an authored Black restart on course 13 to take the lower route;
the unsuccessful upper-ledge attempt is retained. No game-state writes or saved
gameplay state are used. Read-only Player-loop inspection derives the current
bytecode boundary instead of assuming indices from an earlier load.

Held-A Green Flag replay then restores Play, A starts a new round, movement and
jumping resume, Black restarts the level, and held-A Exit leaves zero project
sprites and a stable browser. This private disk has the usual 21 games plus two
unselected clock diagnostics. No console archive, executable or settings were changed.

Evidence: `build-xbox/jumper-fixed-fullrun-20261031/`, including `receipt.json`,
`victory-and-restart-review.json`, `replay-and-close-review.json`, the original
screenshots and failed-route reviews. These emulator checks close the regenerated
archive's full-win/restart/replay gate; they add no hardware, frame-rate or audio acceptance.

## Still needed

- Install the regenerated archive and repeat victory/Y+Black/Green Flag on the Xbox.
- Repeat later-course gameplay on the physical Xbox. Emulator frame budgets are
  not Xbox FPS, smoothness, audio or retail 64 MB qualification.
- Repeat the historical second-Exit handoff on current native hardware; prior
  readiness-guard checks pass quick A start and two exits in the emulator.
- Verify subjective/long-run audio and the separate
  [numeric monitor repair](xbox-monitor-number-formatting.md) on hardware.
