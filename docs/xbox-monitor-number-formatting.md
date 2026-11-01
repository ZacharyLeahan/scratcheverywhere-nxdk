# Numeric monitor formatting

The Xbox showed long decimal tails in Jumper's timer: a displayed `0.2` could
become `0.19999999999999998`. The existing core formatter already rounds
numeric monitors to six decimal places, but the Xbox's fast-math options turn
its final division into multiplication by an inexact reciprocal. Ryu then
faithfully prints that new floating-point value, exposing the tail again.

`Render::getVariableValueString` now keeps an actual division for that final
step. Values with magnitude at least 2^33 bypass decimal scaling: double spacing
there already exceeds a millionth, and scaling very large values can overflow.
Text-valued variables retain their exact text. The change is in the shared
monitor formatter; the observed trigger is the Xbox compiler configuration.
Game variables, arithmetic and project scripts are unchanged.

## Validation

`python3 tests/monitor_number_test.py` compiles the actual renderer function,
actual `Math::toString` and configured RyuJS source. It checks normal and Xbox
`-O1 -ffast-math -fno-finite-math-only` builds, including decimals, rounding,
negative zero, large/nonfinite values, exact text and undefined values. It also
covers numeric bits read from the Xbox guest. The old implementation fails
the same `0.1` assertion under those flags.

A normal diagnostics-off NXDK build passed. In isolated xemu snapshot guests,
the identical locally authored monitor probe produced:

| Numeric monitor | Old build | Repaired build |
| --- | --- | --- |
| 0.1 | 0.09999999999999999 | 0.1 |
| 0.2 | 0.19999999999999998 | 0.2 |
| Negative 0.2 | -0.19999999999999998 | -0.2 |
| Score | 100000000 | 100000000 |
| Text `0.20000000000000001` | exact text retained | exact text retained |

Read-only GDB snapshots confirm all nine constant numeric inputs have identical
bits in both runs. A separate pre-existing loading-precision issue remains:
JSON `1e308` reaches the formatter as `1.0000000000000471e308`, and
`8589934592.000002` arrives as `8589934591.999982`. Both builds receive those
same values. The repair preserves those inputs and prevents the first from
being displayed as Infinity solely because of monitor scaling; it does not
repair JSON numeric conversion.

Local before/after framebuffer images, matching symbols, probe archive,
input-bit snapshots, build receipts and test output are under ignored
`build-xbox/monitor-rounding-20261028/`. The old comparison executable is
`03bf7947…` (input tracing enabled); the repaired executable is
`0c4842ee…` (diagnostics off). Their renderer optimization flags match.

Physical Xbox confirmation is pending. The repaired executable has not replaced
either installed normal launcher. Emulator validation does not complete the
21-game hardware qualification.
