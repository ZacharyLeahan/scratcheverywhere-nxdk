# Zach's Spider Adventure — game 21

[Scratch project 1396458859](https://scratch.mit.edu/projects/1396458859/) by
zacharyleahan, installed October 27, 2026. The project describes jumping on red
spiders, chaining stomps for combo scores, and defeating ten spiders on each of
ten levels. This installation keeps the original project JSON and all 125
assets unchanged; the only addition is an Xbox controller sidecar.

## Xbox controls

- D-pad or left stick Left/Right: move.
- A, D-pad Up, or left stick Up: jump.
- Y: restart (the game's on-screen R prompt).
- Back / Select: shared runtime pause, including Return to game list.

The installed files are `E:\ScratchEverywhere\Zachs-Spider-Adventure.sb3` and
`Zachs-Spider-Adventure.sb3.json`. The archive SHA-256 is
`4d70968739e9aafe19660baed7eb12f153d58189760d37559eafaae1b6fe972c`;
the controller sidecar is checked in as
`examples/spider-adventure-xbox-controls.json`. Both passed full temporary and
final FTP readback. The directory now contains 21 games plus the three existing
Xbox/regression test projects; test fixtures do not count as games.

## Hardware checks

Tested on the 128MB Xbox using the diagnostics-off shared-pointer-help build at
`F:\scratch-pointer-help-20261027\default.xbe` (SHA-256
`98c93665e87f51ce9b503c876b0301155e07084922bb1588dcd777bbbfca807e`).
Normal game-list launch, D-pad movement and A jumping produced actual stomps,
combo scores, and automatic level transitions. Controller play reached Level 6,
Score 7,516, Best combo 6, then the authored GAME OVER screen. This is a gameplay
check, not a complete ten-level victory pass. Y restarted after Game Over;
left-stick movement and jumping worked in the new round. Back / Select opened
the pause menu with shared mouse help, and Return to game list reached the
normal populated browser. A confirmed second browser launch reached Level 1
again; Y reset the round and Back / Select paused it for handoff. One short KVM
A confirmation was missed during browser testing; a neutral interval followed
by a 700 ms press launched successfully. This remains consistent with the
existing KVM delivery limitation, not a demonstrated game script fault.

A 30-second KVM video and 15-second HDMI audio sample are retained under ignored
`build-xbox/game21/`. Audio contained a non-clipping signal (peak 0.09534,
14.99 seconds captured); subjective listening and longer stability remain open.
KVM video is a visual record, not a game frame-rate benchmark.

Original metadata, source JSON, asset cache, hashes, installation receipts and
recordings live under `build-xbox/game21/`. No downloaded game assets are added
to Git.

## Native emulator full run — October 29, 2026

The unchanged original archive and controller profile now complete all ten
levels on native candidate `807d1928...` in private Vulkan xemu-macos v0.16.4,
using the normal browser and actual emulated USB controller path. Read-only
positions guide Left/Right/A; no game-state seed, physics edit, input-poll bypass
or mid-run restart is used. All 100 spiders are defeated, with ten confirmed
level completions, **Score 14,110 / Best combo 8 / one life**, and the authored
`won` state and YOU WIN screen. Life losses in levels seven and ten recover
normally; the next level restores two lives as authored.

Y from victory restores Level One, Score 0, ten spiders and two lives while
retaining High score 14,110. Walking and jumping resume, followed by a clean
browser return. Another normal browser launch repeats movement/jumping and
Exit. Read-only cleanup inspection finds zero game sprites and all 21 browser
entries, with renderer/window 3/0. An uninterrupted follow-up also reaches
natural Game Over and exits to the browser.

A separate uninterrupted 10.229-second APU recording has no clipped samples.
Whole-source waveform correlations are 0.99937 for the level announcement and
0.99968 for the hurt cue. The authored simultaneous hurt/Game Over mixture
matches at 0.99975; the last-stomp beep/win mixture across completion matches at
0.99996. These comparisons use full cues without pitch or time correction.
The paused controller run and its replay have weaker individual-cue matches
and are retained as limited evidence, not general sound-quality acceptance.
Not every authored sound is qualified.

Evidence is in ignored `build-xbox/spider-native-fullrun-20261029/review.json`,
its controller/read-only traces, completion audit, images and audio comparisons.
The guidance model is approximate and observations can stop between VM blocks;
this is not a per-frame physics-equivalence or frame-rate benchmark. The guest
exits cleanly with neutral controls and leaves the shared test disk unchanged.
**Physical ten-level victory, subjective/long-run audio and native Xbox
qualification remain open.** No installed Xbox files or firmware changed.
