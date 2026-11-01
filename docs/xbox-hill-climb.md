# Hill Climb Racing: Xbox controls and fuel checks

Source: [Hill Climb Racing v1.0 by griffpatch](https://scratch.mit.edu/projects/56667360/).
The unchanged original SB2 SHA-256 is
`cc0d6c7b1523abfd58403cce174c0fd16c473b580437cf425bdd75490da3f03a`.
These October 28 checks used normal diagnostics-off XBE `ac3142d7…` on the
physical 128 MB Xbox, with HDMI observations and Player Three controller input.

Right accelerates; Left brakes/reverses and affects attitude in the air.
A replays after an ending, X changes vehicle, Black/R restarts an active round,
and Y is the authored pause toggle. Back opens the runtime menu.

## Newly verified

- **Y pause/resume:** at Score 140, the scene, car and fuel bar remained unchanged
  while Right was held for two seconds. The two paused JPEGs are byte-identical.
  Y resumed gameplay; renewed Right advanced the terrain and score to 420.
- **Fuel can:** a later jeep run approached the visible red can at Score 420.
  After Y-resume/Right/Y-pause, the gauge increased from 94 to 134 green columns
  in its 135-column interior. There was no restart between those captures.
  The visible result is Score 900 with a +200 airtime bonus.
- A late Left input did not recover the near-vertical jeep. The authored neck-break
  message appeared, and Back/Exit returned cleanly to the populated browser.
  This is a loss/exit check; precise air braking remains unqualified.

A preliminary attempt sent Black after an Out of Fuel ending and did not
restart it. A replay was then used, consistent with the controls above.

Earlier tests established motorcycle play, fuel exhaustion, vehicle switching,
active Black restart, replay, repeated launches/exits and HDMI audio signal.
Extended terrain, precise brake/air control and subjective/long-run sound remain
open in the [21-game matrix](xbox-game-qualification.md).

Ignored evidence: `build-xbox/hardware/hill-followup-physical-verification-20261028.json`,
`hill-first-fuel-bar-audit-20261028.json`, the corresponding frame directories,
original pause/fuel/loss/browser JPEGs and the controller receipt. Archive and
normal-XBE identities were checked by full FTP readback after the test batch.
