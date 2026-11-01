# SDL Back taps during slow Xbox frames

The legacy Xbox SDL backend could lose a complete Back tap while a game was
loading a costume. This is separate from the physical KVM adapters disconnecting.

## Cause and change

Frozen normal build `ad481593…` reproduces it in Mario's intro: the requested
12-video-frame tap spans frames 2983–2995, with no SDL joystick update or USB
callback during that interval. The first callback afterward, at frame 3014,
contains neutral input. The driver starts its next read from the main-thread
update, leaving a sampling gap while that thread is busy.

The Xbox-only SDL driver patch now reuses the completed USB transfer immediately
in its callback, retains Back's rising edge, and snapshots it at DPC level.
SDL emits the retained down/up events while its final button state still matches
the latest report. The application keeps that reserved menu request until its
next input poll. Gameplay and confirmation buttons remain live snapshots.

USB errors and malformed gamepad reports clear stale state; the main thread
retries a failed read. Disconnect clears the driver reference before the USB
stack frees the device, and removal/cleanup clears the application's retained
request. The changes are in the Xbox SDL dependency patch and guarded Xbox
window/input code. Other platforms, native input, game archives and controller
profiles are unchanged.

## Validation — October 31, 2026

- The host harness compiles the actual patched callback, update and close code
  with stubbed USB/SDL services under ASan/UBSan. It covers complete taps,
  repeated holds, live A, a completion after the protected snapshot, truncated
  allocations, malformed/error reports, rearm failure, retry, disconnect/close
  lifetime and four-pad Back-event handoff. The unchanged callback fails at the
  missing rearm. Run `python3 tests/xbox_sdl_controller_test.py` after building.
- Normal Release candidate `c7c0a9d9…` builds with tracing/profiling disabled;
  complete ISO readback matches the XBE and matching symbols.
- In the cold SDL Mario probe, Back reaches the callback at frame 3038 and
  neutral at 3049. The next game poll at 3099 sees a neutral raw report, yet
  pause opens without another press after 48 additional neutral video frames.
  Three short Back resume/reopen cycles and held-A Exit also pass.
- Actual virtual USB removal of port 1 clears its SDL handle/retained slot.
  Port 2 navigates, launches 2048, pauses and exits. Reconnecting port 1 and
  removing port 2 restores navigation with a new device ID and no stale request.

- All 21 SDL browser selections, archive loads, single Back taps and held-A
  exits pass, returning to zero sprites and the exact 21-game/42-button list.
  This cycle needs no extra pause wait after each tap/release sequence.
- Holding A on Green Flag waits for release, restores Maze’s exact initial
  image, then movement and another clean Exit work. A short reset hold cancels;
  a full chord reaches actual `XReboot` after 123 video frames and fresh `main`.

A separate cold native NV2A smoke test on the same XBE also accepts a short
Mario Back tap and returns cleanly to the browser. It does not repeat every
native gameplay objective.

These are emulator/controller regressions, not
physical gameplay, FPS/audio, 64 MB or hard-freeze recovery acceptance. Work
already blocking the game thread can still delay the visible menu.

Private receipts, original captures and matching artifacts are under ignored
`build-xbox/sdl-back-retention-20261031/`. The initial route-only probe is retained
as a failed test assumption: binding `none` leaves the virtual USB pad attached;
actual removal uses the observed device IDs. The user’s separate emulator is untouched,
and the older Jumper run stays paused separately. This candidate has not been deployed to the physical Xbox.
