# Space Invaders on Xbox

[RokCoder's game](https://scratch.mit.edu/projects/253610111/) uses Left/Right
and Space. The Xbox sidecar maps D-pad/stick steering and A to start/fire.
Release A after starting so the title's press/release sequence can finish.

## Normal hardware follow-up, October 28

The diagnostics-off `ac3142d7…` executable ran the unchanged archive
`09e3816b18a66a34bd9b696442ae0ec8eba340ef994f6793c9a987160bbc0753`
on the physical 128MB Xbox. Directed controller play demonstrated firing through
damaged shields, alien removal, saucer scoring, life loss and natural endings.
Manually reviewed ending frames show scores **260** and **1,230** in separate
rounds. The project returned to the populated browser after testing. Full FTP
readback later confirmed both the archive and normal executable identities.

A full wave is **still open**. The original has 55 aliens; their points total
990, but saucer bonuses can push a partial wave above that score. Neither 990
nor 1,230 proves a clear. The captures do not show the remaining aliens cleared
and a new group of 55 appearing with the score retained. Several camera-guided
attempts ended in losses; one stopped safely when video became stale. A trial
HUD reader misread a known 260 score and was excluded as a verification gate.

A 120-second HDMI recording contains 5,760,000 stereo frames at 48 kHz,
peak 0.0752 and RMS 0.0101. Capture wall time was 122.58 seconds. It includes
active play and ending footage; this is evidence of audio signal, not 120
uninterrupted seconds of gameplay or a subjective sound-quality pass.

Local evidence: `build-xbox/hardware/space-wave-attempt1-20261028-frames/`
and the guided-run frame folders retain original JPEGs and executed helpers;
`space-first-ending-score-detail-20261028.png` shows 260,
`space-edge-column-title-ready-20261028.jpg` shows 1,230, and
`space-wave-round2-audio-20261028.json` records capture accounting.
`catch-scoring-deploy-20261028/receipt.json` contains the subsequent full
readbacks; its saved `debug.txt` records Space Invaders loading and cleanup.
No Space Invaders scripts or runtime behavior changed for these tests.

## Native emulator full wave — October 29, 2026

The unchanged original archive `09e3816b...` now clears a complete wave on
native `4ef49719...`, renderer/window 3/0, in private 128 MB Vulkan xemu.
Normal browser selection and actual emulated USB Left/Right/A play produce
**55 → 0 → a fresh 55 invaders, Score 990, all three lives**. Every remaining
count from 55 through zero is observed; score never resets and Game Over
stays false. The wave initializer's `drops to land` changes from 9 to 8.
A settled capture independently shows all 55 new invaders and the retained
990/three-life HUD. This is a wave transition, not a score-only inference.

Read-only state guides the host controller helper. It clears the leftmost
column before moving on, then times shots from a fixed lane. Three earlier
normal losses at 940/two remaining, 850/seven and 920/three are retained.
They exposed host aiming mistakes: switching columns left distant edge aliens
alive, and the final three moved once per roughly two bullet updates rather
than the helper's assumed one. Only host planning changed. Original scripts/assets are untouched; no gameplay
state or RNG writes, physics edits, input-poll bypasses or mid-round restarts
are used.
The winning round starts with a normal A replay from loss at zero/55/three.

An uninterrupted 1,200-video-frame follow-up advances wave two to Score 1,370,
31 invaders and two lives, with the base normally respawned and no Game Over.
Its 20.037-second APU recording is unclipped. Whole-source correlations are
0.999845/0.999746 for movement effects one/four and 0.982523 for shooting,
without pitch or time warping. Overlapping/unheard cues and silent blocks are
not individually qualified; this is not complete continuity or TV listening
acceptance.

Green Flag returns to the title at zero; A starts a new 55-alien/three-life
round, with Right/Left/fire working again. Two held-confirmation Exits return
to all 21 projects/42 buttons with zero game sprites. Between them, a fresh
browser selection loads the actual Space Invaders archive, starts another
normal round and accepts Right/fire. Observer addresses are refreshed after
reload rather than reading the previous project's freed objects.

Ignored evidence is under `build-xbox/space-native-fullwave-20261029/`:
`review.json`, `fullwave-audit.json`, the four original attempt logs/captures,
`wave2-confirmed.png`, `wave2-audio{,-match}.json` and `project-regressions.json`.
The guest closes cleanly and the shared HDD, game and control profile remain
unchanged. No executable or project is installed on the physical console in
this batch. Hardware full-wave, subjective/long-run audio, pacing and retail
64 MB qualification remain open.
