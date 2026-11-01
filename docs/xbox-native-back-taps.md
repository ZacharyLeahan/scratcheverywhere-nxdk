# Native Xbox Back taps across slow frames

A short Back tap can arrive and be released entirely between a game's input
polls. The native controller previously kept only the latest USB report, so
the game saw neutral and never opened the console menu. This is separate from
the physical KVM adapters disconnecting.

## Reproduction and fix

On frozen native `807d1928...`, the normal Space Invaders → Mario browser transition
reproduces the miss. Read-only execution hooks record Back in the cached USB
report at video frame 4507 and neutral at 4518. No game input poll runs during
the 12-frame tap; the next poll at 4528 reads neutral. The prior Back-edge flag
is zero, ruling out a stale held flag in this reproduction. A clean first Mario
launch accepts the same tap, so the miss depends on timing.

Each valid controller now retains a rising Back edge until the main input poll
consumes it alongside the live report under the existing DPC-level snapshot.
Release does not erase the pending request; disconnect, invalidation and
reconnection clear it. Only reserved Back is retained. Gameplay buttons and
menu confirmation remain live snapshots, and reset-hold timing is unchanged.

## Validation

- Targeted ASan/UBSan checks cover complete taps between polls, one-shot
  consumption, repeated held reports, another player's activity, disconnect,
  reconnect, malformed packets, unchanged gameplay snapshots and reset holds.
- The normal NXDK 480p build with debug symbols succeeds; profiling and runtime
  trace options remain off. Candidate XBE SHA-256 is
  `4ef49719b046338800c97e9858a4721ff8460039c8c85f2b87cba65a7d2ee1f5`.
- The unchanged full prepared Mario archive `7efb9b52...` passes a clean intro
  tap and three Space Invaders → Mario transition probes in private 128 MB
  Vulkan xemu, through actual emulated USB controls on renderer/window 3/0.
  In the second transition, the tap ends before any input poll; frame 7073
  reads neutral with Back pending, consumes the request, and the
  runtime pause check opens the menu at 7096.
- The third helper initially reports no pause after its 36-neutral-frame budget.
  Its trace nevertheless shows the pending request consumed after release.
  Another 60 neutral frames opens pause without another button press. That raw
  early result is retained: the fix preserves a tap, but a slow render can
  still delay the end-of-frame pause check. It cannot recover a permanently
  stuck game thread and supplies no frame-rate or smoothness acceptance.
- Back resumes and reopens the game menu; neutral input leaves it paused.
  Held-A Exit returns to all 21 games/42 buttons with zero game sprites.
  A fresh 2048 launch, short Back and another held-A Exit also pass.
- A short reset hold does not reboot; release cancels it. A fresh full
  Start+Back+both-triggers hold reaches actual `XReboot` after 121 video frames
  and then fresh application `main`. This verifies that path in the emulator,
  not physical dashboard or frozen-thread recovery.

Ignored receipts, original captures and read-only hook logs are under
`build-xbox/native-mario-early-back-20261029/`; fixed results are in
`fix/review.json`. Both guests close, and the saved shared HDD and normal Mario
archive remain unchanged. The fix is not installed on the Xbox. Physical taps,
controller handoff, audio, pacing and retail 64 MB qualification remain open.

## Pause before the next game frame — October 31, 2026

A fresh normal-main `a66ca892…` run isolates a second source of delay. During
Mario's intro, a single 12-video-frame Back press followed by 12 released frames
is received and retained. Pause appears after another 120 neutral video frames,
without a second press. The earlier color-regression cycle checked too soon;
its apparent misses do not establish another input-loss bug.

Xbox now checks reserved Back immediately after reading input, before running
more scripts or rendering the next game frame. It also rearms the Back edge
when a pause-menu action finishes after release, so a new tap can pause again.
The existing native input latch, gameplay controls and reset chord are unchanged.
This is an Xbox-specific runtime change; other platforms keep their existing
pause handling.

The matching normal candidate `ad481593…` on its first Mario launch opens
pause by the end of the same press/release sequence, with no additional
neutral-frame wait. Three Back resume/reopen cycles, a neutral pause and held-A Exit also pass in the native
emulator. No gameplay state is written; only renderer selection is overridden
before startup. These are bounded emulator observations, not physical latency,
FPS or complete-gameplay measurements. Work already blocking an input poll can
still delay pause, and a stuck game thread still needs external recovery.

All 21 projects also pass normal native browser selection, archive load, one
Back tap and held-A Exit, returning to the exact 21-game/42-button list with
zero game sprites each time. Mario needs another 48 neutral video frames in
that longer cycle; the other twenty need none. A separate Maze check holds A
on Green Flag: restart waits for release, restores the exact initial image,
then movement and another clean Exit work. These are menu regressions, not
new full-gameplay or audio passes.

At this checkpoint SDL still has a short-tap limitation: the same intro tap fails
on both unchanged `a66ca892…` and the candidate. The native controller latch
does not cover SDL snapshots. The [SDL USB-read follow-up](xbox-sdl-back-taps.md)
addresses that separate gap. This pause-priority candidate passes longer Back pause/resume/
reopen and held-A Exit. Its short reset hold cancels; a full chord reaches
actual `XReboot` after 124 video frames, then fresh application `main`. This
confirms responsive-thread emulator behavior, not recovery from a hard hang.

Private evidence: `build-xbox/mario-back-single-tap-20261031/review.json` for the
baseline and `build-xbox/pause-priority-20261031/native/` for the candidate,
matching XBE/ELF/ISO receipts, input snapshots and original captures. SDL
results and the unchanged comparison are in `sdl/` and `baseline-sdl/`.
This candidate has not been deployed to the physical Xbox.
