#!/usr/bin/env python3
"""Check listener indexing preserves matches/order without rescanning hats."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='broadcast-index-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.cpp').write_text(r'''
#include "broadcast_index.hpp"
#include <cassert>
struct Block { std::string name; };
int main() {
    Block a{"Game Loop - Scroll"}, b{"other"}, c{"GAME LOOP - SCROLL"};
    std::vector<Block*> hats{&a,&b,&c};
    BroadcastHatIndex index;
    int reads=0;
    const auto name=[&](Block *hat) { ++reads; return hat->name; };
    const auto &matches=index.lookup("game loop - scroll",hats,name);
    assert((matches==std::vector<Block*>{&a,&c}));
    assert(reads==3);
    for(int clone=0;clone<200;++clone) {
        assert(index.lookup("game loop - scroll",hats,name)==matches);
        assert(index.lookup("missing",hats,name).empty());
        assert(index.lookup("other",hats,name)==std::vector<Block*>{&b});
    }
    assert(reads==3);
    BroadcastHatIndex nextProject;
    std::vector<Block*> different{&b};
    assert(nextProject.lookup("other",different,name)==different);
    BroadcastHatIndex empty;
    assert(empty.lookup("anything",std::vector<Block*>{},name).empty());
}
''')
    subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined','-I'+str(root/'include/runtime'),str(tmp/'test.cpp'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
print('PASS: case-insensitive matches, listener order, clone reuse, missing events, project isolation')
