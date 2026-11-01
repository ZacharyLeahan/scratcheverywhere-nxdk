"""Generate independent native Xbox brightness/transparency GPU samples.

Run: python3 examples/make-nv2a-brightness-test.py /tmp/fx.sb3
The companion expected JSON contains 60 solid-centre RGB checks. Rows cover
normal, large-image, pixelate, mosaic, deformed, combined and SVG drawing;
columns vary hue, brightness and ghost. Uniform source colour makes each
expected centre independent of the geometry implementation.

The large-image row exercises tiles only with the expanded rendering policy;
standard policy downsizes it. native_xy assumes a 1280x960 xemu screenshot with
5% overscan; scratch_xy supports other capture sizes. This is a rendering
fixture, not a qualification game or a memory-detection test.
"""
from pathlib import Path
import colorsys, hashlib, json, struct, zlib, zipfile, sys
out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('NV2A-Brightness-Test.sb3')
assets = {}

def costume(name, w, h, svg=False):
    if svg:
        data = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="rgb(80,150,220)" fill-opacity="0.5019607843"/></svg>'.encode()
        ext = 'svg'
    else:

        def chunk(k, d):
            return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k + d) & 4294967295)
        raw = b''.join((b'\x00' + bytes([80, 150, 220, 128]) * w for _ in range(h)))
        data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
        ext = 'png'
    digest = hashlib.md5(data).hexdigest()
    assets[digest + '.' + ext] = data
    return dict(name=name, assetId=digest, md5ext=digest + '.' + ext, dataFormat=ext, bitmapResolution=1, rotationCenterX=w / 2, rotationCenterY=h / 2)
base = costume('POT', 128, 128)
npot = costume('NPOT', 96, 96)
large = costume('Tiled', 520, 80)
vector = costume('SVG', 128, 128, True)
back = b'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#102030"/></svg>'
digest = hashlib.md5(back).hexdigest()
assets[digest + '.svg'] = back
background = dict(name='Background', assetId=digest, md5ext=digest + '.svg', dataFormat='svg', bitmapResolution=1, rotationCenterX=240, rotationCenterY=180)
common = dict(variables={}, lists={}, broadcasts={}, comments={}, currentCostume=0, sounds=[], volume=100)
stage = dict(common, isStage=True, name='Stage', blocks={}, costumes=[background], layerOrder=0, tempo=60, videoTransparency=50, videoState='off', textToSpeechLanguage=None)
targets = [stage]
samples = []
paths = [('normal', base, 20, {}), ('tiled', large, 6, {}), ('fine-pixel', base, 20, {'PIXELATE': 10}), ('pixel-mesh', base, 20, {'PIXELATE': 500}), ('pixel-baked', base, 20, {'PIXELATE': 50}), ('mosaic-wrap', base, 20, {'MOSAIC': 50}), ('mosaic-grid', npot, 26.6666666667, {'MOSAIC': 50}), ('deformed', base, 20, {'WHIRL': 90, 'FISHEYE': 30}), ('combined', base, 20, {'WHIRL': 90, 'MOSAIC': 50, 'PIXELATE': 50}), ('svg', vector, 20, {})]
cases = [(0, -50, 0), (0, 50, 0), (0, 100, 50), (0, -100, 50), (35, 25, 50), (105, -25, 0)]
for (row, (path, cost, size, fx)) in enumerate(paths):
    for (col, (hue, brightness, ghost)) in enumerate(cases):
        x = -200 + 80 * col
        y = 145 - 32 * row
        name = f'{path}-{col}'
        effects = {'COLOR': hue, 'BRIGHTNESS': brightness, 'GHOST': ghost, **fx}
        bs = {}
        keys = ['flag'] + list(effects)
        bs['flag'] = dict(opcode='event_whenflagclicked', next=keys[1], parent=None, inputs={}, fields={}, shadow=False, topLevel=True, x=20, y=20)
        for (i, (effect, val)) in enumerate(effects.items(), 1):
            bs[effect] = dict(opcode='looks_seteffectto', next=keys[i + 1] if i + 1 < len(keys) else None, parent=keys[i - 1], inputs={'VALUE': [1, [4, str(val)]]}, fields={'EFFECT': [effect, None]}, shadow=False, topLevel=False)
        targets.append(dict(common, isStage=False, name=name, blocks=bs, costumes=[cost], layerOrder=len(targets), visible=True, x=x, y=y, size=size, direction=90, draggable=False, rotationStyle='all around'))
        rgb = [80 / 255, 150 / 255, 220 / 255]
        if hue:
            (h, s, v) = colorsys.rgb_to_hsv(*rgb)
            rgb = list(colorsys.hsv_to_rgb((h + hue / 200) % 1, s, v))
        rgb = [max(0, min(255, c * 255 + brightness * 2.55)) for c in rgb]
        alpha = 128 / 255 * (1 - ghost / 100)
        expected = [round(c * alpha + b * (1 - alpha)) for (c, b) in zip(rgb, [16, 32, 48])]
        samples.append(dict(name=name, scratch_xy=[x, y], native_xy=[round(640 + x * 2.4), round(480 - y * 2.4)], expected=expected, tolerance=9))
project = dict(targets=targets, monitors=[], extensions=[], meta={'semver': '3.0.0', 'vm': '1.1.2', 'agent': 'Independent native brightness draw-path integration check'})
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('project.json', json.dumps(project))
    for (n, data) in assets.items():
        z.writestr(n, data)
out.with_suffix('.expected.json').write_text(json.dumps({'background': [16, 32, 48], 'samples': samples}, indent=2) + '\n')
print('60 independent path/color samples prepared')
