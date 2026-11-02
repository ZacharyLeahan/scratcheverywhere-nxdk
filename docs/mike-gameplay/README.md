# Xbox gameplay clips

These GIFs come from the physical 128MB Original Xbox's HDMI output, captured
through the user's KVM. They contain no xemu, browser-game or generated frames.
Some use earlier timestamped test footage; the others were recorded for this
recap. Each clip is one continuous interval, kept at its recorded pace,
resampled to 10 fps and scaled to 480 × 320 with a 128-color GIF palette.
GIFs are silent and repeat from the beginning.

The [original clips manifest](manifest.json) and [nine-game manifest](pack30-provenance.json) record capture time, duration,
source-image hashes and output hash. Original JPEGs, detailed timestamps and
controller traces remain local in ignored `build-xbox/hardware/`,
`build-xbox/game21/`, and the ESP-KVM checkout’s `observations/`. The Spider Adventure clip uses the saved October 27
physical recording, seconds 7–19; its original relative timestamps preserve
capture gaps. An exact absolute start time was not recorded. Short clips
illustrate gameplay; the accompanying milestones may come from longer tests.
The Beach Volleyball clip uses a continuous November 1 hardware interval;
two stream warm-up/cache frames are excluded before sampling. It demonstrates
CPU gameplay, not independent two-player support or a measured frame rate.
See the [recap](../xbox-handoff-for-mike.md) for game credits/source links and
the [qualification matrix](../xbox-game-qualification.md) for limits.

The Level EATEN clip uses November 2 ordinary-build footage of movement and Y reset
on earned Level 3. The longer hardware test cleared Levels 1–2 without gameplay
seeding; the GIF illustrates the resulting level and reset, rather than the full clear.

The Fireboy clip uses November 2 ordinary-build Xbox footage of the final blue
gem and both exits, followed by the Level 1 results. The saved longer run collects
all seven gems; the time medal is missed during inspection. It is a 6.1-second
continuous interval at recorded pace, not a performance measurement.
