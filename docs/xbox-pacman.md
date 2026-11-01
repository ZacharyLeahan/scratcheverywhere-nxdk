# PacMan hardware qualification

The cdaniels7088 project uses four arrow directions, mapped to the Xbox D-pad
and left stick. It has no authored sound playback. Earlier work repaired its
Game Over name handling; power-pellet scoring and frightened costumes now pass. Eating a frightened
ghost and a complete board remain unverified on physical hardware; the separate
native emulator result below closes those emulator checks.

## Combined pen/exact-pixel engine regression, October 27

Normal candidate `b75e9beb` selected and launched PacMan from the browser.
Holding Up at the initial corridor left the player below the cage wall at
Score 0 while ghosts continued moving. Right collected pellets for Score 20;
Up turned into the next corridor for 40, then Left reached 70. A later original
capture shows 80, followed by a visible natural Game Over. Short Start replay
restored Score 0 and the initial player position, and another Right hold
scored 20. Exit returned to the populated game list.

A fresh browser selection and launch again started at zero. Left moved through
the opening corridor and scored 20; a second Exit returned to the populated
browser. These checks used only HDMI observation
and ordinary controller reports; no debugger, watch state or game-state writes
were used.

A host helper's attempted upper-left bonus route failed. Its global yellow
bounding box included disconnected image noise and later the large yellow
Game Over illustration, so its reported waypoint positions are excluded.
Neither a bonus collection nor frightened/eaten ghosts is established by that
attempt. A replacement connected-component detector requires one player-sized
shape and rejects the ending illustration; six stored-image checks pass, but
that is host-detector validation, not new gameplay evidence.

Ignored evidence is in `hardware/pen-regression-pacman-*.jpg`, the associated
controller reports, `pen-regression-pacman-verification.json`,
`pen-regression-pacman-power-excluded.json` and
`pacman-connected-detector-check.json`. The shared intermittent KVM delivery
issue remains open.


## Power pellet on normal Xbox, October 28

On diagnostics-off `ac3142d7…`, ordinary P3 controller input reached the
upper-left power pellet. The native score changed **100 → 200**, the large
pellet disappeared, and both previously red/cyan ghosts visibly turned blue.
The original project and runtime were unchanged; this test used HDMI pixels
and controller reports, without debugger or game-state writes.

The original maze requires a detour around the lower vertical wall. In video
coordinates, the successful route continued from `(279,253)` through
`(279,210)`, `(225,210)`, `(225,85)`, `(135,85)` to the pellet at `(135,40)`.
A preceding attempt to go directly from the starting corridor to X=225 stopped
at X=279 with Score 20: that was a real wall, not a runtime movement failure.
The first short-B resume attempt had not visibly left the pause menu and is
also excluded. The connected detector rejected both menu and ending artwork.

Original before/after frames are
`build-xbox/hardware/pacman-power-route3-20261028-frames/waypoint-3.jpg`
and `route-complete.jpg`. The folder retains the exact executed helpers;
`pacman-power-physical-verification-20261028.json` records the review and
hashes. The earlier globally thresholded route remains excluded. Eating a
frightened ghost and clearing all 92 dots/bonuses still need normal hardware
proof; a blue costume alone does not establish either result.

A subsequent continuous Green Flag run collected that pellet again (Score
190 with blue ghosts) and traversed the upper corridor to Score 250. By then
the ghosts had returned to normal costumes; the next contact ended the round.
Two other attempts ended earlier. These are ordinary loss/progression checks,
not ghost-eating passes. `pacman-power-hunt3-20261028-frames/` retains the
original frames and full controller/camera route. No project or runtime fix
was needed for the verified power-pellet behavior.

The final Exit returned to the populated browser. The homebrew controller
reset combo restored XBMC for log retrieval. Full FTP readback verified the
unchanged PacMan archive
`283feafd4c25cec72c09e9de3b76722aba3997c788342e340212f797fc7081d9`
and recorded its controls, while also rechecking the installed Catch repair,
rollback archive, normal `ac3142d7…` test executable and unchanged primary
`b75e9beb…` launcher. The native log records both game loads, cleanup and
browser returns without runtime errors. Evidence is
`build-xbox/hardware/pacman-followup-readback-20261028/receipt.json` and
`normal-log.txt`; `pacman-followup-browser-20261028.jpg` shows the final Exit.


## Native emulator full board — October 29, 2026

The unchanged original archive `283feafd…` and arrow-control profile `46c9f91e…`
complete one normal round on native `4ef49719…`, renderer/window 3/0, in private
Vulkan xemu 0.16.4. All **88 ordinary dots and four bonuses** disappear, Dots
reaches **92**, Score reaches **1,380**, and the settled display shows **You Won!**
Read-only observations guide ordinary emulated USB directions; there are no
game-state/RNG writes, gameplay edits, save-state restores or mid-round restarts.

Frightened ghost eating has separate evidence: adjacent observations show
Score **690 → 790** with Dots unchanged at 42, while blue Ghost2 becomes normal
and respawns at `(0,26)`. The four bonuses and 88 dots account for 1,280 points;
the eaten ghost accounts for the extra 100.

Short Start from both Win and a subsequently visible ordinary Game Over restores
all 92 collectibles, Score zero and working movement. A fresh browser selection
loads the actual PacMan archive and starts a new round. Two held-A Exits each
leave zero game sprites, the exact 21-game manifest and 42 browser buttons.
The snapshot guest closes after acknowledged quit; the saved HDD and all 41
manifest source files remain byte-identical. No runtime or project changes were
needed for this batch.

One scoring issue remains: the winning round has Score 1,380 but High Score
1,370, retained by Start. The original periodic high-score check and Win's
stop-all may explain the final ten-point gap, but its cause and comparison with
Scratch still need investigation. A fresh archive load restores its saved zero.
Do not count high-score correctness as passed.

The first normal round ends at 20/two dots. During the next, the host helper
stops at 60/six dots because its wall model and short-input observations are
inadequate. Ordinary corner probes reach 70/seven dots; corrected held-direction
observations then continue that same round to victory. These retained host
failures are not engine collision failures. The route includes observational
pauses and is not a continuous-play or FPS measurement.

The original has no authored sound-playback blocks; its 96 default pop sound
references remain present. An 8.021-second settled-Win APU recording is entirely
silent. That establishes only ending-screen silence, not active-play continuity
or TV audio quality.

Ignored evidence: `build-xbox/pacman-native-board-20261029/review.json`,
`attempt2-review.json`, `corner-direction-probes.json`,
`attempt2-continued-review.json`, `frightened-ghost-audit.json`,
`project-regressions.json`, `win-silence.json`, original screenshots and QMP logs.
Physical frightened-ghost/full-board/replay, native rendering, pacing and 64 MB
gates remain open. These emulator images do not satisfy the real-Xbox GIF request.

## Optional final high-score repair — October 30, 2026

The original updates High Score in a separate forever loop. Win and Game Over
stop every script, so the last score change can be missed. This is a
**prepared-project repair**, not an Xbox renderer or shared-runtime change.
[The preparation script](../scripts/prepare-pacman.py) updates the record before
each ending while preserving a higher existing record:

```sh
python3 scripts/prepare-pacman.py PacMan-cdaniels7088.sb2 PacMan-fixed.sb2
```

The tool requires the original `283feafd…` archive and refuses to overwrite
an existing output. Only two guards in the stage's ending handlers are added;
all assets, credits, controls and other project data are preserved. A separately
named test copy needs the existing arrow-control sidecar copied to its new
archive name, e.g. `PacMan-fixed.sb2.json`. This does not add disk persistence
for High Score.

On normal current-main XBE `eb3492c2…`, native renderer/window 3/0, paired
**diagnostic ending fixtures** reproduce original Win **1,380 / 1,370** and show
prepared Win **1,380 / 1,380**. Loss **80 / 70 → 80 / 80** and preservation of a
higher record (**80 / 200**) also pass: six runtime cases plus twelve host cases.
These fixtures preset scores and disable other project threads to isolate the
ending handlers; they are not natural board clears or real-Xbox evidence.

The full prepared archive `fc4cea990e6a99978a4aaac3f2ad7d5b0a028b5807e2e937f00c4f4786188487`
also passes three fresh DVD loads, ordinary USB Right movement/pellet collection
and three clean browser returns. A normal Right → Up route reaches natural
Game Over at Score 20. Short Start restores Score/Dots zero, retains High Score
20, and renewed Right collects two dots for Score 20. Read-only debugger
observations verify these values; only the initial DVD path/backend are selected
in the debugger. No mid-round score, position, RNG or thread-state writes are
used in these full-project checks.

The prepared archive has not been uploaded to the physical Xbox. Installation, a natural full
board on the prepared copy, physical win/loss/replay and audio/performance gates
remain open. Ignored evidence is under
`build-xbox/native-qualification-20261030/`: `pacman-archive-audit.json`,
`pacman-ending-probes/review.json`, the three normal-copy reviews, screenshots,
QMP/GDB journals and `final-review.json`.
