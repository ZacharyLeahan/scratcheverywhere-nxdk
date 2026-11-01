#!/usr/bin/env python3
"""Exercise native XID validation, controller handoff and dashboard reset holds."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='xbox-native-controller-') as tmp:
    tmp = Path(tmp)
    source = tmp / 'test.cpp'
    source.write_text(r'''
#include "controller_state.hpp"
#include <cassert>
#include <iostream>
using namespace XboxNativeInput;
Report neutral() { Report r{}; r[1]=20; return r; }
int main() {
    Controllers pads;
    Report output;
    assert(!pads.copyActive(output));
    for (int i=0;i<4;++i) pads.connect(i);
    auto a=neutral(), b=neutral(), n=neutral(); a[4]=255; b[5]=255;
    assert(pads.submit(0,a.data(),20,0));
    assert(pads.activeIndex()==0 && pads.copyActive(output) && output==a);
    assert(pads.submit(1,b.data(),20,1)); assert(pads.activeIndex()==1);
    // Repeated held input and neutral packets must not fight a newer player.
    for (int i=0;i<100;++i) {
        pads.submit(0,a.data(),20,2+i);
        pads.submit(2,n.data(),20,2+i);
        assert(pads.activeIndex()==1);
    }
    a[2]=8; pads.submit(0,a.data(),20,102); assert(pads.activeIndex()==0);
    pads.submit(1,b.data(),20,103); assert(pads.activeIndex()==0);
    a[2]=0; pads.submit(0,a.data(),20,104); assert(pads.activeIndex()==0);
    b[2]=1; pads.submit(1,b.data(),20,105); assert(pads.activeIndex()==1);
    // Stick drift does not steal control; a new direction beyond the deadzone does.
    auto stick=n; stick[12]=0x10; stick[13]=0x27; // exactly 10000
    pads.submit(3,stick.data(),20,106); assert(pads.activeIndex()==1);
    ++stick[12]; pads.submit(3,stick.data(),20,107); assert(pads.activeIndex()==3);
    assert(pads.copyActive(output) && axis(output,12)==10001);
    stick[12]=0; stick[13]=0x80; pads.submit(3,stick.data(),20,108);
    assert(pads.copyActive(output) && axis(output,12)==-32768);
    // Releasing/disconnecting a pad clears its data and lets another pad take over.
    pads.disconnect(3); assert(pads.activeIndex()!=3);
    pads.connect(3); pads.submit(3,n.data(),20,109); assert(pads.activeIndex()!=3);
    stick[13]=0x7f; stick[12]=0xff; pads.submit(3,stick.data(),20,110);
    assert(pads.activeIndex()==3 && pads.copyActive(output) && axis(output,12)==32767);
    // An actual short allocation catches any speculative read beyond xfer_len under ASan.
    for (size_t len=0;len<20;++len) {
        auto *shortReport=new uint8_t[len];
        for(size_t i=0;i<len;++i) shortReport[i]=n[i];
        assert(!pads.submit(3,shortReport,len,111)); delete[] shortReport;
        assert(pads.activeIndex()!=3);
    }
    auto malformed=n; malformed[1]=14;
    assert(!pads.submit(3,malformed.data(),20,112));
    malformed=n; malformed[0]=1;
    assert(!pads.submit(3,malformed.data(),20,112));
    assert(!pads.submit(3,nullptr,20,112));
    assert(!pads.submit(8,n.data(),20,112));
    pads.disconnect(3); assert(!pads.submit(3,n.data(),20,113));

    // A complete Back tap between game polls still requests the console menu.
    Controllers taps;
    taps.connect(0); taps.connect(1);
    auto backTap=n; backTap[2]=0x20;
    taps.submit(0,backTap.data(),20,1);
    taps.submit(0,n.data(),20,2);
    assert(taps.copyActive(output) && output==n);
    assert(taps.consumeBackPress()); assert(!taps.consumeBackPress());
    // Repeated held reports do not create repeated edges.
    taps.submit(0,backTap.data(),20,3); assert(taps.consumeBackPress());
    taps.submit(0,backTap.data(),20,4); assert(!taps.consumeBackPress());
    taps.submit(0,n.data(),20,5);
    // Gameplay/confirmation taps retain live state, not a queued old press.
    taps.submit(0,a.data(),20,6); taps.submit(0,n.data(),20,7);
    assert(taps.copyActive(output) && output==n && !taps.consumeBackPress());
    // Another player's activity does not erase a valid console-menu request.
    taps.submit(0,backTap.data(),20,8); taps.submit(0,n.data(),20,9);
    taps.submit(1,b.data(),20,10); assert(taps.activeIndex()==1);
    assert(taps.consumeBackPress()); assert(!taps.consumeBackPress());
    // Disconnection, malformed data and reconnection cannot leave phantom taps.
    taps.submit(0,backTap.data(),20,11); taps.disconnect(0);
    assert(!taps.consumeBackPress()); taps.connect(0);
    assert(!taps.consumeBackPress());
    taps.submit(0,backTap.data(),20,12); taps.submit(0,n.data(),19,13);
    assert(!taps.consumeBackPress());
    // Invalidating one route must preserve another route's valid Back edge.
    taps.submit(0,backTap.data(),20,14);
    taps.submit(1,backTap.data(),20,15); taps.invalidate(1);
    assert(taps.consumeBackPress()); assert(!taps.consumeBackPress());

    Controllers reset;
    for(int i=0;i<4;++i) reset.connect(i);
    auto chord=n; chord[2]=0x30; chord[10]=chord[11]=255;
    reset.submit(0,chord.data(),20,100);
    assert(!reset.resetRequested(2099)); assert(reset.resetRequested(2100));
    reset.submit(0,n.data(),20,2101); assert(!reset.resetRequested(5000));
    reset.submit(0,chord.data(),20,5001); assert(!reset.resetRequested(7000));
    reset.invalidate(0); assert(!reset.resetRequested(8000));
    reset.submit(0,chord.data(),20,8001); reset.disconnect(0);
    assert(!reset.resetRequested(12000));
    // Separate controllers cannot contribute pieces of a reset chord or share hold time.
    auto start=n, back=n; start[2]=0x10; back[2]=0x20;
    start[10]=start[11]=back[10]=back[11]=255;
    reset.connect(0); reset.submit(0,start.data(),20,12001); reset.submit(1,back.data(),20,12001);
    assert(!reset.resetRequested(20000));
    reset.submit(1,chord.data(),20,20001); assert(!reset.resetRequested(22000));
    assert(reset.resetRequested(22001));
    chord[10]=191; reset.submit(1,chord.data(),20,22002); assert(!reset.resetRequested(30000));
    chord[10]=192; reset.submit(1,chord.data(),20,0xfffffff0u);
    assert(!reset.resetRequested(uint32_t(0xfffffff0u+1999u)));
    assert(reset.resetRequested(uint32_t(0xfffffff0u+2000u)));
    std::cout << "PASS: four-pad handoff, drift/held/neutral reports, hotplug, malformed/short reports, signed axes, per-pad reset/release/error, reserved Back tap retention and clock wrap\n";
}
''')
    exe = tmp / 'test'
    subprocess.run(['c++','-std=c++17','-fsanitize=address,undefined',
                    '-I'+str(root/'include/windowing/nv2a'),str(source),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
