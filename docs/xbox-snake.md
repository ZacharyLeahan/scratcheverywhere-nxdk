# Snake controller and gameplay checks

NemoNaturally's Snake was tested through the normal Xbox project browser on
synchronized build `be4bc0b4…`, installed separately in
`F:/scratch-sync-20261026/default.xbe`. The build passed FTP readback
verification. The game archive was not modified for these tests. Its installed
SHA-256 is `efd37742f496c4ad6e8baabac6d2ed0396def2f029de144e343f871340af7982`;
the installed profile SHA-256 is
`8f4aa042e9166fcf37f512779eefc9bcd2317ac7f60b3d39e4177c4e286f791b`.

## Physical Xbox, October 26

A bounded D-pad run lasted approximately 21 seconds and used all four
directions. The snake grew, collected points, and subsequently reached the
complete loss screen with **Score 125**. The downloaded project's existing
Highscore 2000 remained visible; that is not a result from this test.

Runtime pause and Green Flag replay produced a later loss screen with Score 0.
Exit returned to the populated browser after a 2.2-second A confirmation was
released. Selecting Snake again started a fresh game. Separate captures show Up, Left, Down and
Right moving the head during this fresh launch, followed by a second successful
exit to the game list. The prior up/down steering failure was not reproduced. An
eight-second HDMI capture contains non-clipping audio: peak 0.12561, RMS
0.012573. Subjective and long-run audio are not established by that sample.

The scoring run's temporary vision helper eventually confused the growing gray
snake/body with other gray objects. Its automatic "Game Over" message was
premature. The later actual Score 125 screen supplies the loss/scoring evidence.
The final tracking coordinates are not accepted as accurate head positions. The
fresh-launch directional captures independently establish all four D-pad
directions.

## Controls and remaining checks

Use the D-pad or the installed WASD-bound left stick. Hold Start for the runtime
menu, select Green Flag to replay, or Exit Project to return to the list. This
project's ending stops other scripts rather than using Scratch's global stop-all
state, so the runtime's short-Start stopped-project replay shortcut does not
apply. Green Flag replay is verified.

Explicit tail self-collision, clock/blade pickup behavior and longer audio/play
sessions remain unverified. The earlier input trace established the four stick
directions; the current run provides clean D-pad gameplay evidence. This is not
a full-board completion claim.

Evidence is under ignored `build-xbox/hardware/`: `snake-sync-score-125.jpg`,
`snake-sync-replay-score-zero.jpg`,
`snake-sync-fresh-{up,left,down,right}.jpg`,
`snake-sync-audio.{wav,json}`, `snake-auto2-inputs.json` and its intermediate
captures. A screenshot named `snake-sync-replay-active.jpg` still shows the menu
transition and is not used as evidence of active gameplay.

An additional fresh launch/exit captured the populated list after A release in
`snake-sync-post-release-browser.jpg`. Earlier files named
`snake-sync-exit-browser.jpg` and `snake-sync-second-exit.jpg` captured the
pending pause-menu confirmation; they are not browser-return evidence.

The final retrieved runtime log confirms profile loading, project cleanup and
browser return (`frog-snake-catch-controls.log`).

## Clock and ending audio — October 28, 2026

A normal diagnostics-off `ac3142d7…` run on the physical Xbox collected fruit,
grew the tail and visibly picked up a clock. Original HDMI frames show the clock
at approximately (342, 208), the head approaching from the left, its disappearance
and continued upward movement. The authored movement delay changes from 0.125 to
0.25 seconds. Median observed cell intervals increased from 0.153 to 0.291 seconds
(about 1.90×); these are video receive times, not precise simulation timing.
The four-second restoration under uninterrupted play remains unverified.

The planner reads HDMI pixels only. Static project inspection confirms movement
in 24-unit steps and the authored head X offset of −12; screen steps are 36×32
pixels. One tail corner falsely matched the head at run second 23.358. That raw
sample is retained and excluded from the interval calculation; the original
clock/approach/after frames were independently viewed.

A continuation reached the ordinary boundary loss at **Score 175**. Later
Green Flag replays included a Score 0 boundary ending. These are not tail
self-collision passes. One helper incorrectly released direction after leaving
its artificial safety bounds; another lost head confidence. Those attempts and
their receipts remain separate from accepted gameplay evidence. Blade pickup
and explicit self-collision remain open.

A separate 60-second HDMI capture contains the tail of the authored Game Over
cue after a Score 0 ending, followed by digital silence from capture second 8.
The first five one-second probes match original source offsets 0.875875 through
4.875875 seconds with correlations 0.99666–1.00000. It contains exactly 2,880,000
stereo frames at 48 kHz, peak 0.03644, without clipping; receipt time is 60.77
seconds. It is not an active gameplay minute or a subjective listening pass.

Ignored evidence: `build-xbox/hardware/snake-clock-physical-audit-20261028.json`,
`snake-grid-attempt1-20261028-{result,client}.json` and its original frames;
`snake-grid-resume2-20261028-frames/ending.jpg`; the separately retained
`snake-grid-fresh{3,4}-20261028*` failures; and
`snake-grid-long-audio-20261028.{wav,json}` with
`snake-ending-audio-match-20261028.json`. The installed original archive and
normal executable passed full FTP readbacks after this batch.

## Blade, clock restoration and tail collision — October 29, 2026

The existing normal SDL texture-retirement build `78cb682a…` passed three
additional checks on the physical 128 MB Xbox with the unchanged archive and
profile. Input came through Player One; observations used HDMI only.

- **Blade:** the head entered the visible blade cell, the blade disappeared,
  one body segment was removed, and steering continued.
- **Clock:** an ordinary pickup slowed movement, then normal speed returned
  during uninterrupted play. Median observed one-cell intervals were 0.155 s
  before, 0.287 s while slowed, and 0.150 s afterward (22, 12 and 16 samples).
  Original JPEG hashes match the frame receipt timestamps. The return occurs
  approximately four active seconds after pickup, consistent with the authored
  timer. These receive-time measurements are not exact simulation timing or FPS.
- **Tail collision:** the snake reached a visible U-shaped enclosure near the
  center of the board, with its next downward cell occupied by its own tail.
  After a runtime pause, B alone resumed movement and Game Over appeared at
  **Score 225**. This identifies self-collision from the visible position,
  occupied next cell and immediate ending far from a boundary; the recording
  jumps from the menu to the ending and does not contain an individual contact
  frame. The downloaded Highscore 2000 remains unrelated to these test scores.

A short confirmation returned to the populated browser. A fresh browser launch
and Green Flag replay restored the short snake and renewed Up/Left steering.
The second Exit was not accepted: the confirmation missed, and its retry found
all four KVM controller adapters stale. Earlier failed observer tracking,
short-tail loops and a separate boundary loss at 125 are retained and excluded
from the self-collision result. The adapters required two physical reconnects;
no firmware, network settings, game archive or executable changed.

Subjective listening and extended active-game audio remain open. This batch
qualifies the legacy renderer build, not the draft native NV2A candidate.
Evidence: ignored `build-xbox/hardware/snake-reconnected-20261029/review.json`,
`clock-raw-cadence-audit.json`, the `blade-video`, `restored2-video`,
`tail-contact-video` and `fresh-replay-video` original frames/receipts, and the
linked controller traces. The initial contact-sheet time labels used an offset
origin; corrected clock sheet v2 and original frame timestamps are authoritative.
