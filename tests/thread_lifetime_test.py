#!/usr/bin/env python3
"""Exercise restart retirement across nested execution, yields and real stops."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="thread-lifetime-") as tmp:
    work = Path(tmp)
    (work / "test.cpp").write_text(r'''
#include "thread_lifetime.hpp"
#include <cassert>
#include <vector>

struct Thread {
    bool finished = false;
    int tail = 0;
    inline static int destroyed = 0;
    ~Thread() { ++destroyed; }
};

int main() {
    const auto dispose = [](Thread *thread) { delete thread; };
    auto *sender = new Thread;
    auto *replacement = new Thread;
    Thread procedure;
    std::vector<Thread *> scheduled{sender};
    {
        ThreadExecutionScope<Thread> root(*sender);
        {
            ThreadExecutionScope<Thread> nested(procedure);
            scheduled[0] = replacement;
            ThreadExecutionFrame::finishAfterCurrentQuantum(sender);
            RetiredThreads<Thread>::retire(sender, dispose);
            RetiredThreads<Thread>::collect(dispose);
            assert(Thread::destroyed == 0 && !sender->finished);
            ++procedure.tail;
        }
        // Returning from the procedure must not clear or stop its parent.
        assert(!sender->finished && procedure.tail == 1);
        ++sender->tail;
        assert(sender->tail == 1 && !replacement->finished);
    }
    assert(sender->finished && sender->tail == 1);
    assert(scheduled[0] == replacement);
    RetiredThreads<Thread>::collect(dispose);
    assert(Thread::destroyed == 1);

    // A yielded invocation is retired; it cannot later resume its old tail.
    auto *waiting = new Thread;
    {
        ThreadExecutionScope<Thread> execution(*waiting);
        ThreadExecutionFrame::finishAfterCurrentQuantum(waiting);
        RetiredThreads<Thread>::retire(waiting, dispose);
        assert(!waiting->finished);
    }
    assert(waiting->finished && waiting->tail == 0);
    RetiredThreads<Thread>::collect(dispose);
    assert(Thread::destroyed == 2);

    // An inactive receiver stops immediately, even during another invocation;
    // disposal waits until there are no nested execution frames.
    auto *inactive = new Thread;
    {
        ThreadExecutionScope<Thread> execution(*replacement);
        ThreadExecutionFrame::finishAfterCurrentQuantum(inactive);
        assert(inactive->finished);
        RetiredThreads<Thread>::retire(inactive, dispose);
        RetiredThreads<Thread>::collect(dispose);
        assert(Thread::destroyed == 2);
        // Explicit Stop remains immediate and is never undone at scope exit.
        replacement->finished = true;
        if (!replacement->finished) ++replacement->tail;
    }
    assert(replacement->finished && replacement->tail == 0);
    RetiredThreads<Thread>::collect(dispose);
    assert(Thread::destroyed == 3);
    delete replacement;
    auto *outside = new Thread;
    RetiredThreads<Thread>::retire(outside, dispose);
    assert(Thread::destroyed == 5);
    assert(!ThreadExecutionFrame::active());
}
''')
    subprocess.run(["c++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-fsanitize=address,undefined", "-I" + str(root / "include/runtime"),
                    str(work / "test.cpp"), "-o", str(work / "test")], check=True)
    subprocess.run([str(work / "test")], check=True)
print("PASS: nested sender lifetime, yield retirement, receiver cancellation, explicit Stop and deferred disposal")
