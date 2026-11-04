#!/usr/bin/env python3
"""Compare cached transforms with forced recomputation across mutable inputs."""
from pathlib import Path
import argparse
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--reference', type=Path, help='Optional pre-change renderer.cpp for an additional differential check')
args = parser.parse_args()
source = (root / 'source/renderer.cpp').read_text()
function = source[source.index('void Render::calculateRenderPosition('):source.index('\nvoid Render::setRenderScale()')]
reference = ''
if args.reference:
    previous = args.reference.read_text()
    reference = previous[previous.index('void Render::calculateRenderPosition('):previous.index('\nvoid Render::setRenderScale()')]
    reference = reference.replace('void Render::calculateRenderPosition(', 'void Render::calculateReferencePosition(', 1)
preamble = r'''
#include <runtime/data/entity_components.hpp>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>
struct Costume { double rotationCenterX=16,rotationCenterY=16; int bitmapResolution=1; };
struct Sprite {
    enum Style { NONE, LEFT_RIGHT, ALL_AROUND };
    float size=100,rotation=90;
    double xPosition=50,yPosition=70;
    int currentCostume=0;
    Style rotationStyle=ALL_AROUND;
    int spriteWidth=32,spriteHeight=32;
    std::vector<Costume> costumes{Costume{},Costume{7,11,2}};
    RenderInfo renderInfo{};
};
namespace Scratch { inline bool bitmapHalfQuality=false; inline int projectWidth=480,projectHeight=360; }
namespace Math {
inline unsigned conversions=0;
float degreesToRadians(float d) { ++conversions; return d*3.14159265358979323846f/180; }
}
namespace Render {
enum Mode{TOP_SCREEN_ONLY,BOTH_SCREENS};
inline Mode renderMode=TOP_SCREEN_ONLY;
inline float renderScale=4.f/3;
inline int width=640,height=480;
int getWidth(){return width;} int getHeight(){return height;}
void calculateRenderPosition(Sprite*,bool);
void calculateReferencePosition(Sprite*,bool);
}
'''
checks = r'''
void equal(const Sprite &a,const Sprite &b) {
    const auto &x=a.renderInfo;const auto &y=b.renderInfo;
    assert(x.renderX==y.renderX && x.renderY==y.renderY);
    assert(x.renderScaleX==y.renderScaleX && x.renderScaleY==y.renderScaleY);
    assert(x.renderRotation==y.renderRotation);
}
void check(Sprite &cached,bool svg) {
    Sprite fresh=cached;
    fresh.renderInfo.forceUpdate=true;
    Render::calculateRenderPosition(&fresh,svg);
    Render::calculateRenderPosition(&cached,svg);
    equal(cached,fresh);
#ifdef HAS_REFERENCE
    // The old sentinel scheme failed only at this exact first-render position;
    // the explicit validity flag intentionally fixes that case.
    if (cached.xPosition!=-999999 || cached.yPosition!=-999999) {
        Sprite previous=cached;
        previous.renderInfo.forceUpdate=true;
        Render::calculateReferencePosition(&previous,svg);
        equal(cached,previous);
    }
#endif
    // An immediate repeated call must also preserve the computed result.
    Render::calculateRenderPosition(&cached,svg);
    equal(cached,fresh);
}
uint32_t state=0x19408;
uint32_t random32(){state=state*1664525u+1013904223u;return state;}
int main() {
    Sprite sprite;
    check(sprite,true);
    assert(std::abs(sprite.renderInfo.renderX-(50.f*Render::renderScale+320.f))<.0001f);
    assert(std::abs(sprite.renderInfo.renderY-(-70.f*Render::renderScale+240.f))<.0001f);
    assert(sprite.renderInfo.renderScaleX==Render::renderScale);
    assert(sprite.renderInfo.renderRotation==0);

    // Exact known off-center/flip geometry at a one-to-one viewport.
    Render::width=Scratch::projectWidth;Render::height=Scratch::projectHeight;Render::renderScale=1;
    sprite.currentCostume=1;sprite.costumes[1]={7,11,1};sprite.rotationStyle=Sprite::LEFT_RIGHT;
    sprite.rotation=-90;sprite.xPosition=50;sprite.yPosition=70;
    check(sprite,false);
    assert(sprite.renderInfo.renderX==281); // (32-14)/2 is mirrored: 50-9+240.
    assert(sprite.renderInfo.renderY==115); // 180-(70-(32-22)/2).
    sprite.rotationStyle=Sprite::NONE;check(sprite,false);
    assert(sprite.renderInfo.renderX==299);
    sprite.rotationStyle=Sprite::ALL_AROUND;sprite.rotation=90;check(sprite,false);
    assert(sprite.renderInfo.renderX==299 && sprite.renderInfo.renderRotation==0);

    // Same costume index can acquire new crop/dimensions during image reload.
    sprite.spriteWidth=47;sprite.spriteHeight=59;check(sprite,true);
    sprite.costumes[1].rotationCenterX=11.25;check(sprite,true);
    sprite.costumes[1].rotationCenterY=17.125;check(sprite,true);
    sprite.costumes[1].bitmapResolution=2;check(sprite,false);
    Scratch::bitmapHalfQuality=true;check(sprite,false);check(sprite,true);
    sprite.rotationStyle=Sprite::LEFT_RIGHT;check(sprite,true);
    sprite.rotation=90;check(sprite,true);sprite.rotation=-90;check(sprite,true);
    sprite.currentCostume=0;check(sprite,true);

    // Coordinate cache must retain the source double, including fractional
    // values and the former sentinel coordinate on a first render.
    Sprite sentinel;sentinel.xPosition=sentinel.yPosition=-999999;
    check(sentinel,true);
    assert(sentinel.renderInfo.renderX!=-999999 && sentinel.renderInfo.renderX!=0);
    sprite.xPosition=0.1;sprite.yPosition=-0.2;check(sprite,true);
#ifdef __XBOX__
    assert(sprite.renderInfo.oldX==sprite.xPosition && sprite.renderInfo.oldY==sprite.yPosition);
#endif

    bool svg=true;
    for (unsigned i=0;i<30000;++i) {
        switch(random32()%18) {
        case 0:sprite.xPosition=(int(random32()%200000)-100000)/13.7;break;
        case 1:sprite.yPosition=(int(random32()%200000)-100000)/17.3;break;
        case 2:sprite.size=(random32()%8000)/17.f;break;
        case 3:sprite.rotation=(int(random32()%144000)-72000)/100.f;break;
        case 4:sprite.rotationStyle=static_cast<Sprite::Style>(random32()%3);break;
        case 5:sprite.currentCostume=random32()%2;break;
        case 6:sprite.spriteWidth=1+random32()%400;sprite.spriteHeight=1+random32()%400;break;
        case 7:sprite.costumes[sprite.currentCostume].rotationCenterX=(random32()%8000)/19.;break;
        case 8:sprite.costumes[sprite.currentCostume].rotationCenterY=(random32()%8000)/23.;break;
        case 9:sprite.costumes[sprite.currentCostume].bitmapResolution=1+random32()%2;break;
        case 10:svg=!svg;break;
        case 11:Scratch::bitmapHalfQuality=!Scratch::bitmapHalfQuality;break;
        case 12:Render::width=320+random32()%1000;Render::height=240+random32()%600;break;
        case 13:Scratch::projectWidth=240+random32()%700;Scratch::projectHeight=180+random32()%400;break;
        case 14:Render::renderMode=static_cast<Render::Mode>(random32()%2);break;
        case 15:Render::renderScale=.25f+(random32()%400)/100.f;break;
        case 16:sprite.renderInfo.forceUpdate=true;break;
        default:break; // Unchanged frame, including fractional positions.
        }
        check(sprite,svg);
        if(i%47==0){Sprite clone=sprite;clone.xPosition+=1.25;check(clone,svg);}
    }
#ifdef __XBOX__
    // The old reciprocal invalidation performed 1000 angle conversions here.
    Sprite steady;Math::conversions=0;
    for(unsigned i=0;i<1000;++i)Render::calculateRenderPosition(&steady,true);
    assert(Math::conversions==1);
    for(unsigned i=0;i<1000;++i){steady.xPosition+=.3;Render::calculateRenderPosition(&steady,true);}
    assert(Math::conversions==1); // Scrolling does not change size or rotation.
    steady.rotation+=1;Render::calculateRenderPosition(&steady,true);assert(Math::conversions==2);
    steady.rotationStyle=Sprite::NONE;Render::calculateRenderPosition(&steady,true);
    steady.rotationStyle=Sprite::ALL_AROUND;Render::calculateRenderPosition(&steady,true);assert(Math::conversions==3);
    steady.renderInfo.forceUpdate=true;Render::calculateRenderPosition(&steady,true);assert(Math::conversions==4);
#endif
    std::puts("PASS: forced-recompute equivalence, geometry/style/viewport/quality invalidation, fractional coordinates, copied clones, unchanged/scrolling reuse");
}
'''
with tempfile.TemporaryDirectory(prefix='render-transform-cache-') as tmp:
    tmp = Path(tmp)
    (tmp / 'se_export.hpp').write_text('#define SE_EXPORT\n')
    (tmp / 'test.cpp').write_text(('#define HAS_REFERENCE\n' if reference else '') + preamble + reference + function + checks)
    for mode in ['xbox', 'other']:
        binary = tmp / mode
        flags = ['-D__XBOX__'] if mode == 'xbox' else []
        subprocess.run(['c++', '-std=c++17', '-O2', '-fsanitize=address,undefined', *flags,
                        '-I'+str(tmp), '-I'+str(root/'include'), str(tmp/'test.cpp'), '-o', str(binary)], check=True)
        # The non-Xbox cache has preexisting behavior for style/geometry changes;
        # only check its preprocessing/build, leaving that path unchanged.
        if mode == 'xbox':
            subprocess.run([str(binary)], check=True)
print('PASS: Xbox runtime check and non-Xbox compile under ASan/UBSan')
