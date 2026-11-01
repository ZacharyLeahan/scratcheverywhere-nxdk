# Upstream 1.3 integration — November 1, 2026

This sync includes all 17 upstream commits through
[`1d606eb4`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/1d606eb47e18b96a82349fea83e9cdf060ea88d2).
It brings release 1.3 packaging and Xbox workflow updates, together with three
native renderer changes:

- [`85146de8`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/85146de8):
  software effect-cache and memory management improvements.
- [`157afb18`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/157afb18):
  configurable hardware color adjustments.
- [`0bd8c383`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/0bd8c383):
  experimental GPU hue rendering and effect-texture optimizations.

These are Xbox changes. The release also updates other platforms; those builds
have not been validated here. No changes were sent upstream.

## Fork fixes retained

The merge keeps the original-asset color recovery used by Scratch collision
queries, SVG linear sampling, explicit nearest sampling for pixelate, clamped
non-power-of-two texture uploads, and alpha-correct brightness across ordinary,
tiled, mosaic, pixelate and deformed drawing. The upstream ordinary positive
brightness helper runs without also applying the fork's brightness stage.

Controller handoff, retained Back taps, pause/restart/return-to-browser, the Xbox
reset chord, authored project lists, prepared-project support and profiling
options remain intact. The Xbox source includes logging in normal builds too;
upstream effect-source error handling needs it outside profiling builds.

`SE_XBOX_NV2A_HARDWARE_COLOR_ADJUSTMENTS` defaults to `ON`.
`SE_XBOX_NV2A_HYBRID_HUE` stays `OFF`, as upstream specifies. If explicitly enabled,
combined brightness retains CPU hue plus the fork's brightness combiner. The
experimental GPU hue path is not qualified by the default-build results below.

## Validation

The normal Release NXDK build succeeds with 480p, expanded RAM enabled, menus
on, loading screen off, and tracing/profiling/regression startup options off.
A separate `SE_XBOX_NV2A_HYBRID_HUE=ON` build also compiles successfully; that
is compile coverage only, with no experimental-mode runtime acceptance.

- 3,216 independent DXT layout cases pass ASan/UBSan: selectors, endpoints,
  partial-block edges, pitches, guarded writes and overlapping buffers.
- All 27 clamped-upload sanitizer cases and 1,756 color-reference cases pass.
- Native and SDL emulator regressions each report **58 passes / 0 errors**.
- Native GPU pixels pass **60/60** in the ordinary memory policy and **60/60**
  with an explicit diagnostic expanded-graphics-policy override, maximum channel
  errors 9 and 2. Read-only breakpoints confirm all four special draw paths in
  the expanded-policy run. That override does not test RAM detection.

The tested normal executable is `84d60d94…`. Final cleanup removes duplicate
CMake source entries and fixes a comment; the rebuilt executable is
`4a738161…`. Its machine code, mutable data, all section addresses and all 59
embedded-file contents match the tested build. Only the debug-directory build
timestamp and ZIP timestamps differ. Matching symbols and both binaries are
preserved with the private evidence.

All **21 normal games** pass native-emulator browser selection → actual archive
load → pause → Exit, in one snapshot guest. Every return has zero game sprites
and the exact 21-game/42-button browser. The first observer attempt had a
malformed symbols-file path before any game launched; that failed harness
record is retained separately. The corrected run uses the matching ELF.
No new physical qualification or speed improvement is inferred from these checks.
The live hardware Sokoban/Maze results use the earlier `c7c0a9d9…` build, and
the primary dashboard launcher remains separate. See the
[game status](xbox-game-status.md) for actual gameplay coverage.

Original evidence is ignored under `build-xbox/upstream13-20261101/` in the
primary checkout. All guests use a disposable snapshot of the preserved HDD;
no authored game variables are written by the debugger.
