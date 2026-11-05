# Upstream Xbox performance review — November 4, 2026

This is an integration/test branch. Main remains at `2bf9fd13`; the installed
Xbox launcher remains `092ca5ff…`. No speedup or 30-game qualification is
claimed.

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

The physical console is reachable at its game list. The existing Player Two
route advertises S3 `192.168.1.243`, configured and consuming USB reports, but
bounded A presses on routes Two and One did not visibly select a project. This
is a controller-delivery limitation; no physical JIT performance result exists.
No KVM firmware, routing or configuration was changed.

Two temporary Appel copies differ only in their sidecar runtime setting
(`bytecode`/`jit`); original archive, profile, settings and primary executable
were verified unchanged before testing. A separate older profiled executable was
launched as the baseline. Its runtime matches main apart from inactive
mouse-help UI code. Return to XBMC is needed to remove the temporary copies and
finish any deployment/readbacks. The new adapted JIT executable has not yet been
launched on the physical console.

A valid comparison needs the same first-wall scene/controller workload, reviewed
before/after images, and complete console frame-profile windows excluding menu
and loading time. Compare the existing main runtime, upstream bytecode, and
upstream JIT. Report script time, frame periods and slow frames separately.
