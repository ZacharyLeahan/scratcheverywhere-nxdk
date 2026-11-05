# Upstream Xbox performance review — November 4, 2026

This is an integration/test branch in
[draft PR #76](https://github.com/ZacharyLeahan/scratcheverywhere-nxdk/pull/76).
Main remains at `2bf9fd13`; the installed Xbox launcher remains `092ca5ff…`. The
first physical Appel measurements regress, so promotion is held. No speedup or
30-game qualification is claimed.

## What changed upstream

At this check, upstream main is
[`4054c836`](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/4054c836e23bd19b9e7c0fecac3b51b6915c6674),
25 commits beyond the fork's last synchronization (`b62d2070`).

- [Shared JIT compiler](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/7374c171df4c72adcebac2679528f7455f24188d)
  compiles supported bytecode into native machine code.
- [Mike's Xbox x87 backend](https://github.com/ScratchEverywhere/ScratchEverywhere/commit/91b765cff422dec6f33b6f4885899dd71d43b2fd)
  makes it work on the original Xbox CPU, which lacks SSE2. It adds a 1 MiB
  executable-memory arena and enables JIT support for Xbox builds.
- Further upstream changes optimize numeric variables, list operations, JIT
  calls and memory use. The new scheduler also uses spare frame time for
  scripts.
- Earlier NV2A effect-cache/hybrid-hue improvements were already incorporated.
  The saved console configuration uses the **Xbox renderer with SDL3
  window/audio**; native NV2A-specific improvements do not establish gains on
  that selected path.

JIT can reduce script execution cost, so Appel is a useful candidate. Rendering,
collision work, asset loading and frame pacing can still limit smoothness. A 30
FPS project does not automatically become a 60 FPS project.

## Fork adaptations

The integration preserves deferred sender retirement, indexed broadcasts,
source-alpha collision repairs, SVG reload behavior and homebrew controls.
Upstream's numeric cache supersedes the older fork cache.

The first build revealed that the fork's seven private arithmetic/boolean
opcodes prevented JIT analysis of most sprites. They are replaced by upstream's
operator lowering, which JIT understands. Its old opcode-only harness is retired
with that implementation. The upstream cache format is now used without those
private opcodes; the earlier private test executable is excluded from
acceptance.

## Validation and limits

NXDK Release builds pass. Relevant host checks cover numeric conversions, list
operations, thread retirement, broadcast dispatch, collision overlap, texture
layouts/uploads and costume-cache behavior. Their standalone harnesses were
adapted for upstream's moved conversion/list/rounding helpers and vector hats.

A private xemu check confirms requested/compiled JIT code and Beach CPU
movement, jumping, replay, pause, browser return and system-menu cancel. That
first build still had the private arithmetic opcodes, so it only demonstrates
partial compatibility. With the adaptation, JIT code is present for 23 Appel
sprites instead of none. A readiness-gated repeat passes title → level picker →
Level 1, right movement, one apple, a jump, pause and return to the game list.
Two earlier runs sent inputs before the title was ready and are excluded from
gameplay acceptance. Emulator configuration is 128 MiB, but its current guest
kernel reports 64 MiB. No emulator timing is presented as Xbox performance.

## Physical comparison — November 4, 2026

The main ESP DEVICE USB adapter is physical Player One. Fresh streaming video
confirms actual A pressure and release in Controller Tool, then Appel movement,
pause, browser return and confirmed dashboard return. Earlier ineffective S3
attempts do not apply to this working direct route. No firmware, routing or
console settings were changed during these tests.

On the physical **128 MB Xbox**, matching profiled Release builds use the Xbox
renderer, SDL3 window/audio, forced 480p and the same prepared Appel archive and
controls. Two temporary copies differ only in their runtime sidecar. The old
baseline runtime matches main apart from inactive mouse-help UI files.

Each run starts at Level 1's first wall with one apple. It repeats eight Left
1.5-second / Right 2-second cycles. Fresh images before and after confirm the
same scene. No test video consumer is open during measurement. All complete
120-frame intervals inside the action are included with 0.5-second boundary
guards; loading and menu time are excluded. Host/console interval checks pass.

| Runtime                    | Frames |   FPS | Script ms/frame | Median window p95 ms |
| -------------------------- | -----: | ----: | --------------: | -------------------: |
| Previous main runtime      |    600 | 26.71 |           17.22 |                52.69 |
| Upstream bytecode          |    480 | 23.16 |           22.23 |                52.68 |
| Upstream JIT, second load  |    360 | 19.36 |           24.13 |                68.97 |
| Upstream JIT, fresh launch |    480 | 19.43 |           23.88 |                68.40 |

These samples show **no Appel speedup**: upstream bytecode is about 13% slower
and JIT mode about 28% slower than the baseline in this sequence. A
fresh-process JIT repeat gives 19.43 FPS, about 27% below baseline; reload/order
does not explain this observed slowdown. These are short samples, not a
whole-game benchmark. Window p95 is not a pooled percentile. Maximum periods are
still 133–153 ms; neither Mac-like smoothness nor an A grade follows.

The console logs distinguish `Runtime: bytecode VM` and
`Runtime: bytecode VM + JIT`, without a logged backend-check failure. Exact
physical JIT compilation coverage was not instrumented; the 23-sprite count
above comes from xemu. Do not infer that every script ran native code from the
runtime label alone.

All 39 baseline, 44 first-candidate and 24 fresh-JIT frame reports match the
retrieved console logs. Received sequences are contiguous while listening. Both
runtimes return through the game list to XBMC with working FTP. Both temporary
test archives and sidecars were removed after the final run. FTP readbacks
verify the original 30-game list, Appel archive/profile, settings and primary
executable. The Xbox is left in XBMC with all test controls released.

The tested profiler XBEs are `8f15c424…` (baseline) and `a20baa59…` (adapted
upstream). Matching ELF/cache receipts, plans, frame reports and fresh image
reviews are retained under ignored `build-xbox/hardware/upstream-jit-20261104/`
and the shared ESP-KVM observations directory. The earlier `c35bf7ca…`
executable is excluded and was not launched in this comparison.

Before merging, isolate the regression: verify native-code coverage/arena use,
separate script cost from present/frame pacing, and repeat on an ordinary build.
The new bytecode path must also remain usable for games whose JIT coverage is
partial. Keep the working regular launcher while this draft is investigated.
