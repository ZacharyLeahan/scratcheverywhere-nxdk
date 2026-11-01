#pragma once
#include <vector>

// Restarting a hat replaces its scheduled thread, but an invocation already on
// the C++ stack may finish its current quantum. Scratch VM's _restartThread
// likewise replaces the scheduled entry without stopping that invocation.
class ThreadExecutionFrame {
    inline static ThreadExecutionFrame *current = nullptr;
    ThreadExecutionFrame *previous;
    const void *thread;

  protected:
    bool finishAtYield = false;

  public:
    explicit ThreadExecutionFrame(const void *value) : previous(current), thread(value) { current = this; }
    ~ThreadExecutionFrame() { current = previous; }
    ThreadExecutionFrame(const ThreadExecutionFrame &) = delete;
    ThreadExecutionFrame &operator=(const ThreadExecutionFrame &) = delete;

    static bool active() { return current != nullptr; }

    template <class Thread>
    static void finishAfterCurrentQuantum(Thread *value) {
        for (auto *frame = current; frame; frame = frame->previous) {
            if (frame->thread == value) {
                frame->finishAtYield = true;
                return;
            }
        }
        value->finished = true;
    }
};

template <class Thread>
class ThreadExecutionScope : public ThreadExecutionFrame {
    Thread &thread;

  public:
    explicit ThreadExecutionScope(Thread &value) : ThreadExecutionFrame(&value), thread(value) {}
    ~ThreadExecutionScope() {
        if (finishAtYield) thread.finished = true;
    }
};

// A restarted sender (including a legacy procedure's parent) must not be
// cleared, pooled or deleted while a nested invocation can still access it.
template <class Thread>
class RetiredThreads {
    inline static std::vector<Thread *> pending;

  public:
    template <class Dispose>
    static void retire(Thread *thread, Dispose dispose) {
        if (ThreadExecutionFrame::active()) pending.push_back(thread);
        else dispose(thread);
    }

    template <class Dispose>
    static void collect(Dispose dispose) {
        if (ThreadExecutionFrame::active()) return;
        for (auto *thread : pending)
            dispose(thread);
        pending.clear();
    }
};
