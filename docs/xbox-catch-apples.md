# Catch Apples controls and replay

The Xbox install was missing `Catch-Apples-superd1.sb2.json`. The game checks
`left arrow` and `right arrow`, while the default D-pad keys are `g` and `j`.
The default left stick already supplies arrows. This explains the observed
stationary basket during D-pad testing; it is separate from the authored
timer-expiry behavior.

Copy [the supplied profile](../examples/catch-apples-xbox-controls.json) next to
the game archive, naming it exactly `Catch-Apples-superd1.sb2.json`. It binds
both D-pad and left stick to the game's left/right arrows. No archive edits or
runtime changes are required. Hold Start for the runtime menu; after timer
expiry, a short Start press restarts the stopped project.

## Physical Xbox check, October 26

On synchronized build `be4bc0b4…`, the initial D-pad run left the bowl at
approximately screen X=112 throughout. It reached Score 9 through incidental
stationary catches. The retrieved log reported that the control sidecar could
not be opened. An FTP folder audit confirmed the file was absent.

The new profile was uploaded with complete readback verification, SHA-256
`19a523f3f4501309d929545ab4edef0f529d218176ab333b941846344aaac04e`. Repeating
the timed round with D-pad steering moved the bowl across the stage and reached
**Score 22 / Timer 0**. The complete Game Over/replay instruction remained
visible. This ending uses Scratch stop-all; it is not evidence of an application
hang.

A separate 500 ms Start press restored **Score 0 / Timer 30**. Left-stick Left
then moved the bowl left, and Left-stick Right moved it back right as the timer
advanced through 29 and 28. An eight-second HDMI capture from the earlier round
contains non-clipping audio (peak 0.5, RMS 0.013642); subjective and long-run
audio quality remain unverified.

Exit returned to the populated browser after confirmation was released. A fresh
browser launch showed another playable round; D-pad Right moved the bowl right, and Left
moved it back left. The second exit also returned to the list.
Bonus/rotten-apple scoring has not been isolated in a targeted test. The game
scripts and assets remain unchanged. The installed archive matches the original
download byte for byte, SHA-256
`dfdc129664dff3a9b65f1c3523ba5d05f162e0b198b474cccc2cfd58cf7c1ede`.
The retrieved `catch-fixed-runtime.log` confirms all four movement bindings,
short-Start replay, two cleanup/browser returns and the dashboard reset combo.

Local evidence is under ignored `build-xbox/hardware/`:
`frog-snake-catch-controls.log`, `installed-profile-audit.json`,
`catch-sync-inputs.json`, `catch-sync-gameover-before-controls.jpg`,
`catch-controls-deploy.json`, `catch-fixed-inputs.json`,
`catch-fixed-score-22.jpg`, `catch-fixed-short-start.jpg`,
`catch-fixed-stick-{left,right}.jpg` and `catch-sync-audio.{wav,json}`.

Fresh-launch movement evidence: `catch-fixed-fresh-{right,left}.jpg`.
Earlier files named `catch-fixed-exit-browser.jpg` and
`catch-fixed-second-exit.jpg` captured the pending pause-menu confirmation,
so they are not browser-return evidence.

An additional October 26 exit on the same build unexpectedly launched 2048
instead of remaining in the list (`catch-extra-unexpected-2048.jpg`). The
retrieved `catch-extra-unexpected-2048.log` confirms Catch cleanup followed by
a 2048 load. Thus the earlier two successful returns do not establish reliable
menu handoff. This intermittent defect remains under investigation.

The separately deployed bounded-trace build (`26215225…`) then passed three
Catch exits and one Snake exit, including Snake followed by Catch. The retrieved
`catch-menu-handoff-trace.log` records neutral input at each of those exits.
It also records a transient A release/reappearance during one held launch
confirmation (158318–159284 ms), so a single observed release does not always
mean the KVM-held button has finished. The failing exit itself was not traced;
the cause remains unproven. Post-release browser captures are
`catch-trace-post-release.jpg`, `catch-trace2-post-release.jpg` and
`catch-trace3-post-release.jpg`.

## Special-apple scoring repair, October 28

[superd_1's original game](https://scratch.mit.edu/projects/124652800/)
awards +1 for red, +2 for green and −2 for brown apples. The latter two sprites
are named `Sprite1` and `Sprite3`. Their separate movement and scoring scripts
both test the basket. Movement can hide an apple at contact before the scoring
script runs, leaving the score unchanged. Two normal Xbox brown contacts
reproduced this: **4 → 4** and **6 → 6**. An isolated green catch passed
**1 → 3**, so a successful catch does not rule out the race.

`scripts/prepare-catch-apples.py ORIGINAL.sb2 NEW.sb2` creates a separate
prepared copy. Each special apple now checks contact, plays its existing cue,
changes Score once and repositions in its movement script. The old scoring
forever loop is removed; its Green Flag score reset remains. A missed apple
still hides for five seconds before returning. Fall speeds, score values,
sounds, all 13 asset files, credits and other sprites are unchanged. This is a
**game-script repair**, with no runtime or Xbox collision-rule change.

The original archive is
`dfdc129664dff3a9b65f1c3523ba5d05f162e0b198b474cccc2cfd58cf7c1ede`;
the prepared archive is
`7d3410d7f6d88658523def105328b1c91d23f09094bef516ea4dfcab91d57ff8`.
Use the same controller sidecar next to the output archive. The script checks
the known original hash and refuses to overwrite an existing output.

The separate `Catch-Apples-Score-Test.sb2` entry passed full FTP readback and
normal-browser selection on diagnostics-off XBE `ac3142d7…`, physical 128MB
Xbox. Paired original HDMI frames show brown catches **7 → 5** and
**22 → 20**, plus a green catch **15 → 17**, with other fruit away from the basket. These checks used
ordinary controller input, without debugger or game-state writes. The timed
round ended normally at Score 22 / Timer 0 with the full Game Over message.
A 400 ms Start replay restored Score 0 (observed at Timer 27), and renewed
Right moved the bowl from the left edge to the middle.

`python3 tests/catch_apples_scoring_test.py` reproduces the original race in
both script orders, then checks +2/−2 exactly once, no hidden-apple award,
miss cooldown, replay reset and preserved metadata by executing the SB2
control flow. This small semantic harness complements the actual hardware
checks; it is not a test of the full runtime scheduler.

Local evidence is under `build-xbox/hardware/`: the
`catch-special-physical-verification-20261028.json` audit, the
`catch-prepared-{brown1,brown2,green1}-20261028-frames/` raw frames, and
`catch-scoring-deploy-20261028/receipt.json`. Earlier helper attempts that
confused grass or a clipped basket with an apple, or stopped before contact,
are retained and excluded. Audio listening and the intermittent browser
handoff remain separate open checks.

After those checks, the prepared copy replaced the regular
`E:/ScratchEverywhere/Catch-Apples-superd1.sb2` entry. The original is preserved
as `catch-original-dfdc-20261028.fixture`. Temporary upload, installed archive,
rollback original, unchanged controls and unchanged normal XBE all passed full
FTP readback. The separate Score-Test entry and its sidecar were removed after
readback; they do not increase the 21-game count. Deployment evidence is
`build-xbox/hardware/catch-scoring-promote-20261028/receipt.json`; the saved
native log also confirms the test entry's load, cleanup and browser return.

A fresh normal-browser launch of the regular filename then repeated the brown
penalty **4 → 2**, with the red apples away from the basket. Return to game
list also passed with A held for 1.2 seconds, leaving 2048 selected in the
browser without launching it. Original frames are
`catch-canonical-brown1-20261028-frames/` and
`catch-canonical-final-browser-20261028.jpg`. These two successful exits do
not establish that the earlier intermittent handoff defect is fixed.

## Current main, native hardware follow-up — October 29

Normal diagnostics-off main build `207edc25…` now has a physical NV2A result on
the 128 MB Xbox: normal browser selection, Score 13 / Timer 0 Game Over, short
Start replay to 0/30, recorded D-pad Right and Left with renewed scoring, Back
pause, and one clean held-confirmation Exit. The original 148-frame replay clip
spans 6.82 seconds; it is not a game-FPS measurement. A separate Left press
after expiry is excluded. Repeated handoff and audio acceptance remain open.

See the [backend/startup evidence and limits](xbox-native-hardware-followup.md).
A separate framebuffer-initialization experiment was discarded; this result
uses unchanged main, and does not close the 21-game hardware goal.
