#!/usr/bin/env python3
"""Add an Xbox X-to-CPU menu shortcut to a separate prepared Scratch copy.

Original targets, game logic and assets are preserved. Adds one helper sprite,
one controls-hint SVG, a sidecar profile and a provenance receipt. This does
not add simultaneous multi-controller support or qualify performance/audio.
Beach Volleyball uses the original Easy CPU setting. Existing mouse menus remain.
"""
import argparse
import copy
import hashlib
import json
import pathlib
import zipfile
SPECS = {'beach-volleyball': ('Beach-Volleyball', 'Beach Volleyball', 'Make Menu', 'Begin match', 'Against CPU?', 'DIFFICULTY'), 'glowball': ('GlowBall', 'GlowBall', 'Menu', 'CPU', 'against cpu', None)}

class Blocks:

    def __init__(self):
        self.blocks = {}
        self.n = 0

    def add(self, op, inputs=None, fields=None, shadow=False):
        self.n += 1
        k = 'xbox_cpu_' + str(self.n)
        self.blocks[k] = dict(opcode=op, next=None, parent=None, inputs=inputs or {}, fields=fields or {}, shadow=shadow, topLevel=False)
        return k

    def chain(self, *ids):
        for (a, b) in zip(ids, ids[1:]):
            self.blocks[a]['next'] = b
            self.blocks[b]['parent'] = a
        return ids[0]

    def hat(self, op, fields, body):
        k = self.add(op, fields=fields)
        self.blocks[k].update(topLevel=True, x=20, y=self.n * 10, next=body)
        self.blocks[body]['parent'] = k
        return k

    def set(self, name, i, value):
        return self.add('data_setvariableto', {'VALUE': [1, [10, str(value)]]}, {'VARIABLE': [name, i]})

    def broadcast(self, name, i):
        return self.add('event_broadcast', {'BROADCAST_INPUT': [1, [11, name, i]]})

def prepare(game, source, output):
    (name, title, menu, begin, modevar, difficulty) = SPECS[game]
    source = pathlib.Path(source)
    output = pathlib.Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('Keep the original archive; choose a separate output path.')
    if any((p.exists() for p in (output, pathlib.Path(str(output) + '.json'), pathlib.Path(str(output) + '.preparation.json')))):
        raise ValueError('Choose new output paths; existing prepared files are never overwritten.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as z:
        raw = z.read('project.json')
        p = json.loads(raw)
        files = {n: z.read(n) for n in z.namelist() if n != 'project.json'}
    if any((t.get('name') == 'Xbox CPU menu shortcut' for t in p['targets'])):
        raise ValueError('This archive already has the CPU shortcut.')
    stage = p['targets'][0]
    lookup = {v[0]: k for (k, v) in stage['variables'].items()}
    bid = {v: k for (k, v) in stage['broadcasts'].items()}
    for t in p['targets']:
        for block in t['blocks'].values():
            if isinstance(block, dict) and block.get('opcode') == 'event_whenbroadcastreceived':
                field = block['fields']['BROADCAST_OPTION']
                bid[field[0]] = field[1]
    off = 'Begin match' if name == 'Beach-Volleyball' else 'Menu OFF'
    if not all((n in bid for n in (menu, begin, off))) or modevar not in lookup or (difficulty and difficulty not in lookup):
        raise ValueError('Unexpected project revision: required CPU-menu variables or broadcasts are missing.')
    active = 'xbox_cpu_active'
    b = Blocks()
    activate = b.chain(b.set('Xbox CPU menu active', active, 1), b.add('looks_show'))
    b.hat('event_whenflagclicked', {}, activate)
    activate = b.chain(b.set('Xbox CPU menu active', active, 1), b.add('looks_show'))
    b.hat('event_whenbroadcastreceived', {'BROADCAST_OPTION': [menu, bid[menu]]}, activate)
    off = 'Begin match' if name == 'Beach-Volleyball' else 'Menu OFF'
    deactivate = b.chain(b.set('Xbox CPU menu active', active, 0), b.add('looks_hide'))
    b.hat('event_whenbroadcastreceived', {'BROADCAST_OPTION': [off, bid[off]]}, deactivate)
    keymenu = b.add('sensing_keyoptions', fields={'KEY_OPTION': ['c', None]}, shadow=True)
    key = b.add('sensing_keypressed', {'KEY_OPTION': [1, keymenu]})
    b.blocks[keymenu]['parent'] = key
    neg = b.add('operator_not', {'OPERAND': [2, key]})
    b.blocks[key]['parent'] = neg
    wait = b.add('control_wait_until', {'CONDITION': [2, neg]})
    b.blocks[neg]['parent'] = wait
    acts = [wait, b.set('Xbox CPU menu active', active, 0), b.add('looks_hide'), b.set(modevar, lookup[modevar], 1)]
    if difficulty:
        acts.append(b.set(difficulty, lookup[difficulty], 1))
    acts.append(b.broadcast(begin, bid[begin]))
    body = b.chain(*acts)
    cond = b.add('operator_equals', {'OPERAND1': [3, [12, 'Xbox CPU menu active', active], [10, '']], 'OPERAND2': [1, [10, '1']]})
    branch = b.add('control_if', {'CONDITION': [2, cond], 'SUBSTACK': [2, body]})
    b.blocks[cond]['parent'] = branch
    b.blocks[body]['parent'] = branch
    b.hat('event_whenkeypressed', {'KEY_OPTION': ['c', None]}, branch)
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="28" viewBox="0 0 420 28"><rect width="420" height="28" rx="7" fill="#172238"/><text x="210" y="19" text-anchor="middle" font-family="sans-serif" font-size="16" fill="white">Xbox: X plays CPU' + (b' (Easy)' if difficulty else b'') + b' | D-pad moves, A jumps</text></svg>'
    md = hashlib.md5(svg).hexdigest()
    asset = md + '.svg'
    assert asset not in files
    files[asset] = svg
    helper = dict(isStage=False, name='Xbox CPU menu shortcut', variables={active: ['Xbox CPU menu active', 1]}, lists={}, broadcasts={}, blocks=b.blocks, comments={}, currentCostume=0, costumes=[dict(name='Xbox controls', bitmapResolution=1, dataFormat='svg', assetId=md, md5ext=asset, rotationCenterX=210, rotationCenterY=14)], sounds=[], volume=100, layerOrder=1000, visible=True, x=0, y=-160, size=100, direction=90, draggable=False, rotationStyle="don't rotate")
    originals = copy.deepcopy(p['targets'])
    p['targets'].append(helper)
    assert p['targets'][:-1] == originals
    out = output
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        info = zipfile.ZipInfo('project.json', (2000, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, json.dumps(p, separators=(',', ':')))
        for (n, data) in sorted(files.items()):
            info = zipfile.ZipInfo(n, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        with zipfile.ZipFile(source) as orig:
            for n in orig.namelist():
                if n != 'project.json':
                    assert z.read(n) == orig.read(n)
    profile = {'controls': {'left arrow': ['dpadLeft', 'LeftStickLeft'], 'right arrow': ['dpadRight', 'LeftStickRight'], 'up arrow': ['dpadUp', 'LeftStickUp', 'A'], 'down arrow': ['dpadDown', 'LeftStickDown'], 'c': 'X'}}
    data = (json.dumps(profile, indent=2) + '\n').encode()
    pathlib.Path(str(out) + '.json').write_bytes(data)
    receipt = dict(source=str(source), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(), profile_sha256=hashlib.sha256(data).hexdigest(), scope='Prepared-project CPU menu shortcut plus controller profile; original targets/gameplay and every original asset identical', original_target_count=len(originals), additional_targets=1, additional_assets=1, hardware_tested=False, emulator_tested=False)
    pathlib.Path(str(out) + '.preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('game', choices=sorted(SPECS))
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('output', type=pathlib.Path)
    args = parser.parse_args()
    receipt = prepare(args.game, args.source, args.output)
    print(json.dumps(receipt, indent=2))
if __name__ == '__main__':
    main()
