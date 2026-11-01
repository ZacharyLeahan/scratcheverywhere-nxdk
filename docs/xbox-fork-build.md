# Building this fork for the Original Xbox

This fork starts from `ScratchEverywhere/ScratchEverywhere` at
`79a843c33be1f290450bf6c98fc0a7616a850a76`. MikeDev101's original
`ScratchEverywhere-OGXbox` fork was archived on October 19, 2026; its README
directs users to upstream, which now includes the Xbox port.

Current main includes the [upstream release 1.3 integration](xbox-upstream-1.3.md)
and supports both the native NV2A renderer/window with dedicated Xbox audio and
the legacy Xbox SDL path. Compatibility patches remain in `cmake/patches`;
the SDK revision matches `docker/Dockerfile.xbox`. Existing saved renderer
preferences are respected. Build success does not qualify either path on hardware;
see the [21-game status and known issues](xbox-game-status.md).

## Native build

Install Git, CMake, Make, LLVM (including LLD), Bison, Flex and Rust/Cargo.
Cargo builds the `dsp56300-asm` host tool used by Xbox audio. On macOS use
Homebrew LLVM rather than Apple's compiler.

If Rust is not already installed, an isolated official rustup installation can
be created without changing your shell profile:

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/se-rustup-init.sh
CARGO_HOME="$PWD/.cache/toolchains/cargo" \
RUSTUP_HOME="$PWD/.cache/toolchains/rustup" \
  sh /tmp/se-rustup-init.sh -y --profile minimal --default-toolchain stable --no-modify-path
```

The helper automatically uses that local installation. Then build:

```sh
bash scripts/build-xbox.sh
```

The script keeps its patched SDK under `.cache/toolchains/nxdk` and builds
under `build-xbox`. It does not use or patch a shared NXDK installation.
The first build downloads dependencies and compiles NXDK. To limit application
compilation parallelism, set `BUILD_JOBS` (default: 4). Extra arguments are passed
to CMake, for example `bash scripts/build-xbox.sh -DSE_DECTALK=OFF`.

Expected outputs are `build-xbox/default.xbe` for a modded Xbox and
`build-xbox/scratch-xbox.iso` for xemu. Producing these files does not establish
that a build boots or works on hardware; test separately.

The Xbox SDL source cache includes the local `nxdk-sdl3.patch` hash. Editing
that patch triggers reconfiguration and selects a new patched SDL checkout,
so incremental builds cannot silently keep an earlier driver patch. Existing
cache revisions are retained. See the [texture-retirement regression](xbox-texture-retirement.md)
for the driver change that exposed this cache issue.

### First successful local build

On October 25, 2026, `bash scripts/build-xbox.sh` completed on macOS with
Homebrew Clang 23.1.2 and Rust 1.99.1, using the default Xbox options. The XBE
header begins with `XBEH`; packaging added that XBE to the XISO successfully.
That initial build had not yet been boot-tested. Later, separately identified
emulator and physical results are recorded in the [game status](xbox-game-status.md).

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| `default.xbe` | 9437184 | `f983cf5b0d3f77a4129a45a9f5a7aaa1ee72bcd910ac6ab3438bc374f7dceb36` |
| `scratch-xbox.iso` | 10027008 | `141ac60ccff104b5422f95714be05de96e90f4f4f6dce0973f4d9708a00ab32c` |

## Upstream container build

With Docker running, use the existing upstream image definition:

```sh
mkdir -p romfs build-xbox-export
docker build --file docker/Dockerfile.xbox --target exporter \
  --output type=local,dest=build-xbox-export .
```

The Xbox workflow is `.github/workflows/nightly-xbox.yml` and supports manual
dispatch. Forks may require enabling GitHub Actions first.

## Native renderer options

Upstream 1.3 enables `SE_XBOX_NV2A_HARDWARE_COLOR_ADJUSTMENTS` by default.
`SE_XBOX_NV2A_HYBRID_HUE` is experimental and remains `OFF`; the normal regression
results do not qualify that opt-in path. Frame capture and the NV2A startup test
suite are diagnostic options and remain disabled for normal gameplay builds.
See the [integration notes](xbox-upstream-1.3.md) for retained fork behavior and
validation limits. These compile options do not override saved renderer choices.

## Running projects

Put Scratch projects in `E:\ScratchEverywhere` on the console or emulated HDD.
See <https://scratcheverywhere.github.io/install> for current installation details.

## Expanded-memory hardware tests

Xbox packaging clears the XBE's 64MB limit by default
(`SE_XBOX_ALLOW_EXPANDED_RAM=ON`). This permits an expanded console to use its
additional RAM; it does not add RAM to a retail console. Python 3 is required
for this packaging step. Set the option to `OFF` to retain CXBE's original
memory-limit flag for comparison.

Earlier 128MB hardware tests loaded Appel's complete map lists with NXDK's
native allocator. Upstream has since removed the Xbox lwmem override;
`SE_USE_LWMEM` is no longer a current Xbox build option. Historical lwmem
investigations in older test notes do not describe the current allocator.

The combined October 29 source tree builds with:

```sh
BUILD_JOBS=4 bash scripts/build-xbox.sh \
  -DSE_XBOX_FORCE_480P=ON -DSE_XBOX_ALLOW_EXPANDED_RAM=ON \
  -DSE_XBOX_DEBUG_SYMBOLS=ON \
  -DSE_XBOX_PROFILE_FRAMES=OFF -DSE_XBOX_PROFILE_THREADS=OFF \
  -DSE_XBOX_TRACE_GAME_STATE=OFF -DSE_XBOX_TRACE_MENU_INPUT=OFF
```

This produces a Release XBE and matching debug symbols with profiling/input
tracing disabled. The merged build and 21 affected host checks pass; that does
not replace native-backend physical acceptance or establish FPS. The latest
physical test launcher remains separate from the newly merged build.

For diagnostics only, `SE_XBOX_TRACE_GAME_STATE=ON` logs stage variables when
the runtime pause menu opens. It defaults to `OFF`. See the
[hardware checklist](xbox-game-qualification.md) for remaining tests.


## Upstream synchronization (October 26, 2026)

Merged upstream `main` through
[`ac8a468b`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/ac8a468bb42681127bd3a0ba1507a1d7f0f4390d),
including the new bytecode VM (`4cb9003d`) and libdlgmod update (`94b040fb`).
The pre-merge fork tip is retained at
`backup/pre-upstream-20261026-8a1efc0f`.

The upstream ROMFS repair supersedes the fork's overlapping embedded-archive
workaround: embedded projects always retain their archive in memory, even when
`sb3InRam=false`; only external archives are subject to the 6/24MiB RAM budget.
The failed-file-open fallback now copies the caller's stream into owned memory
rather than retaining a stream the caller subsequently destroys. The fork
keeps complete authored Xbox map lists instead of truncating them.

Upstream split the runtime into smaller files. The empty-input defaults were
carried into `runtime_inputs.cpp`, preserving false/zero/empty results in legacy
execution and VM fallbacks. Xbox's physical Start hold still opens pause after
three seconds of wall time in `runtime_loop.cpp`. Upstream's bytecode VM remains
enabled by default; it was not disabled to resolve the merge. SB2 costume name
lookup, per-project controller profiles, multi-controller/reset/replay behavior,
browser confirmation-release gating and the GPU/color/pen fixes are retained.

Validation: the NXDK regular and embedded builds passed, as did all 1,756 host
color-effect cases. An embedded fixture explicitly set `sb3InRam=false` and
`useBytecode=true`. GDB verified archive retention was true and stopped in the
new bytecode executor. The fixture rendered its SVG after loader completion and
reported PASSES=3, ERRORS=0, EMPTY ADD=7. A second boot selected the legacy engine
under GDB before sprite parsing, stopped in its executor, and produced a
pixel-identical passing image. Networking was skipped under GDB only for these
two diagnostic runs. Evidence is in ignored `build-xbox/upstream-sync`, with
matching diagnostic ISO/XBE/ELF files and settings retained under `fixture/`.

The final normal build restores menu mode, has no embedded fixture, and disables
debug symbols and renderer/game tracing. Its XBE is 9,633,792 bytes, SHA-256
`f90ec7b0ba1aaa460dcbaa8cfbdce69945ae878eed422f97042d72852dab918f`.
It reached the populated browser in xemu without debugger overrides. At sync completion this build had not yet been tested on the physical Xbox.
It was subsequently installed in a separate test folder for Appel and Asteroids
checks; the regular Games launcher retains the previous production build.
See `xbox-game-qualification.md` for that testing and the later SB2 text repair.
Qualification across all twenty games remains incomplete.
The normal-build emulator smoke test also passed browser selection, SB2
named-costume rendering, the installed D-pad profile (a crate push), physical
Start-hold pause, and Exit Project back to the browser with an 800ms confirm.
Images are `normal-browser.png`, `normal-sb2-moved.png`, `normal-pause.png` and
`normal-browser-return.png`; `validation.json` records artifact hashes.

## Upstream synchronization (October 27, 2026)

Merged upstream `main` through
[`0bacdb6d`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/0bacdb6d0d7d7285d4ca8f46ae59e5cd6fb3a174)
(`feat: add wii u audio backend`) into the fork without conflicts. All existing
Xbox fixes are retained. The new backend is guarded by `AUDIO_WIIU`; Xbox still
builds SDL3 audio. Although the shared backend enum gains an entry, settings
store `AudioEngine` by name, so an existing `"SDL3"` setting needs no migration.

The separate NXDK build in
`build-xbox/upstream-wiiu-audio-20261027/build` passed with the normal menu,
forced 480p, native allocator, and renderer/game/menu tracing disabled. Debug
symbols are retained for matching GDB sessions. Existing emulator images and
previous matching symbols were preserved. The resulting artifacts are:

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| `default.xbe` | 9,699,328 | `e332255e51c0bed0847e5601b4e8abe2547ff56cc857187c704131829b413b69` |
| `scratch-xbox.iso` | 10,289,152 | `7eb5a9d5a0306c2ad52324a41e3809c28386589c5c6eff38d88f111bb7a313f6` |
| `scratch-xbox-symbols.elf` | 129,528,740 | `a36d536901e1f8dec17730a6ddbbaf6a4f0e3890f478b96262619835e45ae4d2` |

A fresh dependency resolution also advanced dr_libs from `ea33eedd` to
`a466dbe8` under the existing dependency specification. Its three changes fix
AIFF decoding, WAV fact-chunk handling, and unsigned 8-bit PCM centering. Host
probes verified the corrected 8-bit conversion and identical decoded samples
for Sokoban's IMA ADPCM music against the previous decoder and FFmpeg
(2,408,256 mono frames). Six other checked Git dependencies were unchanged.
The host audio-resampler suite also passed all 160 cases and its EOF, gain,
pitch-change and reset checks.

The XBE was uploaded to a separate hardware test folder,
`F:\scratch-upstream-wiiu-audio-20261027`, with complete temporary and final
FTP readbacks. On the 128MB Xbox it reached the populated browser, selected
Sokoban, completed puzzles 1–3 with all four D-pad directions, and restarted a
puzzle with Black. Fifteen observed board states matched the independent
model, ending at level 4 / moves 14. A 120-second HDMI capture matched the
project's music across its loop, with no full-scale samples; the measured loop
delay was approximately 94ms. Y mute produced eight seconds of exact digital
silence. These are measured playback checks; subjective audio acceptance and
qualification across all twenty games remain open.

At this sync checkpoint the regular Games launcher remains the preceding
`2b8b5778` build, confirmed by full FTP readback. No installed project archive
was changed. Build/dependency manifests, decoder probes, and hardware evidence
are retained under ignored `build-xbox/upstream-wiiu-audio-20261027` and
`build-xbox/hardware/upstream-wiiu-*` paths.

## Upstream synchronization (October 30, 2026)

Merged upstream `main` through
[`59057691`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/59057691)
from fork main `d35d77e7`. This imports eleven upstream commits after `ec2400eb`,
including microphone/loudness support, the NV2A effect-cache allocation retry,
NDS audio/assets fixes, PSP SDL3 migration and other platform build fixes.
The merge preserves the complete fork history and all existing Xbox/game work;
`backup/pre-upstream-20261030` retains the previous main locally. Existing
unmerged feature branches remain separate and unchanged.

The host event-dispatch harness now provides the new loudness dependency and
checks unavailable microphones and rising threshold crossings. Audio resampling
(160 streaming cases plus EOF/gain/pitch/reset), hat dispatch/allocation,
typed arithmetic/logic bytecode and costume-cache lifetime checks passed.

A native-only renderer configuration exposed the existing cross-renderer texture
cache dependency on `Image_Xbox` and SDL headers. Use the documented dual-backend
configuration (`SE_RENDERER=all`, `SE_WINDOWING=all`, `SE_AUDIO_ENGINE=all`)
for this validation. Native Xbox audio returns -1 for an unsupported microphone.
No console deployment or new hardware acceptance is implied by this sync.

The dual-backend NXDK Release build passed with forced 480p, native allocator,
and frame/thread profiling disabled. The resulting `build-xbox/default.xbe`
SHA-256 is `eb3492c2b7149a14200d02486a5d12b95cf886ebdb26655c255ac5f738a24535`.
Build logs are retained locally in `/tmp/upstream-sync-20261030-build-all.log`.

### Checking the disc image used for testing

When the build cache sets `EXTRACT_XISO_BIN=OFF`, a successful build updates the
XBE without regenerating `scratch-xbox.iso`; an older ISO may still be present.
Check the disc's embedded `default.xbe` against the executable under test before
using matching debugger symbols. The October 30 native regression uses a fresh
separate image with complete embedded-XBE byte comparison, not the stale primary
ISO. This does not change the cache's intentional packaging setting.
