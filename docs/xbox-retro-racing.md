# Retro Racing checks

Griffpatch's Retro Racing uses arrows for acceleration, braking/reverse and
steering; A/Space is the handbrake and Y/P is its authored pause control. The
installed profile also binds the left stick to arrows. Hold Start for the
runtime menu, whose Green Flag resets the race and Exit returns to the browser.

## Xbox executable in xemu

Build `242d1c78…` launched from the normal browser with the car, road, HUD and
map rendered. Acceleration reached 64 MPH, D-pad Right and left-stick Left
steered in opposite directions, and grass slowed the car. A braking reduced 39
MPH to 11. Green Flag restored zero speed/time. GDB counted 191 clones before
and after replay, then zero after exit. A fresh browser launch reached 40 MPH
and exited again. These emulator runs use the existing GDB-only network
initialization bypass. They do not measure console performance.

## Physical Xbox, October 26

The same `242d1c78…` build launched twice through the browser. Acceleration
reached 108 MPH; A braking reduced it to 27. D-pad Right changed the car/road
heading, and left-stick Left steered back. Off-road slowdown occurred. Green
Flag restarted the race, both held-confirmation exits returned to the populated
browser, and the Player One controller dashboard combo restored XBMC. The
retrieved log confirms both cleanups, browser activation and the dashboard
reset. An eight-second HDMI capture contains non-clipping engine audio.

After the [audio continuity repair](xbox-audio-resampling.md), build `cf887b1d…`
launched the game and reached 100 MPH. Its 8.09-second HDMI capture also
contains non-clipping audio. Y paused the authored game clock at 17.50 across
captures three seconds apart; Y resumed play and the clock advanced. Runtime
Green Flag then visibly restored 0 MPH and time 00:00.00.

Local evidence is in ignored `build-xbox/hardware/`, including
`retro-hardware-{start,speed,brake,right-turn,stick-left}.jpg`,
`retro-hardware-{exit-browser,second-speed,second-exit-browser}.jpg`,
`retro-hardware-audio.{wav,json}`, `breakout-retro-fixed.log`,
`retro-audio-build.{wav,json}`, `retro-audio-y-{pause,still-paused,resume}.jpg`
and `retro-audio-green-zero.jpg`. The Y-resume capture is taken while the button
remains held; subsequent live video establishes the advancing clock.

On hardware, full-lap completion, traffic visuals, deliberate drifting and
subjective/long-run audio remain unverified. Traffic collisions are not authored;
see the source audit below. Two bounded driving attempts advanced through
the opening bend and later track sections, then stopped when the road-following
helper lost sight of the road. No lap-completion result appeared. This is not a
complete game qualification.

After the driving attempts, runtime Exit returned to the populated browser. The
controller dashboard combo restored XBMC. The final retrieved log records
cleanup, browser activation and the reset. Evidence: ignored
`build-xbox/hardware/retro-audio-exit-browser.jpg` and `audio-fixed-final.log`.


## Current native emulator full lap — October 31, 2026

The unchanged [Retro Racing v0.8 project](https://scratch.mit.edu/projects/26999060/)
(`1d9ccc0a…`) completes one ordinary lap on normal main `eb3492c2…` in private
128 MB Vulkan xemu, with renderer/window `3/0`. Throttle, braking and steering
use actual emulated USB input; GDB exports a read-only state layout and QMP
observations guide the route. There are no gameplay-state/RNG writes, save-state
restores or mid-lap restarts.

The authored HUD displays **Last Lap 02:02.00**. Road distance passes 70,400,
the next-lap threshold becomes 140,800 and the new lap timer starts. The run
records 1,324 input/state observations with monotonically increasing distance,
peaks at 153 MPH, and includes visible traffic and three opponent passes in
read-only world coordinates. Off-road excursions are retained as part of the
ordinary run, not removed from its result.

Additional checks on that round pass:

- Y freezes distance, the lap clock and game tick across 180 video frames;
  a second Y resumes them.
- A + Right deliberately triggers `car_slide`, then throttle after release
  shows visible drift smoke with dust mode 2.
- Speed decreases on grass while Up remains held, without a brake input.
- Green Flag resets speed/distance, clears Last Lap and restores 00:00.00.
  Renewed throttle works, with the same 201 sprites / 191 clones after replay.
- Two held-A Exits return to zero game sprites and the exact 21-game/42-button
  browser. A fresh browser launch between them accelerates and brakes again.

The isolated guest closes and the shared base HDD hash is unchanged. This is
emulator gameplay evidence; it adds no physical-console, frame-rate or listening
acceptance. Private evidence is ignored `build-xbox/retro-native-fullrun-20261031/`:
`review.json`, `drive-observations.jsonl`, source-matched symbols, read-only GDB
layouts, QMP input journals, original PNGs and `review-contact-sheet.jpg`.

### Traffic mechanics

A whole-project script audit finds no object/color collision blocks. The other
car's script positions, scales and shows/hides it; speed-changing gameplay
blocks are in the player's key/off-road logic, with no traffic-contact handler.
The source also contains an unattached mouse-speed example, unused by these
controller tests. Traffic rendering/overtaking is meaningful to test; a traffic
crash is not an authored behavior to wait for. `collision-source-audit.json`
retains the inspected speed writers and `traffic-pass-audit.json` the ordinary
opponent passes. No game or engine change was made to create collision behavior.
