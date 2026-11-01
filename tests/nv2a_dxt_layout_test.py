"""Check compressed texture selectors, edge replication, pitches and aliasing."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = r'''
#include "dxt_layout.hpp"
#include <cassert>
#include <cstdio>
#include <vector>
#include <algorithm>
#include <cstdint>

static unsigned selector(const uint8_t *bytes, int first, int count) {
    unsigned value=0;
    for (int k=0;k<count;++k) value|=((bytes[(first+k)/8]>>((first+k)%8))&1u)<<k;
    return value;
}
static void bits(uint8_t *bytes,int first,int count,unsigned value) {
    for(int k=0;k<count;++k) {
        const int bit=first+k; const uint8_t mask=uint8_t(1u<<(bit%8));
        bytes[bit/8]=uint8_t((bytes[bit/8]&~mask)|(((value>>k)&1u)<<(bit%8)));
    }
}
static int pot(int n) {int p=1;while(p<n)p*=2;return p;}
static void check(int w,int h,bool dxt5,int mode) {
    const int block=dxt5?16:8, coff=dxt5?8:0;
    const int cols=(w+3)/4,rows=(h+3)/4,pitch=cols*block+8;
    const size_t inputBytes=size_t(rows-1)*pitch+cols*block;
    std::vector<uint8_t> input(inputBytes,0xD3);
    for(int by=0;by<rows;++by)for(int bx=0;bx<cols;++bx) {
        auto *p=input.data()+by*pitch+bx*block;
        const uint32_t tag=uint32_t(by*cols+bx)*1103515245u+12345u;
        for(int k=0;k<4;++k)p[coff+k]=uint8_t(tag>>(8*k));
        if(dxt5){p[0]=uint8_t(tag);p[1]=uint8_t(tag>>8);}
        for(int y=0;y<4;++y)for(int x=0;x<4;++x){
            bits(p+coff+4,(y*4+x)*2,2,unsigned(x+3*y+bx+by)%4);
            if(dxt5)bits(p+2,(y*4+x)*3,3,unsigned(3*x+5*y+3*bx+by)%8);
        }
    }
    const auto layout=NV2ADxtLayout::make(w,h,dxt5);
    assert(layout.width==std::max(dxt5?16:32,pot(w)));
    assert(layout.height==std::max(4,pot(h)));
    assert(layout.pitch==layout.width/4*block && layout.pitch%64==0);
    const size_t outputBytes=size_t(layout.pitch)*(layout.height/4);
    int offset=mode==1?0:mode==2?16:-16;
    size_t destAt=32+size_t(std::max(0,-offset)),sourceAt=size_t(int(destAt)+offset);
    std::vector<uint8_t> storage(std::max(destAt+outputBytes,sourceAt+inputBytes)+32,0xA5);
    const uint8_t *src=input.data();
    if(mode){std::copy(input.begin(),input.end(),storage.begin()+sourceAt);src=storage.data()+sourceAt;}
    const auto before=storage;
    assert(NV2ADxtLayout::upload(storage.data()+destAt,layout,src,pitch,w,h,dxt5));
    for(size_t i=0;i<storage.size();++i)if(i<destAt||i>=destAt+outputBytes)assert(storage[i]==before[i]);
    for(int y=0;y<layout.height;++y)for(int x=0;x<layout.width;++x) {
        const int sx=std::min(x,w-1),sy=std::min(y,h-1);
        const uint8_t *expected=input.data()+size_t(sy/4)*pitch+(sx/4)*block;
        const uint8_t *actual=storage.data()+destAt+size_t(y/4)*layout.pitch+(x/4)*block;
        for(int k=0;k<4;++k)assert(actual[coff+k]==expected[coff+k]);
        assert(selector(actual+coff+4,((y%4)*4+x%4)*2,2)==selector(expected+coff+4,((sy%4)*4+sx%4)*2,2));
        if(dxt5){assert(actual[0]==expected[0]&&actual[1]==expected[1]);assert(selector(actual+2,((y%4)*4+x%4)*3,3)==selector(expected+2,((sy%4)*4+sx%4)*3,3));}
    }
}
int main() {
    const int dims[]={1,2,3,4,5,7,8,9,15,16,17,31,32,33,63,64,65,127,128,129};
    unsigned cases=0;
    for(bool dxt5:{false,true})for(int w:dims)for(int h:dims)for(int mode=0;mode<4;++mode){check(w,h,dxt5,mode);++cases;}
    for(bool dxt5:{false,true})for(int mode=0;mode<4;++mode){check(1024,1,dxt5,mode);check(1,1024,dxt5,mode);cases+=2;}
    uint8_t data[256]={};const auto layout=NV2ADxtLayout::make(4,4,false);
    assert(!NV2ADxtLayout::upload(nullptr,layout,data,8,4,4,false));
    assert(!NV2ADxtLayout::upload(data,layout,nullptr,8,4,4,false));
    assert(!NV2ADxtLayout::upload(data,layout,data,7,4,4,false));
    assert(!NV2ADxtLayout::upload(data,layout,data,8,0,4,false));
    std::printf("PASS: %u DXT layouts: selector/endpoint edges, row pitches, guarded writes, exact final source row and three overlap modes (ASan/UBSan)\n",cases);
}
'''
with tempfile.TemporaryDirectory(prefix="nv2a-dxt-") as folder:
    folder = Path(folder)
    (folder / "test.cpp").write_text(source)
    exe = folder / "test"
    subprocess.run(["clang++", "-std=c++17", "-O1", "-fsanitize=address,undefined", "-g",
                    "-I", str(root / "source/renderers/nv2a"), str(folder / "test.cpp"),
                    "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
