#!/usr/bin/env python3
"""Validate Appel preparation against a caller-supplied original archive."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_appel', root / 'scripts/prepare-appel.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = Path(sys.argv[1])
with zipfile.ZipFile(source) as archive:
    original = json.loads(archive.read('project.json'))
prepared = module.prepare(copy.deepcopy(original))
assert len(prepared['targets']) == len(original['targets'])
old_stage = next(t for t in original['targets'] if t['isStage'])
new_stage = copy.deepcopy(next(t for t in prepared['targets'] if t['isStage']))
for key in ['xbox-menu-focus', 'xbox-menu-controller-mode', 'xbox-victory-focus']:
    new_stage['variables'].pop(key)
assert new_stage == old_stage, 'Stage gameplay, lists or non-controller variables changed'
for old, new in zip(original['targets'], prepared['targets']):
    assert old['costumes'] == new['costumes'] and old['sounds'] == new['sounds']
    if old['name'] not in ['menu', 'in-game menu'] and not old['isStage']:
        assert old == new, old['name'] + ' gameplay changed'
menu = next(t for t in prepared['targets'] if t['name'] == 'menu')
blocks = menu['blocks']
hats = [b for k, b in blocks.items() if k.startswith('xbox-menu-') and b['opcode'] == 'event_whenkeypressed']
assert sorted(b['fields']['KEY_OPTION'][0] for b in hats) == ['b', 'down arrow', 'l', 'left arrow', 'right arrow', 'space', 'up arrow']
space = next(b for b in hats if b['fields']['KEY_OPTION'][0] == 'space')
guard = blocks[space['next']]
assert guard['opcode'] == 'control_if'
mode = blocks[guard['inputs']['SUBSTACK'][1]]
assert mode['opcode'] == 'data_setvariableto'
wait = blocks[mode['next']]
assert wait['opcode'] == 'control_wait_until', 'Must release A before transitioning'

def evaluate(value, state, identity, focus, mode=1, mouse=False):
    if isinstance(value, list):
        if value[0] == 3 and isinstance(value[1], list) and value[1][0] == 12:
            return {'GAME STATE': state, 'id': identity, 'Xbox menu selection': focus, 'Xbox controller menus': mode}[value[1][1]]
        if isinstance(value[1], list): return value[1][1]
        return evaluate(value[1], state, identity, focus, mode, mouse)
    b = blocks[value]
    if b['opcode'] == 'sensing_touchingobject': return mouse
    args = [evaluate(v, state, identity, focus, mode, mouse) for v in b['inputs'].values()]
    return {'operator_equals': lambda: str(args[0]) == str(args[1]),
            'operator_contains': lambda: str(args[1]) in str(args[0]),
            'operator_and': lambda: all(args), 'operator_or': lambda: any(args), 'operator_not': lambda: not args[0]}[b['opcode']]()
allowed = guard['inputs']['CONDITION']
for state, identity, focus, expected in [
    ('MENU', 'PLAY', 1, True), ('MENU', 'EDITOR', 1, False),
    ('MENU', 'EDITOR', 2, True), ('MENU', 'AUDIO ON', 3, True),
    ('MENU LEVELS', 'SELECT', 1, True), ('MENU LEVELS', 'PLAY', 1, False),
    ('PLAY', 'PLAY', 1, False), ('PLAY', 'SELECT', 1, False),
    ('MENU OFF', 'SELECT', 1, False), ('MENU', '', 1, False),
]:
    assert evaluate(allowed, state, identity, focus) == expected, (state, identity, focus)
hover = blocks['Y9iOLfz]Q%ofF`ur6i7n']['inputs']['CONDITION']
assert not evaluate(hover, 'MENU', 'PLAY', 2, mode=1, mouse=True), 'Old pointer hover must not create a second focus'
assert evaluate(hover, 'MENU', 'EDITOR', 2, mode=1, mouse=False)
assert evaluate(hover, 'MENU', 'EDITOR', 1, mode=0, mouse=True), 'Pointer mode must preserve authored hover'
assert evaluate(hover, 'PLAY', 'EDITOR', 1, mode=1, mouse=True), 'Other authored menus retain pointer hover'
try: module.prepare(prepared)
except ValueError: pass
else: raise AssertionError('Preparation must refuse repeated application')
print('PASS: assets/gameplay preserved; menu keys, focus guards, release gate, duplicate refusal')

# Victory navigation must preserve every authored action and every other target.
victory = next(t for t in prepared['targets'] if t['name'] == 'in-game menu')
old_victory = next(t for t in original['targets'] if t['name'] == 'in-game menu')
vb = victory['blocks']
changed_conditions = {'X|iW.r0pMOpcby0vVm+8', '2p^0iQn$a`QmovdGC*!Z', 'cupJLhn*zW+h:$r2KN/Z'}
setup_id = 'f{DfM8=tflY4XF=AGwAw'
for key, before in old_victory['blocks'].items():
    after = copy.deepcopy(vb[key]); before = copy.deepcopy(before)
    before.pop('parent', None); after.pop('parent', None)
    if key in changed_conditions:
        before['inputs'].pop('CONDITION'); after['inputs'].pop('CONDITION')
    if key == setup_id:
        before.pop('next'); after.pop('next')
    assert before == after, 'Authored victory action changed: ' + key
assert {k: v for k, v in old_victory.items() if k != 'blocks'} == {
    k: v for k, v in victory.items() if k != 'blocks'}

vh = {b['fields']['KEY_OPTION'][0]: b for k, b in vb.items()
      if k.startswith('xbox-victory-') and b['opcode'] == 'event_whenkeypressed'}
assert sorted(vh) == ['down arrow', 'left arrow', 'right arrow', 'space', 'up arrow']

def ve(value, state='WIN', identity='', focus=1, mode=1, active=1,
       space=False, white=False, mouse=False, x=0, y=0, mx=0, my=0):
    values = {'GAME STATE': state, 'id': identity, 'Xbox victory selection': focus,
              'Xbox controller menus': mode, 'IN-GAME MENU': active}
    def run(value):
        if isinstance(value, list):
            if value[0] == 3 and isinstance(value[1], list) and value[1][0] == 12:
                return values[value[1][1]]
            if isinstance(value[1], list): return value[1][1]
            return run(value[1])
        b = vb[value]; op = b['opcode']
        if op == 'sensing_keyoptions': return b['fields']['KEY_OPTION'][0]
        if op == 'sensing_keypressed':
            key = run(b['inputs']['KEY_OPTION'])
            return {'space': space, 'l': white}[key]
        if op == 'sensing_mousedown': return mouse
        if op in ['motion_xposition', 'motion_yposition', 'sensing_mousex', 'sensing_mousey']:
            return {'motion_xposition': x, 'motion_yposition': y,
                    'sensing_mousex': mx, 'sensing_mousey': my}[op]
        args = [run(v) for v in b['inputs'].values()]
        if op == 'operator_mathop':
            assert b['fields']['OPERATOR'][0] == 'abs'
            return abs(float(args[0]))
        return {'operator_equals': lambda: str(args[0]) == str(args[1]),
                'operator_gt': lambda: float(args[0]) > float(args[1]),
                'operator_lt': lambda: float(args[0]) < float(args[1]),
                'operator_and': lambda: all(args), 'operator_or': lambda: any(args),
                'operator_not': lambda: not args[0],
                'operator_add': lambda: float(args[0]) + float(args[1]),
                'operator_subtract': lambda: float(args[0]) - float(args[1]),
                'operator_mod': lambda: float(args[0]) % float(args[1])}[op]()
    return run(value)

space_guard = vb[vh['space']['next']]
space_allowed = space_guard['inputs']['CONDITION']
choices = ['Continue3', 'Try Again', 'Level Select', 'Replay']
for focus in range(1, 5):
    assert [name for name in ['', 'pause back', *choices]
            if ve(space_allowed, identity=name, focus=focus)] == [choices[focus - 1]]
for state in ['PLAY', 'MENU', 'MENU LEVELS', 'MENU OFF']:
    assert not ve(space_allowed, state=state, identity='Try Again', focus=2)
assert not ve(space_allowed, identity='Try Again', focus=2, active=0)
assert not ve(space_allowed, identity='Try Again', focus=2, white=True), 'White reserves pointer mode'
# A restores controller mode, waits for release, then checks the same choice again.
mode = vb[space_guard['inputs']['SUBSTACK'][1]]
assert mode['fields']['VARIABLE'][0] == 'Xbox controller menus'
wait = vb[mode['next']]
assert wait['opcode'] == 'control_wait_until'
assert not ve(wait['inputs']['CONDITION'], space=True)
assert ve(wait['inputs']['CONDITION'], space=False)
recheck = vb[wait['next']]
assert recheck['opcode'] == 'control_if'
assert ve(recheck['inputs']['CONDITION'], identity='Try Again', focus=2)
assert not ve(recheck['inputs']['CONDITION'], identity='Try Again', focus=3)
assert not ve(recheck['inputs']['CONDITION'], state='PLAY', identity='Try Again', focus=2)
call = vb[recheck['inputs']['SUBSTACK'][1]]
original_call = next(b for b in old_victory['blocks'].values() if b['opcode'] == 'procedures_call'
                     and b.get('mutation', {}).get('proccode') == 'show menu')
assert call['mutation'] == original_call['mutation']
assert call['inputs'] == original_call['inputs'] and call['fields'] == original_call['fields']

for key, delta in [('up arrow', -1), ('down arrow', 1)]:
    guard = vb[vh[key]['next']]
    for name in choices:
        assert not ve(guard['inputs']['CONDITION'], identity=name), 'Clone multiplied a move'
    assert ve(guard['inputs']['CONDITION'], identity='')
    assert not ve(guard['inputs']['CONDITION'], state='PLAY')
    assert not ve(guard['inputs']['CONDITION'], white=True), 'Pointer movement must not move victory focus'
    mode = vb[guard['inputs']['SUBSTACK'][1]]
    assignment = vb[mode['next']]
    for focus in range(1, 5):
        assert ve(assignment['inputs']['VALUE'], focus=focus) == (focus - 1 + delta) % 4 + 1
for key, current, target in [('left arrow', 4, 3), ('right arrow', 3, 4)]:
    guard = vb[vh[key]['next']]; mode = vb[guard['inputs']['SUBSTACK'][1]]
    assert not ve(guard['inputs']['CONDITION'], white=True), 'White must also reserve horizontal pointer movement'
    change = vb[mode['next']]; assignment = vb[change['inputs']['SUBSTACK'][1]]
    for focus in range(1, 5):
        assert ve(change['inputs']['CONDITION'], focus=focus) == (focus == current)
    assert ve(assignment['inputs']['VALUE']) == str(target)

vertical = vb['X|iW.r0pMOpcby0vVm+8']['inputs']['CONDITION']
horizontal = vb['2p^0iQn$a`QmovdGC*!Z']['inputs']['CONDITION']
mouse_press = vb['cupJLhn*zW+h:$r2KN/Z']['inputs']['CONDITION']
positions = {'Continue3': (-90, 0), 'Try Again': (-90, -48),
             'Level Select': (-90, -118), 'Replay': (90, -118)}
# A stale pointer over Replay cannot create a second hover or click in D-pad mode.
for name, (x, y) in positions.items():
    args = dict(identity=name, focus=2, x=x, y=y, mx=90, my=-118, mouse=True)
    assert (ve(vertical, **args) and ve(horizontal, **args)) == (name == 'Try Again')
    assert not ve(mouse_press, **args)
    assert (ve(vertical, mode=0, **args) and ve(horizontal, mode=0, **args)) == (name == 'Replay')
    assert ve(mouse_press, mode=0, **args)
    assert (ve(vertical, white=True, **args) and ve(horizontal, white=True, **args)) == (name == 'Replay')
    assert ve(mouse_press, white=True, **args), 'White must allow authored pointer click even before mode changes'
    assert (ve(vertical, state='PLAY', **args) and ve(horizontal, state='PLAY', **args)) == (name == 'Replay')

mode = vb[vb[setup_id]['next']]; assignment = vb[mode['next']]
assert mode['fields']['VARIABLE'][0] == 'Xbox controller menus' and ve(mode['inputs']['VALUE']) == '1'
assert assignment['fields']['VARIABLE'][0] == 'Xbox victory selection' and ve(assignment['inputs']['VALUE']) == '1'
assert assignment['next'] == old_victory['blocks'][setup_id]['next']
print('PASS: victory focus/release/recheck, single-clone activation, pointer isolation, authored actions preserved')
