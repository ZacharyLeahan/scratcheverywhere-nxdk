# Native Xbox hardware follow-up — October 30, 2026

The 128 MB physical Xbox now has a limited native-backend gameplay result on
unchanged main. **Startup reliability and all-21-game qualification remain
open.** No initialization experiment from this investigation was merged.

## Normal main build

The separate executable is SHA-256
`207edc251d01fb9ddfba341b2ab67557f278b2c5ea514bf3287efddb4bd86f08`.
It was built from the code merged in [PR 43](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/43);
main `2760ff8c…` adds documentation to that code. All tracing, GPU probes and
frame/thread profiling are off. The test requests NV2A graphics/windowing and
Xbox audio; the recovered log confirms those actual backends.

After a longer startup observation, the native browser appeared. A separate
8-second HDMI stream retained 71 frames. Catch Apples then passed:

- Selection from the normal game list and actual archive loading.
- Normal timer expiry at **Score 13 / Timer 0**, with Game Over visible.
- Short Start replay to **Score 0 / Timer 30**.
- D-pad Right and Left while the replay timer advanced; the score reached 2.
- Back pause, held-A confirmation and one clean return to the populated browser.
- Start + Back + both triggers held three seconds, followed by XBMC recovery.

The replay/steering recording retains **148 original JPEG frames over 6.82
seconds**. These are capture measurements, not game FPS. A separate Left input
after timer expiry is excluded from steering evidence. This is one native Catch
launch/exit cycle; it does not establish repeated handoff reliability, audio
quality, smoothness, another game's behavior or retail 64 MB support.

The same executable also passed a separate legacy Xbox-renderer Catch trial:
timer ending, short-Start replay, recorded Right/Left steering, one browser
return, and the System menu's Restart Xbox confirmation. Its saved audio choice
was SDL3, but its log identifies the actual fallback backend as Xbox audio.

## Purple startup and the rejected experiment

Earlier captures of normal main and a logging-only variant showed purple even
though their logs reached the browser. The logging-only variant continued
finishing frames and accepted a three-second controller reboot. Therefore
purple did not, by itself, establish an unresponsive application.

A diagnostic variant passed all 14 GPU pixel probes on this console, including
viewport/scissor, off-screen target restoration, alpha and subrect composition.
That is a separate instrumented build, not evidence of reliable normal startup.

An experiment forcing the existing main-target restoration at construction
reached the browser twice and ran Catch, but another early capture was purple.
That trial was reset before a longer observation. Unchanged main subsequently
reached the browser under the longer observation too. **The experiment has no
demonstrated benefit and was discarded.** Neither extra probe drawing nor an
arbitrary startup delay is being shipped as a fix.

Short KVM captures can include old frames. Continue with an explicit observation
window, longer live streams, backend logs and a controller/navigation response
before classifying a startup failure. The intermittent startup issue remains
under investigation; no GPU register or timing cause has been established.

## Recovery and remaining checks

The application's reset threshold is two seconds. The shared test runner's
original maximum hold was exactly that threshold, so its failed two-second
attempt was not proof of a hard hang. A privately validated runner copy allowed
a three-second hold and recovered both the purple logging-only trial and normal
main to XBMC. Shared tracked tooling and KVM firmware were unchanged.

All test executables were uploaded to separate folders with complete FTP
readback. The primary dashboard executable and game archives/control profiles
were preserved. After testing, the exact original settings were restored with
readback verification; their SHA-256 is
`adc181b7f41955ab7356dcc88329e6416c650bd50c301bd00c647b25e78454d2`.

That checkpoint left repeated observed native starts, the other twenty games,
longer gameplay/audio and measured Appel performance open. The latest three-game
and timing follow-up is below. The [hardware checklist](xbox-game-qualification.md) retains all outstanding gates.

Private evidence is in the shared ESP-KVM observations run
`scratch-p1-reconnected-20261029T231759Z`: `main-native-long-video/`,
`main-native-catch-steering-video/`, `main-native-catch-exit/`, and the final
reset/FTP receipts. `initial-target-rejection.json` preserves the discarded
experiment; no diagnostic payloads or game archives are bundled here.


## Current main: three-game hardware check — October 30

Normal main after [PR 46](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/46)
uses XBE SHA-256 `eb3492c2b7149a14200d02486a5d12b95cf886ebdb26655c255ac5f738a24535`.
Profiling and runtime traces are off. The retrieved startup log confirms native
NV2A graphics/windowing at 640×480 and Xbox audio on the physical 128 MB console.
One session passes:

| Game | Observed on the Xbox |
| --- | --- |
| Catch Apples | Browser selection; natural Game Over at Score 14 / Timer 0; short-Start replay; visible Right and Left basket movement |
| Appel, installed v3 | Browser selection; controller Play/level-selection menus; Level 1 terrain; ordinary walking/jumping to two apples |
| PacMan, original installed copy | Browser selection; Right/Up corridor turn; Score 40 / High Score 40 |

Each game accepts a 180 ms Back tap, shows the runtime menu, and returns to the
populated browser after a 1.2-second A confirmation and release. No accidental
2048 launch occurs in these three returns. The three-second homebrew reset chord
then reboots to XBMC, where FTP retrieves the session log and verifies unchanged
Appel/PacMan archives. This is one launch per game and one application start;
full gameplay, repeated-start reliability, frame rate, listening quality and the
other eighteen games remain open on this current native build.

The first Catch replay/Right attempt leaves the basket in its initial location
and is excluded from steering evidence. A later shorter Right press visibly
reaches the right boundary; Left then visibly moves it back. No input or engine
fix is inferred from that inconclusive first attempt.

The main KVM is running `v.0.56.1-179-g083d473-dirty`, whose matching local build
has S3 routing disabled. Direct documented S3 HTTP input at `192.168.1.244`
visibly navigates XBMC and controls these games. Another online board reports
USB completions without a visible dashboard response to the test press; that
is not an input-delivery pass. The Xbox log enumerates three controllers, so
this session does not establish single-controller isolation or physical port
assignment. No KVM firmware was changed. Scenarios retain the shared validator,
report encoder and OXOS-inspired bounded evidence workflow; raw completions
remain inconclusive until the actual screens are reviewed.

Private evidence: shared observations `scratch-physical-current-20261031T013014Z`,
`normal-current-review.json`, `native-current-*` plans/captures, and
`normal-current-ftp-after/debug.txt`. The normal review verifies 1,138 original
JPEG hashes. After the separate timing follow-up, all 21 archives and 20
control sidecars match the fresh pre-session backups byte for byte. The exact original settings
are restored and verified as `adc181b7…`; the primary dashboard launcher is
preserved. XBMC FTP is available, and all controls/capture/listeners are released.


## Dashboard recovery and saved log — October 31

The previous native Maze session's 2,806-byte startup log is now saved, SHA-256
`372b572bc4e40adc9fe81282ef41aef465ff47cf9741bac490a1789c66e79ccd`.
It records successful NV2A 640×480/Xbox-audio initialization, the browser, three
controller identifiers and Maze archive/control loading through precache.
It contains no explicit crash and does not explain the later signal loss.
Native Maze replay and Exit remain unverified in that hardware session.

Direct S3 input visibly navigated XBMC settings. Toggling XBMC's enabled FTP
service off and on restored access long enough to retrieve the log and restore
the exact original settings, with full readback matching `adc181b7…` above.
The next launch preflight timed out connecting to FTP, before writing settings
or requesting RunXBE. HDMI and controller USB then became unavailable while
still in XBMC, before any new Scratch launch. This dashboard occurrence does
not establish a Scratch crash or a hardware root cause. The saved preferences
are restored; there is no pending settings rollback.

Private evidence: shared observations `scratch-reconnected-20261031T1153Z`,
`retrieval-restoration-receipt.json`, `ftp-before/debug.txt`,
`Settings-restored-readback.json` and the aborted native-launch receipt.
