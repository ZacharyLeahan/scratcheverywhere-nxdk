# Streaming audio continuity

The mixer previously decoded `floor(outputFrames * step) + 2` source frames per
callback, then restarted interpolation at zero on the next callback. It
discarded both lookahead samples and fractional position. At 22050 Hz into 48000
Hz with 1024-frame callbacks, that consumed 472 source frames for about 470.4
frames of output. The gaps accumulate and create callback-boundary
discontinuities. The final partial callback could also read past the valid
decoded data.

Each SoundStream now retains decoded lookahead and fractional position in an
AudioResampler. Only consumed whole frames are removed. Interpolation stops at
decoder EOF, preserves the final sample for interpolation, and leaves the
remaining output untouched for other streams. Short decoder reads are filled
until the required lookahead or EOF. Stream initialization resets this state;
pitch changes retain the current position. Volume, pan and summing stay in the
shared mixer. This change applies to all platforms using that mixer.

## Checks

`python3 tests/audio_resampler_test.py` runs ASan/UBSan against direct
interpolation for 160 rate/channel/callback-size/short-read combinations, empty
and short EOF, additive gains, pitch changes and reset. It also checks a
simulated minute of mono 22050-to-48000 playback. These passed, and the NXDK
build succeeded.

`python3 examples/make-audio-resampler-test.py OUTPUT.sb2` makes a deterministic
two-second mono 22050 Hz signal with no third-party assets. A starts playback at
volume 50; Finished becomes 1 after play-until-done returns. In isolated xemu,
GDB captured the actual Xbox executable's PCM immediately after
Mixer::requestSound and before SDL_PutAudioStreamData. Build `cf887b1d…`
produced 48,128 frames matching continuous interpolation: correlation
0.9999999889, maximum error 0.99988 PCM16 units, identical left/right channels.
Finished reached 1. A second playback produced byte-identical captured PCM. This
verifies many callback boundaries, EOF completion and replay reset; it does not
establish audible quality or performance on hardware.

The prior Retro Racing capture matches an offline simulation of the old
callback-reset algorithm at correlation 0.99999999997. A later whole-game
capture could not be matched to one uninterrupted source clip. Its initial acc1
segment matches the new continuous interpolation, but the game can schedule
further clips; that mixed capture is not the continuity acceptance test. The
deterministic single-sound fixture supplies that check.

Evidence is under ignored `build-xbox/retro-racing/`: the original
`buffer-boundary-observation.json`, and `resampler/fixture-continuity.json`,
`fixture-{start,finished}.png`, `fixture-pcm.wav`, `fixture-replay-pcm.wav` and
`fixture-replay-comparison.json`. GDB tapping affects timing. Generic QEMU
wavcapture yielded silence because xemu's APU monitor uses its direct SDL audio
stream; that capture was rejected, not treated as a game failure.

The audio build was installed separately at
`F:/scratch-audio-20261026/default.xbe`, with full FTP readback verification. On
the physical Xbox, the fixture's sound completed and Finished reached 1. Both
initial playback and replay completed. Their eight-second HDMI recordings
contain the full two-second signal, each matching the continuous source at
correlation 0.9999996 without clipping. Evidence: ignored
`build-xbox/hardware/audio-fixture-hardware-continuity.json`, the two WAVs and
`audio-fixture-first-finished.jpg`. The earlier hardware Retro Racing checks
used build `242d1c78…` without this change; the audio build also passes physical
Retro Racing launch, acceleration to 100 MPH, authored Y pause/resume and
runtime Green Flag replay. Two bounded driving attempts progressed around the
opening bend and later sections; neither established a completed lap. Full-game
and long-run audio qualification remain open.

After the physical checks, Retro Racing exited to the game list and the
controller combo returned to XBMC. The final log was retrieved. The temporary
fixture and profile were retained under `.fixture` extensions, removing their
entry from the game browser. The dashboard launcher was not replaced.

## Capture transport limits — October 27

Appel's later normal build (`98c93665…`, profiling OFF) ran continuously at
checkpoint three during a four-minute HDMI recording, without runtime menu
pauses or controller input. The exact 240-second PCM file took 258.26 seconds
of wall time to receive. The KVM's own stream log reports 875,040 missing frames
between transmitted blocks: **18.23 seconds at 48 kHz**, accounting for the
extra recording time within 30 ms. Its I2S overrun counter stayed zero; the
stream's queue-loss and gap counters are separate from that producer counter.

Forty-three of 49 sampled one-second windows match the unchanged music source
at correlation >= 0.9. Their source offsets contain jumps, consistent with the
recorded transport loss. This recording cannot establish uninterrupted Xbox
playback or subjective sound quality. Earlier captures with runtime pauses
also cannot certify a gapless authored music loop: the playing sound can end
while scripts are paused and restart when scripts resume.

Local evidence is under ignored `build-xbox/hardware/`:
`appel-normal98-active-loop-audio3{.wav,.json,-continuity.json}`,
`-kvm-end.log`, `-transport-analysis.json`, and the 1,611 original JPEGs in its
frame-history manifest. No KVM firmware or persistent settings were changed.

A second 240-second recording closed the MJPEG viewer and sent no controller
input. It took 248.43 seconds; the KVM logged 402,960 gap frames (**8.395
seconds**), again with zero I2S overruns. Removing video reduced losses in this
bounded comparison but did not eliminate them. Evidence is
`appel-normal98-audio-only4{.wav,.json,-continuity.json,-kvm-end.log}` and
`-transport-analysis.json`. The before/after console images show Appel still
active at checkpoint three with eighteen apples; it was then paused safely.
The user subsequently listened directly to the TV and confirmed clean Appel
music without crackles or dropouts in this normal-build session. That passes
the subjective listening check for this session; it does not make the KVM
files gapless or qualify other games. The response is retained in
`appel-normal98-tv-listening-confirmation.json`. Loss-accounted long-run audio
continuity verification remains open. The local recorder also reported that its
current mode needs H.264; no codec setting was changed for these tests.
