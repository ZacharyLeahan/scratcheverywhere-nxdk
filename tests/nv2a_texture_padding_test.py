"""Check native texture interiors, filtered borders, row pitches and bounds."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="nv2a-padding-") as temporary:
    work = Path(temporary)
    source = work / "padding.c"
    source.write_text(r'''#include "swizzle.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned pot(unsigned n) { unsigned p=1; while(p<n) p*=2; return p; }
static void check(unsigned w, unsigned h, unsigned bpp) {
    const unsigned dw=pot(w), dh=pot(h), pitch=w*bpp+8;
    const size_t source_bytes=(size_t)pitch*h, bytes=(size_t)dw*dh*bpp;
    uint8_t *src=malloc(source_bytes), *saved=malloc(source_bytes);
    uint8_t *guarded=malloc(bytes+64), *linear=malloc(bytes), *original=malloc(bytes);
    assert(src && saved && guarded && linear && original);
    memset(src,0xD3,source_bytes); memset(guarded,0xA5,bytes+64);
    for(unsigned y=0;y<h;y++) for(unsigned x=0;x<w;x++)
        for(unsigned k=0;k<bpp;k++) src[y*pitch+x*bpp+k]=(x*37+y*59+k*83)&255;
    memcpy(saved,src,source_bytes);
    memset(original,0xA5,bytes);
    swizzle_subrect(src,w,h,dw,dh,original,pitch,bpp);
    swizzle_subrect_clamped(src,w,h,dw,dh,guarded+32,pitch,bpp);
    unswizzle_rect(guarded+32,dw,dh,linear,dw*bpp,bpp);
    for(unsigned y=0;y<dh;y++) for(unsigned x=0;x<dw;x++) {
        const int content=x<w && y<h;
        const int right=w<dw && x==w && y<h;
        const int bottom=h<dh && y==h && x<(w+(w<dw));
        for(unsigned k=0;k<bpp;k++) {
            const unsigned sx=x<w?x:w-1, sy=y<h?y:h-1;
            uint8_t expected=(content||right||bottom)?src[sy*pitch+sx*bpp+k]:0xA5;
            assert(linear[(y*dw+x)*bpp+k]==expected);
        }
    }
    if(w==dw && h==dh) assert(memcmp(original,guarded+32,bytes)==0);
    for(unsigned n=0;n<32;n++) assert(guarded[n]==0xA5 && guarded[32+bytes+n]==0xA5);
    assert(memcmp(src,saved,source_bytes)==0);
    // A subsequent upload must replace the border too, not leave stale colors.
    memset(src,0x73,source_bytes);
    swizzle_subrect_clamped(src,w,h,dw,dh,guarded+32,pitch,bpp);
    unswizzle_rect(guarded+32,dw,dh,linear,dw*bpp,bpp);
    const unsigned ew=w+(w<dw), eh=h+(h<dh);
    for(unsigned y=0;y<eh;y++) for(unsigned x=0;x<ew;x++)
        for(unsigned k=0;k<bpp;k++) assert(linear[(y*dw+x)*bpp+k]==0x73);
    free(src);free(saved);free(guarded);free(linear);free(original);
}
int main(void) {
    const unsigned shapes[][2]={{1,1},{1,17},{17,1},{3,5},{82,82},{88,88},{31,33},{256,128},{511,257}};
    for(unsigned bpp=1;bpp<=4;bpp*=2)
        for(unsigned i=0;i<sizeof(shapes)/sizeof(shapes[0]);i++)check(shapes[i][0],shapes[i][1],bpp);
    puts("PASS: 27 texture shapes/formats, interiors, one-texel borders, pitched rows, repeated updates and guards (ASan/UBSan)");
}
''')
    exe = work / "padding"
    subprocess.run(["clang", "-std=c11", "-fsanitize=address,undefined", "-g",
                    "-I", str(root / "include/renderers/nv2a"), str(source),
                    str(root / "source/renderers/nv2a/swizzle.c"), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
