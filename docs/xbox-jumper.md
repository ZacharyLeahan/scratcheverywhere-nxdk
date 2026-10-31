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

### Current-build repeat

The normal current-main build, XBE `c7c0a9d9…` from the code merged through
[PR 55](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/55), also
clears **courses 1–19** with native graphics/windowing. This fresh run starts
from the browser with the same prepared archive and controller profile above;
it includes the [color-boundary correction](xbox-color-self-alpha.md).
The final stage's two opening ledges and lower underpass pass again, but
victory and post-victory replay remain unverified.

Short automated jump holds needed longer presses, and routes needed adjusting
for different entry heights. Natural deaths and wall-jump recovery are retained
in the evidence. These adjustments change only the test controls; no game or
engine repair, gameplay-state writes or saved-state loading were used. Read-only
collision-image inspection supports route planning, not a gameplay pass.

Private evidence: `build-xbox/jumper-c7-fullrun-20261031/`, including
`receipt.json`, `checkpoint.json`, per-course reviews and `end-state-audit.json`.
Both preserved test guests end paused with controls released. This repeat adds
no physical-console, audio, smoothness or frame-rate qualification.

## Still needed

- Complete the final stage and verify the visible win, timer stop and replay.
- Repeat later-course gameplay on the physical Xbox. Emulator frame budgets are
  not Xbox FPS, smoothness, audio or retail 64 MB qualification.
- Repeat the historical second-Exit handoff on current native hardware; prior
  readiness-guard checks pass quick A start and two exits in the emulator.
- Verify subjective/long-run audio and the separate
  [numeric monitor repair](xbox-monitor-number-formatting.md) on hardware.
