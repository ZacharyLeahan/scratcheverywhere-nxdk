# Original Xbox follow-up for Mike

Updated November 1, 2026. **This recap and its GIFs stay on a feature branch.**
[Main](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/tree/main) has the
latest code; the [game status](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/blob/main/docs/xbox-game-status.md)
tracks what actually passed.

## Upstream baseline

Our main now includes upstream through
[`1d606eb4`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/1d606eb47e18b96a82349fea83e9cdf060ea88d2),
including [release 1.3](https://github.com/ScratchEverywhere/ScratchEverywhere/releases/tag/1.3).
The native NV2A/window/audio work is upstream's baseline. Earlier input-default,
SB2 parsing and resampler fixes are already incorporated; their implementation
files match upstream. They are not being proposed again.

## What remains in our fork beyond upstream

These follow-ups remain beyond upstream. Some predate the 1.3 tag; this is the
**current code difference**, rather than a list of changes authored after release. [Full fork-only comparison](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/compare/1d606eb47e18b96a82349fea83e9cdf060ea88d2...main).

| Scope | Follow-up / review link |
| --- | --- |
| Shared core | [Exact subject alpha for color sensing](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/7f6015cf8a6d8083eb4939ccd9cffc06fb55048b), with an expanded 58-case reproducer. [Monitor number formatting](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/d0cbbbfdb29ff5bd08ec7556f4c33efbd44406c9) removes distracting decimal tails. Other platforms still need review. |
| Xbox graphics | Retain exact collision colors, SVG filtering, alpha-correct brightness/pen compositing and clamped texture uploads around your newer effect cache. [1.3 merge/adaptations](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/61) and [evidence](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/blob/main/docs/xbox-upstream-1.3.md). Experimental GPU hue stays off by default. |
| Xbox input | [Pause before the next game frame](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/300b42ddf7ea36e31dce89970deb3b2bfbe06998) and [retain short SDL Back taps](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/75da9c5b7d485a04a338c234ed1dfb76c6c4133a). Native controller handoff and confirmation-release gating remain. Slow work already running can still delay pause. |
| Xbox homebrew controls | Return to game list/launcher, short Start replay for stopped projects, Restart Xbox / Shut down menus, and **LT + RT + Back + Start** held two seconds. [Implementation](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/7bd8152f0f8e9d031875e28ca50add7db9aaab9f). A three-second test hold reaches XBMC while the runtime responds; disconnected controls or a hard hang cannot guarantee reset. |
| Individual projects | Reproducible prepared copies, separate from engine changes: [Jumper post-win timer restart](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/2a52b3114e24c8e35d57976d986fab82c4516730), [Sokoban full-set map/goal repairs](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/commit/1ecd8978f78cf78c6caa1566e7c0e19cda209492), and the other [preparation scripts](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/tree/main/scripts). Controller sidecars only map existing keys. |

For upstream review, the small shared fixes and their reproducers are the best
starting point. Keep Xbox backend changes and prepared Scratch projects separate;
the full fork comparison is context, not a request to pull every commit.

## What testing establishes

The 1.3 integration builds, passes native/SDL regressions and both GPU fixtures,
and launches/exits all **21 games** in native xemu. Separate emulator runs complete
Mario, a Retro Racing lap, all 20 Jumper courses and all 13 Sokoban puzzles.

On the physical **128 MB Xbox**, native Maze passes win/replay/two clean returns;
Sokoban completes puzzles 1–11 and is paused in twelve. These use the earlier
tested executable; the new 1.3 binary is not yet hardware-tested. The primary
launcher remains the older SDL build. **Full 21-game and 64 MB qualification are open.**

Open: native startup/handoffs, later levels/replay, audio and Appel smoothness.
A short Appel sample near 29 FPS does not establish a speed improvement; the
transform-cache experiment stays unmerged. KVM delivery is tracked separately
from game defects. See the [current matrix](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/blob/main/docs/xbox-game-qualification.md).

## Games in action

These are **physical Xbox captures**, including older sessions, at their recorded
pace. GIFs are silent; written milestones can come from later tests. Scratch
source links and credits are retained. [Capture provenance](mike-gameplay/README.md).

### [Ultra Bird](https://discord.com/channels/428359196719972353/428399682239332354)

<img src="mike-gameplay/ultra-bird.gif" alt="Ultra Bird gameplay on the physical Xbox" width="480" height="320">

Six pipes scored; original archive.

### [Hopper Heros](https://scratch.mit.edu/projects/1184969400/)

<img src="mike-gameplay/hopper.gif" alt="Hopper Heros gameplay on the physical Xbox" width="480" height="320">

Movement/jump and replay; original Everywhere variant.

### [Catch Apples](https://scratch.mit.edu/projects/124652800/)

<img src="mike-gameplay/catch-apples.gif" alt="Catch Apples gameplay on the physical Xbox" width="480" height="320">

22 points at timer expiry; native ending/replay also checked.

### [Maze Starter](https://scratch.mit.edu/projects/10128431/)

<img src="mike-gameplay/maze.gif" alt="Maze Starter gameplay on the physical Xbox" width="480" height="320">

Native Xbox win/replay and two clean returns; prepared copy.

### [Snake](https://scratch.mit.edu/projects/511466864/)

<img src="mike-gameplay/snake.gif" alt="Snake gameplay on the physical Xbox" width="480" height="320">

Score 225, loss/replay and four-direction steering.

### [Appel](https://scratch.mit.edu/projects/60917032/)

<img src="mike-gameplay/appel.gif" alt="Appel gameplay on the physical Xbox" width="480" height="320">

Hardware: 21/35 apples and checkpoints; older clip shows seven.

### [Tetris](https://scratch.mit.edu/projects/469540467/)

<img src="mike-gameplay/tetris.gif" alt="Tetris gameplay on the physical Xbox" width="480" height="320">

Ten lines/Level 1; original + profile.

### [Frogger](https://scratch.mit.edu/projects/12221773/)

<img src="mike-gameplay/frogger.gif" alt="Frogger gameplay on the physical Xbox" width="480" height="320">

Six pads in one round; prepared copy.

### [Breakout](https://scratch.mit.edu/projects/11007566/)

<img src="mike-gameplay/breakout.gif" alt="Breakout gameplay on the physical Xbox" width="480" height="320">

Full board at 1,940; prepared copy.

### [PacMan](https://scratch.mit.edu/projects/13701368/)

<img src="mike-gameplay/pacman.gif" alt="PacMan gameplay on the physical Xbox" width="480" height="320">

Walls, pellets and replay; original + profile.

### [Space Invaders](https://scratch.mit.edu/projects/253610111/)

<img src="mike-gameplay/space-invaders.gif" alt="Space Invaders gameplay on the physical Xbox" width="480" height="320">

Hardware: 1,230 points and loss/replay.

### [Asteroids](https://scratch.mit.edu/projects/32219470/)

<img src="mike-gameplay/asteroids.gif" alt="Asteroids gameplay on the physical Xbox" width="480" height="320">

9,200 points and replay; original scripts + profile.

### [Sokoban](https://scratch.mit.edu/projects/24490009/)

<img src="mike-gameplay/sokoban.gif" alt="Sokoban gameplay on the physical Xbox" width="480" height="320">

Native Xbox: puzzles 1–11 complete; checkpoint paused in twelve.

### [2048](https://scratch.mit.edu/projects/19554088/)

<img src="mike-gameplay/2048.gif" alt="2048 gameplay on the physical Xbox" width="480" height="320">

Unseeded 2,048-tile win; prepared A acknowledgement.

### [Retro Racing](https://scratch.mit.edu/projects/26999060/)

<img src="mike-gameplay/retro-racing.gif" alt="Retro Racing gameplay on the physical Xbox" width="480" height="320">

Acceleration, braking and steering; original scripts + profile.

### [Hill Climb Racing](https://scratch.mit.edu/projects/56667360/)

<img src="mike-gameplay/hill-climb.gif" alt="Hill Climb Racing gameplay on the physical Xbox" width="480" height="320">

Jeep/motorcycle, crash/replay; original scripts + profile.

### [Super Mario Bros.](https://scratch.mit.edu/projects/196684240/)

<img src="mike-gameplay/mario.gif" alt="Super Mario Bros. gameplay on the physical Xbox" width="480" height="320">

Opening pipes and death recovery; prepared copy.

### [Doodle Jump](https://scratch.mit.edu/projects/399123680/)

<img src="mike-gameplay/doodle-jump.gif" alt="Doodle Jump gameplay on the physical Xbox" width="480" height="320">

1,044 m and automatic replay; original scripts + profile.

### [Jumper](https://scratch.mit.edu/projects/103069687/)

<img src="mike-gameplay/jumper.gif" alt="Jumper gameplay on the physical Xbox" width="480" height="320">

Levels 1–4 cleared; prepared controls/readiness copy.

### [Connect Four](https://scratch.mit.edu/projects/52769452/)

<img src="mike-gameplay/connect-four.gif" alt="Connect Four gameplay on the physical Xbox" width="480" height="320">

Both colors and three win directions; prepared copy.

### [Zach’s Spider Adventure](https://scratch.mit.edu/projects/1396458859/)

<img src="mike-gameplay/spider-adventure.gif" alt="Zach’s Spider Adventure gameplay on the physical Xbox" width="480" height="320">

Jumping, spider stomps and scoring; original game + controller profile. Hardware Level 6 / Score 7,516; all ten levels in xemu. [Details](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/blob/main/docs/xbox-spider-adventure.md).

Hopper links to the original game; we tested its Everywhere variant. Ultra Bird's
link is the example Discord channel because its standalone project URL was not
recorded. Full Appel Level 1 completion is currently emulator evidence; the
normal physical run has not yet repeated that win.

## Why adding games is cumbersome

**The browser selects installed games. There is no in-app Scratch search,
download or add flow.** Download the `.sb2`/`.sb3` on a computer, return to XBMC,
FTP it (and any controller sidecar) into `E:\ScratchEverywhere\`, then relaunch.
That transfer/setup loop is what I meant by tricky when playing with my daughter.

An archive receiver/import screen and easy arrows/WASD presets would help. A
per-project Controls editor already exists; make it easier to find. Importing a
project would not guarantee its compatibility.
