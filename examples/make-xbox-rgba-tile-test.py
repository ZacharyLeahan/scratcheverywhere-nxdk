"""Generate an offline large-SVG fixture for Xbox RGBA tile uploads.

A changes costumes and increments SWAPS. The 900x660 costumes display at 50%,
so their 480p rasterization exceeds the Xbox renderer's 512-pixel tile threshold.
This is a rendering diagnostic, not a game-pack entry. Uses only Python 3.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path, help="New .sb3 output path")
output = parser.parse_args().output
assets = {}


def costume(name, text, width, height):
    data = text.encode()
    asset = hashlib.md5(data).hexdigest()
    assets[asset + ".svg"] = data
    return dict(name=name, assetId=asset, md5ext=asset + ".svg", dataFormat="svg",
                rotationCenterX=width / 2, rotationCenterY=height / 2)


backdrop = costume("Background", '<svg xmlns="http://www.w3.org/2000/svg" '
                   'width="480" height="360"><rect width="480" height="360" '
                   'fill="#18202b"/></svg>', 480, 360)
costumes = []
for index, colors in enumerate([("#ff2030", "#2050ff", "#20ee90"),
                                ("#20ee90", "#ff2030", "#2050ff")]):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="660">'
           '<defs><linearGradient id="g"><stop stop-color="' + colors[0] + '"/>'
           '<stop offset="0.5" stop-color="' + colors[1] + '"/>'
           '<stop offset="1" stop-color="' + colors[2] + '"/></linearGradient>'
           '<pattern id="p" width="12" height="12" patternUnits="userSpaceOnUse">'
           '<rect width="12" height="12" fill="white"/>'
           '<rect width="6" height="6" fill="black"/>'
           '<rect x="6" y="6" width="6" height="6" fill="black"/></pattern></defs>'
           '<rect width="900" height="660" fill="url(#g)"/>'
           '<rect x="24" y="230" width="852" height="190" fill="url(#p)"/>'
           '<rect x="8" y="8" width="884" height="644" fill="none" '
           'stroke="white" stroke-width="8"/>'
           '<path d="M256 0V660M512 0V660M768 0V660M0 256H900M0 512H900" '
           'stroke="white" stroke-width="2"/></svg>')
    costumes.append(costume("Pattern " + str(index + 1), svg, 900, 660))


def block(opcode, next=None, parent=None, inputs=None, fields=None, top=False):
    result = dict(opcode=opcode, next=next, parent=parent, inputs=inputs or {},
                  fields=fields or {}, shadow=False, topLevel=top)
    if top:
        result.update(x=20, y=20)
    return result


number = lambda n: [1, [4, str(n)]]
blocks = {
    "flag": block("event_whenflagclicked", "reset", top=True),
    "reset": block("data_setvariableto", parent="flag",
                   inputs={"VALUE": number(0)}, fields={"VARIABLE": ["SWAPS", "swaps"]}),
    "key": block("event_whenkeypressed", "next", fields={"KEY_OPTION": ["a", None]}, top=True),
    "next": block("looks_nextcostume", "count", "key"),
    "count": block("data_changevariableby", parent="next",
                   inputs={"VALUE": number(1)}, fields={"VARIABLE": ["SWAPS", "swaps"]}),
}
common = dict(lists={}, broadcasts={}, comments={}, currentCostume=0, sounds=[], volume=100)
stage = dict(common, isStage=True, name="Stage", variables={"swaps": ["SWAPS", 0]},
             blocks={}, costumes=[backdrop], layerOrder=0, tempo=60,
             videoTransparency=50, videoState="off", textToSpeechLanguage=None)
actor = dict(common, isStage=False, name="Large pattern", variables={}, blocks=blocks,
             costumes=costumes, layerOrder=1, visible=True, x=0, y=0, size=50,
             direction=90, draggable=False, rotationStyle="don't rotate")
monitor = dict(id="swaps", mode="default", opcode="data_variable",
               params={"VARIABLE": "SWAPS"}, spriteName=None, value=0,
               width=0, height=0, x=5, y=5, visible=True,
               sliderMin=0, sliderMax=100, isDiscrete=True)
project = dict(targets=[stage, actor], monitors=[monitor], extensions=[],
               meta={"semver": "3.0.0", "vm": "0.2.0", "agent": "Xbox RGBA tile fixture"})
with output.open("xb") as destination, zipfile.ZipFile(destination, "w") as archive:
    contents = {"project.json": json.dumps(project, separators=(",", ":")).encode(), **assets}
    for name, data in contents.items():
        info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, data)
print(output)
