#!/usr/bin/env python3
"""Exercise the real switchCostume fast path with controlled image/cache state."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
source = (root/'source/runtime/runtime_costumes.cpp').read_text()
function = source[source.index('void Scratch::switchCostume('):source.index('void Scratch::loadCurrentCostumeImage(')]
with tempfile.TemporaryDirectory(prefix='xbox-costume-cache-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.cpp').write_text(r'''
#define __XBOX__
#include <algorithm>
#include <cassert>
#include <cmath>
#include <limits>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>
struct Image { int width=30,height=40; float x=0,y=0; unsigned freeTimer=30; const unsigned maxFreeTimer=30;
int getWidth(){return width;} int getHeight(){return height;}
std::pair<float,float> getSVGViewOffset()const{return {x,y};}};
struct Costume {std::string fullName;float imageViewOffsetX=0,imageViewOffsetY=0;};
struct Sprite {int currentCostume=0,loadedCostumeIndex=-1,spriteWidth=0,spriteHeight=0;
float size=100,loadedCostumeRequestScale=-1;bool visible=true;std::vector<Costume> costumes{{"one"},{"two"}};};
namespace Render {enum{BOTH_SCREENS,OTHER};int renderMode=OTHER,width=640,height=480;
int getWidth(){return width;}int getHeight(){return height;}}
class Scratch {public:
inline static bool forceRedraw=false;inline static int projectWidth=480,projectHeight=360,loads=0;
inline static std::vector<Sprite*>sprites;
inline static std::unordered_map<std::string,std::shared_ptr<Image>>costumeImages;
static void freeUnusedCostumeImages(){}
static void switchCostume(Sprite*,double);
static void loadCurrentCostumeImage(Sprite*s){++loads;
auto &image=costumeImages[s->costumes[s->currentCostume].fullName];if(!image)image=std::make_shared<Image>();
s->spriteWidth=image->width;s->spriteHeight=image->height;
auto &costume=s->costumes[s->currentCostume];costume.imageViewOffsetX=image->x;costume.imageViewOffsetY=image->y;
s->loadedCostumeIndex=s->currentCostume;
s->loadedCostumeRequestScale=(s->size/100)*std::min(float(Render::width)/projectWidth,float(Render::renderMode==Render::BOTH_SCREENS?480:Render::height)/projectHeight);}
};
'''+function+r'''
int main(){
Sprite s;Scratch::sprites={&s};
Scratch::switchCostume(&s,0);assert(Scratch::loads==1);
Scratch::forceRedraw=false;Scratch::switchCostume(&s,0);assert(Scratch::loads==1&&Scratch::forceRedraw);
s.visible=false;Scratch::forceRedraw=false;Scratch::switchCostume(&s,0);assert(Scratch::loads==1&&!Scratch::forceRedraw);
s.size=200;Scratch::switchCostume(&s,0);assert(Scratch::loads==2);
Render::width=800;Render::height=600;Scratch::switchCostume(&s,0);assert(Scratch::loads==3);
Scratch::costumeImages["one"]->width=50;Scratch::switchCostume(&s,0);assert(Scratch::loads==4&&s.spriteWidth==50);
Scratch::costumeImages["one"]->x=4;Scratch::switchCostume(&s,0);assert(Scratch::loads==5&&s.costumes[0].imageViewOffsetX==4);
Scratch::switchCostume(&s,1);assert(Scratch::loads==6&&s.loadedCostumeIndex==1);
// Some authored blocks increment currentCostume before calling switchCostume.
s.currentCostume=0;Scratch::switchCostume(&s,0);assert(Scratch::loads==7&&s.loadedCostumeIndex==0);
Scratch::costumeImages.erase("one");Scratch::switchCostume(&s,0);assert(Scratch::loads==8);
Scratch::switchCostume(&s,-1);assert(s.currentCostume==1);
Scratch::switchCostume(&s,std::numeric_limits<double>::infinity());assert(s.currentCostume==0);
s.loadedCostumeIndex=-1;int previous=Scratch::loads;
Scratch::switchCostume(&s,0);assert(Scratch::loads==previous+1);
}
''')
    subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined',str(tmp/'test.cpp'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
print('PASS: redundant assignment, redraw, size/viewport, image/crop changes, costume changes, eviction, wrapping')
