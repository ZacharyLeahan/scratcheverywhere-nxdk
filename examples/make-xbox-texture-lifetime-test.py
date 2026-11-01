"""Generate an offline SB2 regression for texture retirement during pen stamping.

Expected: an unchanged 8-by-6 board of six colored, black-bordered tiles.
R (or the A key) redraws it and increments DRAWS. This diagnostic project is
separate from the twenty-one game qualification projects. Uses only Python 3.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile
import zlib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path, help='New .sb2 output path')
out = parser.parse_args().output
assets = {}


def png(width, height, pixels):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data +
                struct.pack('>I', zlib.crc32(kind + data)))
    rows = b''.join(b'\0' + pixels[y * width * 4:(y + 1) * width * 4]
                    for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def costume(index, name, width, height, pixels):
    data = png(width, height, pixels)
    assets[f'{index}.png'] = data
    return dict(costumeName=name, baseLayerID=index,
                baseLayerMD5=hashlib.md5(data).hexdigest() + '.png',
                bitmapResolution=1, rotationCenterX=width / 2,
                rotationCenterY=height / 2)


backdrop = costume(0, 'background', 480, 360, bytes([24, 24, 24, 255]) * 480 * 360)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (255, 0, 255), (0, 255, 255)]
tiles = []
for index, color in enumerate(colors, 1):
    pixels = b''.join(bytes((*color, 255)) if 4 <= x < 60 and 4 <= y < 60
                      else bytes([0, 0, 0, 255])
                      for y in range(64) for x in range(64))
    tiles.append(costume(index, f'tile {index}', 64, 64, pixels))

read = lambda name: ['readVariable', name]
draw = [['procDef', 'Draw tiles', [], [], True],
        ['setVar:to:', 'DRAW_COMPLETE', 0], ['clearPenTrails'],
        ['setVar:to:', 'row', 0], ['setVar:to:', 'tileY', 100],
        ['doRepeat', 6, [
            ['setVar:to:', 'col', 0], ['setVar:to:', 'tileX', -160],
            ['doRepeat', 8, [
                ['lookLike:', ['+', 1, ['%', ['+', ['*', read('row'), 8], read('col')], 6]]],
                ['gotoX:y:', read('tileX'), read('tileY')], ['stampCostume'],
                ['changeVar:by:', 'tileX', 40], ['changeVar:by:', 'col', 1]]],
            ['changeVar:by:', 'tileY', -40], ['changeVar:by:', 'row', 1]]],
        ['changeVar:by:', 'DRAWS', 1], ['setVar:to:', 'DRAW_COMPLETE', 1]]
actor = dict(objName='Painter', variables=[dict(name=n, value=0, isPersistent=False)
             for n in ['row', 'col', 'tileX', 'tileY']], lists=[], sounds=[],
             scripts=[[10, 10, [['whenGreenFlag'], ['hide'], ['setSizeTo:', 62.5], ['call', 'Draw tiles']]],
                      [10, 160, [['whenKeyPressed', 'r'], ['call', 'Draw tiles']]],
                      [10, 260, [['whenKeyPressed', 'a'], ['call', 'Draw tiles']]],
                      [300, 10, draw]], costumes=tiles, currentCostumeIndex=0,
             scratchX=0, scratchY=0, scale=.625, direction=90,
             rotationStyle='none', isDraggable=False, visible=False)
monitor = dict(target='Stage', cmd='getVar:', param='DRAWS', color=15629590,
               label='DRAWS', mode=1, x=390, y=15, visible=True,
               sliderMin=0, sliderMax=100, isDiscrete=True)
project = dict(objName='Stage', variables=[dict(name=n, value=0, isPersistent=False)
               for n in ['DRAWS', 'DRAW_COMPLETE']], lists=[], sounds=[],
               scripts=[[10, 10, [['whenGreenFlag'], ['doForever', [['wait:elapsed:from:', .1]]]]]],
               costumes=[backdrop], currentCostumeIndex=0, penLayerID=-1,
               tempoBPM=60, videoAlpha=.5, children=[actor, monitor],
               info=dict(swfVersion='v461', spriteCount=1, scriptCount=5))
# Stable ZIP metadata makes repeated generation byte-identical.
with out.open('xb') as destination, zipfile.ZipFile(destination, 'w') as archive:
    contents = {'project.json': json.dumps(project, separators=(',', ':')).encode(), **assets}
    for name, data in contents.items():
        info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, data)
print(out)
