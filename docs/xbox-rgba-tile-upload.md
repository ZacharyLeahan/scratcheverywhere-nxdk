# Xbox RGBA tile uploads

The Xbox SDL renderer discarded successful 32-bit tile uploads and compressed
the image instead. SDL3 returns `true` for a successful upload; this branch
tested for `false`. A failed upload could also be retained as a usable tile.

The corrected condition keeps successful RGBA tiles and releases failed uploads
before trying the existing compressed fallback. The expanded-memory and free-RAM
checks are unchanged. Retaining RGBA uses more texture memory than compression;
the existing per-tile memory threshold still applies.

Validation:

- The host test executes the production tile builder with injected SDL results.
  It verifies source pixels and partial edge tiles, failed-upload fallback,
  limited-memory behavior and allocation-failure cleanup under ASan/UBSan.
  Reversing the condition reproduces the original failure.
- Matched diagnostic builds on the physical 128 MB Xbox render the same large
  SVG fixture and complete four costume swaps. Read-only pause metadata reports
  DXT1 for the control's first tile and RGBA32 for the corrected first tile, for
  both the 600 × 440 pattern and 640 × 480 backdrop. Both return to XBMC.
- The normal corrected NXDK build completes with the private metadata logger
  removed. It repeats four costume swaps and returns cleanly to the browser.

Run the host regression and generate the offline hardware fixture:

```sh
python3 tests/xbox_rgba_tile_upload_test.py
python3 examples/make-xbox-rgba-tile-test.py /tmp/rgba-tiles.sb3
```

Map the fixture's Scratch A key to a controller button. Four presses should show
`SWAPS 4` and restore the original pattern. The fixture is separate from the
30-game pack. These checks establish the upload/fallback behavior; game frame
rate, long-session memory use and retail 64 MB hardware remain unqualified.
