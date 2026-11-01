#!/usr/bin/env python3
"""Keep cycling HUD digits cached while evicting genuinely inactive images."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
source = (root/'source/runtime/runtime_costumes.cpp').read_text()
function = source[source.index('void Scratch::flushCostumeImages()'):source.index('void Scratch::freeUnusedCostumeImages(')]
with tempfile.TemporaryDirectory(prefix='costume-cache-lifetime-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.cpp').write_text(r'''
#define __XBOX__
#include <cassert>
#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
struct Image {unsigned int freeTimer=30;const unsigned int maxFreeTimer=30;};
struct Costume {std::string fullName;int *collisionMask=nullptr;};
struct Sprite {int currentCostume=0;std::vector<Costume>costumes;};
class Scratch {public:
inline static std::vector<Sprite*>sprites;
inline static std::unordered_map<std::string,std::shared_ptr<Image>>costumeImages;
static void flushCostumeImages();};
'''+function+r'''
int main(){
Sprite hud;int mask=1;
for(int i=0;i<10;++i){const std::string name=std::to_string(i);hud.costumes.push_back({name,&mask});Scratch::costumeImages[name]=std::make_shared<Image>();}
hud.costumes.push_back({"inactive",&mask});
Scratch::sprites={&hud};
Scratch::costumeImages["inactive"]=std::make_shared<Image>();
Scratch::costumeImages["SE__Missingno"]=std::make_shared<Image>();
// Revisit each digit every ten frames, for much longer than its thirty-frame TTL.
for(int frame=0;frame<300;++frame){
 hud.currentCostume=frame%10;Scratch::flushCostumeImages();
 for(int i=0;i<10;++i)assert(Scratch::costumeImages.count(std::to_string(i))==1);
}
assert(!Scratch::costumeImages.count("inactive"));assert(hud.costumes[10].collisionMask==nullptr);
for(int i=0;i<10;++i)assert(hud.costumes[i].collisionMask==&mask);
Scratch::sprites.clear();for(int i=0;i<30;++i)Scratch::flushCostumeImages();
assert(Scratch::costumeImages.size()==1&&Scratch::costumeImages.count("SE__Missingno"));
}
''')
    subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined',str(tmp/'test.cpp'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
print('PASS: repeated digit reuse survives TTL; inactive images evict and invalidate masks; fallback survives')
