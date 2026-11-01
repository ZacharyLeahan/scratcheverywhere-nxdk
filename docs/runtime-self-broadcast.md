# Self-broadcast restart candidate

Ninja Climb’s first exit broadcasts `Reset`, then `clear`, from a running Reset
handler. Restarting that same handler used to finish or clear the active thread
immediately, so `clear` was skipped and the course stayed at one.

The shared legacy and bytecode executors now replace the scheduled thread in
place. An invocation already on the stack can finish its current quantum; its
storage is retired until nested execution has returned. A yielded old invocation
cannot resume. Explicit stop-this and stop-all still stop immediately. This is a
**shared core change**, with no Xbox-specific branch or Ninja project edits.

This follows the reference VM’s
[`_restartThread`](https://github.com/scratchfoundation/scratch-vm/blob/develop/src/engine/runtime.js)
and [sequencer](https://github.com/scratchfoundation/scratch-vm/blob/develop/src/engine/sequencer.js)
behavior. An independent run with pinned `scratch-vm@5.0.300` provides the
fixture’s expected counters.

## Validation

```sh
python3 tests/thread_lifetime_test.py
python3 tests/broadcast_index_test.py
python3 tests/hat_dispatch_allocation_test.py
python3 examples/make-self-broadcast-test.py /tmp/self-broadcast.sb3
```

After Green Flag, STARTS, TAIL and CLEARS must each be 3. A exercises a
self-broadcast-and-wait: WAIT STARTS=2 and WAIT TAIL=1. X/Y exercise explicit
stop-this/stop-all: both stop-tail counters remain zero. For legacy execution,
put `"useBytecode": false` inside the controller profile’s `settings` object.
The diagnostic is separate from the game pack.

The host lifetime tests pass under AddressSanitizer/UndefinedBehaviorSanitizer,
including a nested procedure’s active parent, deferred disposal, yields and
explicit stops. Existing broadcast-index and allocation/dispatch tests pass.
The native Xbox Release build passes with tracing/profiling disabled.

In isolated 128MB xemu, the unchanged fixture fails before the fix (TAIL and
CLEARS stay zero) and passes after it in **both verified execution modes**.
The candidate also advances the original Ninja project from course one to two
through ordinary controller play, with zero deaths, renewed course-two movement
and a clean return to the 30-game browser. GDB reads state but does not seed game
variables. The initial repeated controller route needed adjustment for the new
run’s timing; that unsuccessful traversal is retained as evidence.

Physical Xbox validation, broader game regressions, audio, measured pacing and
long sessions are still open. This remains a candidate off main.
