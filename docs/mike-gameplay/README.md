# Xbox gameplay clips

These GIFs come from the physical 128MB Original Xbox's HDMI output, captured
through the user's KVM. They contain no xemu, browser-game or generated frames.
Some use earlier timestamped test footage; the others were recorded for this
recap. Each clip is one continuous interval, kept at its recorded pace,
resampled to 10 fps and scaled to 480 × 320 with a 128-color GIF palette.
GIFs are silent and repeat from the beginning.

The [manifest](manifest.json) records each clip's capture time, duration,
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
