# Pack of 30: new-game checkpoint

November 1, 2026. These nine additions bring the installed list to **30**, not
30 qualified games. Original archives and controller profiles were uploaded and
fully read back. Three diagnostic projects were preserved as `.fixture` files.

| Project | Physical Xbox result / remaining work |
| --- | --- |
| [Beach Volleyball](https://scratch.mit.edu/projects/333452181/) | **B:** prepared Easy CPU mode, movement/jump, two points, natural 2–5 loss, Green Flag/X replay, clean browser return. Independent 2P, audio, smoothness and extended play pending. |
| [GlowBall](https://scratch.mit.edu/projects/112176502/) | **B:** prepared CPU mode, movement/jump, natural 2–5 loss, automatic title return/X replay, Green Flag replay and clean browser return on Xbox. Independent 2P, player win, audio/smoothness and extended play pending. |
| [Level EATEN!](https://scratch.mit.edu/projects/704676520/) | **C:** first level won naturally on diagnostic a57, advancing to Level 2; Green Flag replay, renewed movement and browser return. The last cube was resting on the player’s head: stepping aside lets it fall. No eating-runtime fix needed. Initial blue-only launch remains open; repeat win on ordinary build, later levels and audio/smoothness. |
| [Fireboy and Watergirl](https://scratch.mit.edu/projects/571560558/) | **C:** prepared level selector preserves locks; both characters move/jump on one controller. Natural hazard Game Over, Black/R retry and browser return. First-level gems/exit and independent two-pad input pending; compact hint is emulator-only so far. |
| [Paint the Maze](https://scratch.mit.edu/projects/314731988/) | **U:** Xbox gameplay pending. Prepared A Play/B Home/Y Reset clears puzzles 1–3 naturally in native xemu; Level 4 reset/Home/resume and browser return pass. Save/load, physical play and audio/smoothness pending. |
| [Candy Caves](https://scratch.mit.edu/projects/1385416673/) | **D:** original menus work, but level loading stops responding on Xbox and xemu. Prepared clone-initialization repair loads, mines, earns candy and reaches Game Over in xemu; hardware retest pending. |
| [Bouncy Heroes](https://scratch.mit.edu/projects/173918262/) | **B:** controller dash/slam, Score 10/four coins, natural Game Over, A menu/replay, renewed controls and browser return on diagnostic a57. Ordinary-build repeat, character/menu coverage and audio/smoothness pending. |
| [Ninja Climb](https://scratch.mit.edu/projects/404349977/) | **C:** X starts; direction/A jump/X dash, natural death/recovery, Green Flag/X replay and browser return observed on Xbox. Opening section not cleared; sustained progression, audio/smoothness and stability pending. |
| [Mushroom Valley](https://scratch.mit.edu/projects/285730673/) | **B:** A charge/release clears two platforms, Score 2 and natural loss. Prepared copy adds A retry, confirmed fresh zero/alternate character and renewed jump, then browser return. Longer play, normal-build prepared-copy recheck and audio/smoothness pending. |

B means playable through the named checks; C is partial play; D blocks gameplay;
U means no hardware gameplay qualification. No new game is graded A: smoothness,
audio and extended stability remain open. All nine original projects pass
native xemu browser selection, load, pause and Exit, restoring 30 entries each
time. This does not establish gameplay, audio or speed. Level EATEN! additionally
collects/grows from 100 to 200, resets and replays in xemu. Diagnostic hardware
now wins Level 1 and reaches Level 2; ordinary-build acceptance remains open.

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
and browser return. Both repeat the named CPU match/replay/return checks on the
physical **128 MB Xbox**.
The tracked CLI reproduces the tested archives/profiles byte for byte and rejects
overwrite. Tested archive SHA-256 values:

- Beach: `599c658967cf9c43ff8da44488cdbef4fe67e47cbd2fa644b5632926c5571506`
- GlowBall: `15e46a265278580439978c38c4f3b7e8654b0661dc27833bd009c81b5b5c54cf`

Hardware executable: `84d60d948f23d265ad636ecc824e967dafb78a464723833ac137bd1a54c4af07`,
native NV2A/window/Xbox audio, based on the upstream 1.3 integration. This is a
separate test launcher. Later diagnostic checks use `a57d47e0…` with read-only
UDP watch/pause logging. Repeat those loops with the ordinary executable before
final acceptance. The older primary launcher is unchanged. Native test settings
are backed up; rollback is pending manual recovery from Candy Caves. No 64 MB,
measured smoothness or audio qualification is claimed. Detailed controller traces, live MJPEG evidence and
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

## Fireboy and Watergirl controller menu candidate

[The preparer](../scripts/prepare-fireboy-watergirl.py) adds a controller level
selector that reuses the original click/identify procedure and locked-level
checks. D-pad chooses, A starts; Fireboy uses left stick/D-pad and A, Watergirl
uses right stick and X. Black maps the authored R retry. This is one controller
with two keysets; independent two-controller support is not added.

```sh
python3 scripts/prepare-fireboy-watergirl.py Fireboy-Watergirl.sb3 prepared/Fireboy-Watergirl.sb3
```

The compact speech hint (`9e9e6dfe…`) passes native xemu menu visibility,
locked-level rejection, level-one start, Green Flag and clean browser return.
The earlier prepared copy passes hardware selection/locks, both characters’
movement/jumps, natural Game Over/R retry and browser return. The final hint
still needs hardware installation/review. No first-level clear is claimed.

## Candy Caves clone-initialization candidate

The downloaded v1.2 archive has an empty map clone-start hat, with its existing
`set clone to 1` block detached. Original map clones retain zero and enter map
generation. The ordinary native xemu reproduction reaches 25,922 bytecode
threads with 297 sprites and remains at Loading. The physical original also
stops responding after level loading; pause/reset did not recover it.

[The preparer](../scripts/prepare-candy-caves.py) reconnects those two existing
blocks in a separate copy. It preserves all 332 assets and every other original
block/target; its output is deterministic and existing outputs are refused.

```sh
python3 scripts/prepare-candy-caves.py Candy-Caves.sb3 prepared/Candy-Caves.sb3
```

Candidate `b192a9473e7e968e0d9e566c844e04132387a0d55ae2283d966f2a79446d7f4c`
loads a visible level in ordinary native xemu. Controller mining earns candy,
enemies cause damage, Y opens/closes quests, and a natural Game Over shows
Score 80 / Time 0:52. A Replay starts a fresh level; renewed mining earns 20 candy, then pause/Exit
restores zero sprites and the exact 30-game browser. Physical retest is pending.
This is a **prepared-project repair**, not a core or Xbox engine change.

The [Mike recap](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/blob/docs/mike-xbox-handoff-20261027/docs/xbox-handoff-for-mike.md#next-nine-target-pack-of-30)
now includes seven of these additions as real Xbox clips, at 180×120 display,
two per row. That recap and its GIFs remain exclusively on its feature branch.

## Paint the Maze controller menu candidate

[The preparer](../scripts/prepare-paint-maze.py) reuses the authored Play and Home
click handlers behind guarded A/B shortcuts. Directions roll; Y maps the
original R puzzle reset. The original Z+P shortcut is an author-only editor tool,
not Undo; it is left unmapped. All 133 original assets and original blocks remain.

```sh
python3 scripts/prepare-paint-maze.py Paint-the-Maze.sb3 prepared/Paint-the-Maze.sb3
```

Archive `abddaf79494d8a1067760738b07996418e63abac1eb98a13edafcd515190486d`
passes native xemu A Play/B Home/A resume, direction movement and Y reset. Its
first three puzzles are completed using ordinary controller inputs calculated
from the original mazes, naturally reaching Level 4 / Progress 3. Active-game A
does not restart; Level 4 reset restores the exact ball start, Home/A resumes
Level 4, and runtime pause/Exit restores zero sprites and 30 browser entries.
An earlier fixture had an unused X/Z binding; the final profile removes it.
Physical installation/testing and Save/Load menu access remain open.
