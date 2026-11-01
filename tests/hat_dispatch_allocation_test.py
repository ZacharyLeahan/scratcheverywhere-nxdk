#!/usr/bin/env python3
"""Exercise actual hat dispatch, input repeat/pause rules and empty-poll allocations."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
hats=(root/'source/runtime/executor/BlockExecutorHats.cpp').read_text()
threads=(root/'source/runtime/executor/BlockExecutorThreads.cpp').read_text()
key=hats[hats.index('void BlockExecutor::executeKeyHats()'):hats.index('\nnamespace {')]
greater=hats[hats.index('namespace {'):hats.index('void BlockExecutor::doSpriteClicking()')]
broadcast=threads[threads.index('std::vector<uint64_t> BlockExecutor::startBroadcastHats('):threads.index('ScriptThread *BlockExecutor::startThread(')]
all_hats=threads[threads.index('void BlockExecutor::runAllBlocksByOpcode('):]
with tempfile.TemporaryDirectory(prefix='hat-dispatch-') as tmp:
    tmp=Path(tmp)
    (tmp/'test.cpp').write_text(r'''
#include "broadcast_index.hpp"
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <new>
#include <unordered_set>
#include <utility>
inline size_t allocations=0;
void *operator new(size_t n) { ++allocations; if(void *p=std::malloc(n?n:1)) return p; throw std::bad_alloc(); }
void *operator new[](size_t n) { return ::operator new(n); }
void operator delete(void *p) noexcept { std::free(p); }
void operator delete[](void *p) noexcept { std::free(p); }
struct Block { std::string key, name; double threshold=0; };
struct Sprite {
    Sprite *cloneOriginal=nullptr;
    std::unordered_map<std::string,std::unordered_set<Block*>> hats;
    BroadcastHatIndex broadcastHatIndex;
};
struct ScriptThread {};
struct Timer { double getTimeMs() { return 1000; } };
struct SoundPlayer {
    inline static int loudness = -1;
    static int getLoudness() { return loudness; }
};
namespace Input {
std::unordered_map<std::string,int> keyHeldDuration;
std::vector<std::string> inputKeys, inputBuffer;
std::unordered_set<Block*> codePressedBlockOpcodes;
}
namespace Scratch {
std::vector<Sprite*> sprites;
void *pauseMenu=nullptr;
int FPS=30;
std::string getFieldValue(const Block &b,const char *field) { return std::string(field)=="BROADCAST_OPTION"?b.name:b.key; }
void resetInput(Block *,const char *) {}
void getInputValueAs(Block *b,const char *,ScriptThread *,Sprite *,double &v) { v=b->threshold; }
}
class BlockExecutor {
public:
static Timer timer;
inline static std::vector<std::pair<Sprite*,Block*>> started;
static void executeKeyHats();
static void resetWhenGreaterThanHats();
static void executeWhenGreaterThanHats();
static void runAllBlocksByOpcode(const std::string &,std::vector<ScriptThread*> *out=nullptr);
static void runAllBlocksByOpcodeInSprite(const std::string &,Sprite *,std::vector<ScriptThread*> *out=nullptr);
static ScriptThread *startThread(Sprite *s,Block *b,bool=false) { started.emplace_back(s,b); static ScriptThread t; return &t; }
static uint64_t startHat(Sprite *s,Block *b) { started.emplace_back(s,b); return started.size(); }
static std::vector<uint64_t> startBroadcastHats(std::string);
};
Timer BlockExecutor::timer;
class BytecodeExecutor { public: static void *startThread(Sprite*,Block*,bool) { return nullptr; } };
#define __XBOX__
#define ENABLE_MENU
'''+key+greater+broadcast+all_hats+r'''
int main() {
    // Each clone still receives every matching broadcast hat, preserving the
    // source set's iteration order and case-insensitive broadcast matching.
    Sprite original, clone; clone.cloneOriginal=&original;
    Block a{"","Game Tick"},b{"","GAME TICK"},other{"","Other"};
    original.hats["event_whenbroadcastreceived"]={&a,&b,&other};
    Scratch::sprites={&original,&clone};
    std::vector<std::pair<Sprite*,Block*>> expected;
    for(auto *s:Scratch::sprites) for(auto *hat:original.hats.at("event_whenbroadcastreceived"))
        if(hat!=&other) expected.emplace_back(s,hat);
    const auto ids=BlockExecutor::startBroadcastHats("gAmE tIcK");
    assert(ids.size()==4 && BlockExecutor::started==expected);
    assert(clone.hats.empty());
    BlockExecutor::started.clear();
    assert(BlockExecutor::startBroadcastHats("absent").empty());

    Sprite keyboard;
    Block right{"right arrow"}, makey{"","makey"}, code{"","code"};
    keyboard.hats["event_whenkeypressed"]={&right};
    keyboard.hats["makeymakey_whenMakeyKeyPressed"]={&makey};
    keyboard.hats["makeymakey_whenCodePressed"]={&code};
    Scratch::sprites={&keyboard}; Input::inputKeys={"right arrow","any"};
    BlockExecutor::executeKeyHats();
    assert(Input::keyHeldDuration["right arrow"]==1);
    assert(Input::inputBuffer==std::vector<std::string>{"right"});
    assert(BlockExecutor::started.size()==3);
    assert(BlockExecutor::started[0].second==&right);
    BlockExecutor::started.clear(); BlockExecutor::executeKeyHats();
    assert(BlockExecutor::started.size()==2); // no key repeat yet
    Input::keyHeldDuration["right arrow"]=15;
    BlockExecutor::started.clear(); BlockExecutor::executeKeyHats();
    assert(BlockExecutor::started.size()==3 && BlockExecutor::started[0].second==&right);
    Scratch::pauseMenu=&keyboard;
    const auto buffer=Input::inputBuffer;
    BlockExecutor::started.clear(); BlockExecutor::executeKeyHats();
    assert(BlockExecutor::started.empty() && Input::inputBuffer==buffer);
    Input::inputKeys.clear(); BlockExecutor::executeKeyHats();
    assert(Input::keyHeldDuration["right arrow"]==0);
    Scratch::pauseMenu=nullptr;

    Block timerHat{"timer","",.5};
    keyboard.hats["event_whengreaterthan"]={&timerHat};
    BlockExecutor::resetWhenGreaterThanHats(); BlockExecutor::executeWhenGreaterThanHats();
    assert(BlockExecutor::started.size()==1);
    BlockExecutor::executeWhenGreaterThanHats(); assert(BlockExecutor::started.size()==1);
    timerHat.threshold=2; BlockExecutor::executeWhenGreaterThanHats();
    timerHat.threshold=.5; BlockExecutor::executeWhenGreaterThanHats();
    assert(BlockExecutor::started.size()==2);
    BlockExecutor::resetWhenGreaterThanHats();

    Block loudnessHat{"loudness","",10};
    keyboard.hats["event_whengreaterthan"]={&loudnessHat};
    BlockExecutor::started.clear();
    BlockExecutor::executeWhenGreaterThanHats();
    assert(BlockExecutor::started.empty()); // unavailable microphone (-1)
    SoundPlayer::loudness=11;
    BlockExecutor::executeWhenGreaterThanHats();
    BlockExecutor::executeWhenGreaterThanHats();
    assert(BlockExecutor::started.size()==1); // rising edge only
    SoundPlayer::loudness=10;
    BlockExecutor::executeWhenGreaterThanHats();
    SoundPlayer::loudness=12;
    BlockExecutor::executeWhenGreaterThanHats();
    assert(BlockExecutor::started.size()==2);
    BlockExecutor::resetWhenGreaterThanHats();

    // Warming a large scene must not populate absent hats or allocate keys on
    // subsequent empty input polls/broadcast misses. Assert allocation count,
    // not a timing threshold dependent on the host machine.
    std::vector<Sprite> empty(400);
    Scratch::sprites.clear();
    for(auto &s:empty) Scratch::sprites.push_back(&s);
    Input::inputKeys.clear(); Input::keyHeldDuration.clear();
    BlockExecutor::executeKeyHats(); BlockExecutor::executeWhenGreaterThanHats();
    BlockExecutor::startBroadcastHats("absent");
    const auto before=allocations;
    for(int frame=0;frame<100;++frame) {
        BlockExecutor::executeKeyHats(); BlockExecutor::executeWhenGreaterThanHats();
        assert(BlockExecutor::startBroadcastHats("absent").empty());
    }
    assert(allocations==before);
    for(auto &s:empty) assert(s.hats.empty());
    std::cout<<"PASS: actual key/repeat/pause/timer/loudness hats, clone broadcasts/order; 400 sprites x 100 empty polls with zero allocations or inserted hats\n";
}
''')
    subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined','-I'+str(root/'include/runtime'),str(tmp/'test.cpp'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
