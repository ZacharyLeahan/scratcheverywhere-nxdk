# Pack of 30: new-game checkpoint

November 1, 2026. These nine additions bring the installed list to **30**, not
30 qualified games. Original archives and controller profiles were uploaded and
fully read back. Three diagnostic projects were preserved as `.fixture` files.

| Project | Physical Xbox result / remaining work |
| --- | --- |
| [Beach Volleyball](https://scratch.mit.edu/projects/333452181/) | **B:** prepared Easy CPU mode, movement/jump, two points, natural 2–5 loss, Green Flag/X replay, clean browser return. Independent 2P, audio, smoothness and extended play pending. |
| [GlowBall](https://scratch.mit.edu/projects/112176502/) | **B:** prepared CPU mode, movement/jump, natural 2–5 loss, automatic title return/X replay, Green Flag replay and clean browser return on Xbox. Independent 2P, player win, audio/smoothness and extended play pending. |
| [Level EATEN!](https://scratch.mit.edu/projects/704676520/) | **C:** initial launch after Beach shows only blue; Green Flag restores scene. A later automatic launch succeeds. Walk/jump, two blocks eaten, fall/recovery, Y reset and browser return work. Investigate initialization and final-block eating with continued movement; finish level and qualify audio/smoothness. |
| [Fireboy and Watergirl](https://scratch.mit.edu/projects/571560558/) | **U:** gameplay, menus and independent character controls pending. |
| [Paint the Maze](https://scratch.mit.edu/projects/314731988/) | **U:** puzzle progression, reset/menu and replay pending. |
| [Candy Caves](https://scratch.mit.edu/projects/1385416673/) | **U:** menus, mining/combat, progression and loss/retry pending. |
| [Bouncy Heroes](https://scratch.mit.edu/projects/173918262/) | **U:** menus, movement/slam/dash, scored round and retry pending. |
| [Ninja Climb](https://scratch.mit.edu/projects/404349977/) | **C:** X starts; direction/A jump/X dash, natural death/recovery, Green Flag/X replay and browser return observed on Xbox. Opening section not cleared; sustained progression, audio/smoothness and stability pending. |
| [Mushroom Valley](https://scratch.mit.edu/projects/285730673/) | **B:** A charge/release clears two platforms, Score 2 and natural loss. Prepared copy adds A retry, confirmed fresh zero/alternate character and renewed jump, then browser return. Longer play, normal-build prepared-copy recheck and audio/smoothness pending. |

U means no hardware gameplay qualification. All nine original projects pass
native xemu browser selection, load, pause and Exit, restoring 30 entries each
time. This does not establish gameplay, audio or speed. Level EATEN! additionally
collects/grows from 100 to 200, resets and replays in xemu; physical growth and
level completion remain open.

## Reproduce the CPU-menu copies

[The preparer](../scripts/prepare-xbox-cpu-menu.py) adds one helper sprite, one
controls-hint SVG and a profile. Original targets, gameplay scripts, assets and
credits are preserved. It requires the expected authored CPU variables/broadcasts
and refuses existing output paths. Supply downloaded original `.sb3` archives:

```sh
python3 scripts/prepare-xbox-cpu-menu.py beach-volleyball Beach-Volleyball.sb3 prepared/Beach-Volleyball.sb3
python3 scripts/prepare-xbox-cpu-menu.py glowball GlowBall.sb3 prepared/GlowBall.sb3
```

Upload the prepared archive and its `.sb3.json` sidecar together. X starts CPU
(Easy for Beach), D-pad/stick moves and A jumps. Existing mouse menus remain.
For Beach's ending, use **Back → Click Green Flag → X**; short Start does not
restart this ending because the project has not stopped all scripts. Independent
simultaneous two-player input still needs backend/per-port binding work.

Both copies pass emulator CPU start, movement/jump, scoring, Green Flag replay
and browser return. Beach repeats those checks on the physical **128 MB Xbox**.
The tracked CLI reproduces the tested archives/profiles byte for byte and rejects
overwrite. Tested archive SHA-256 values:

- Beach: `599c658967cf9c43ff8da44488cdbef4fe67e47cbd2fa644b5632926c5571506`
- GlowBall: `15e46a265278580439978c38c4f3b7e8654b0661dc27833bd009c81b5b5c54cf`

Hardware executable: `84d60d948f23d265ad636ecc824e967dafb78a464723833ac137bd1a54c4af07`,
native NV2A/window/Xbox audio, based on the upstream 1.3 integration. This is a
separate test launcher. The older primary launcher is unchanged, and original
settings were restored after testing. No 64 MB, measured smoothness or audio
qualification is claimed. Detailed controller traces, live MJPEG evidence and
FTP receipts are retained privately in the shared ESP-KVM observations.

## Mushroom Valley controller retry

The original uses Space to jump but requires clicking its Retry icon after a
loss. [The preparer](../scripts/prepare-mushroom-valley.py) lets Space/A activate
that existing gate, preserves its restart sequence, physics, assets and mouse
control, and adds an ending-screen hint:

```sh
python3 scripts/prepare-mushroom-valley.py Mushroom-Valley.sb3 prepared/Mushroom-Valley.sb3
```

Upload the archive and `.sb3.json` sidecar together. The prepared archive hash is
`eba8ae08dcedd1e031f558f13bd8b7901ce42faf0f94afe38b11b34a51b8e883`.
The physical scored loss, A retry, renewed jump and browser return use separate
diagnostic executable `a57d47e0…`, with existing read-only UDP watch/pause logging.
Repeat the prepared-copy loop with ordinary `84d60d94…` before final acceptance.
The emulator also enters a fresh alternate-character round after A; its initial
fixed jump sequence did not establish a scored replay. The KVM currently reports
audio capture unavailable; that is not evidence of a game audio fault.
