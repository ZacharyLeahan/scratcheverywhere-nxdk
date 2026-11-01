#!/usr/bin/env python3
"""Add controller menu navigation to a separate Appel v1.4 copy.

Preserves assets and gameplay scripts. A/Space activates the focused title
item, selected level or victory action on release; arrows navigate and B returns
from levels. Victory actions use the original in-game menu procedure.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile


def prepare(project):
    stage = next(t for t in project['targets'] if t['isStage'])
    menu = next(t for t in project['targets'] if t['name'] == 'menu')
    blocks = menu['blocks']
    if any(k.startswith('xbox-menu-') for k in blocks):
        raise ValueError('Already prepared')
    variables = {v[0]: k for k, v in stage['variables'].items()}
    local = {v[0]: k for k, v in menu['variables'].items()}
    if not {'GAME STATE', 'LEVEL #'}.issubset(variables) or 'id' not in local:
        raise ValueError('Expected Appel menu variables')
    focus = 'xbox-menu-focus'
    stage['variables'][focus] = ['Xbox menu selection', 1]
    mode = 'xbox-menu-controller-mode'
    stage['variables'][mode] = ['Xbox controller menus', 1]
    variables['Xbox controller menus'] = mode
    number = 0

    def add(op, inputs=None, fields=None, next=None, **extra):
        nonlocal number
        number += 1
        key = 'xbox-menu-' + str(number)
        blocks[key] = dict(opcode=op, next=next, parent=None, inputs=inputs or {},
                           fields=fields or {}, shadow=False, topLevel=False, **extra)
        return key

    def literal(v): return [1, [10, str(v)]]
    def ref(v): return [2, v]
    def var(name):
        key = focus if name == 'Xbox menu selection' else local.get(name, variables.get(name))
        return [3, [12, name, key], [10, '']]
    def eq(a, b): return add('operator_equals', {'OPERAND1': a, 'OPERAND2': b})
    def both(a, b): return add('operator_and', {'OPERAND1': ref(a), 'OPERAND2': ref(b)})
    def either(a, b): return add('operator_or', {'OPERAND1': ref(a), 'OPERAND2': ref(b)})
    def state(v): return eq(var('GAME STATE'), literal(v))
    def identity(v): return eq(var('id'), literal(v))
    def selected(n): return eq(var('Xbox menu selection'), literal(n))
    def setfocus(n, next=None):
        return add('data_setvariableto', {'VALUE': literal(n)}, {'VARIABLE': ['Xbox menu selection', focus]}, next)
    def setmode(n, next=None):
        return add('data_setvariableto', {'VALUE': literal(n)}, {'VARIABLE': ['Xbox controller menus', mode]}, next)
    def hat(key, body):
        h = add('event_whenkeypressed', fields={'KEY_OPTION': [key, None]}, next=body)
        blocks[h].update(topLevel=True, x=3000, y=3000 + number)
    def condition(test, body, next=None):
        return add('control_if', {'CONDITION': ref(test), 'SUBSTACK': ref(body)}, next=next)

    title_focus = either(both(identity('PLAY'), selected(1)),
                         either(both(identity('EDITOR'), selected(2)),
                                both(add('operator_contains', {'STRING1': var('id'), 'STRING2': literal('AUDIO')}), selected(3))))
    allowed = either(both(state('MENU'), title_focus), both(state('MENU LEVELS'), identity('SELECT')))
    original_hat = next(b for b in blocks.values() if b['opcode'] == 'event_whenthisspriteclicked')
    # Copy the authored click stack: reuse its validation, sounds, score load,
    # transitions and level launch instead of bypassing the game's lifecycle.
    copied = {}
    def clone(key):
        if key in copied: return copied[key]
        source = copy.deepcopy(blocks[key])
        target = add(source.pop('opcode'))
        copied[key] = target
        blocks[target].update(source)
        blocks[target]['parent'] = None
        if source.get('next'): blocks[target]['next'] = clone(source['next'])
        for value in blocks[target]['inputs'].values():
            if len(value) > 1 and isinstance(value[1], str) and value[1] in blocks:
                value[1] = clone(value[1])
        return target
    click = clone(original_hat['next'])
    keymenu = add('sensing_keyoptions', fields={'KEY_OPTION': ['space', None]})
    pressed = add('sensing_keypressed', {'KEY_OPTION': [1, keymenu]})
    released = add('operator_not', {'OPERAND': ref(pressed)})
    wait = add('control_wait_until', {'CONDITION': ref(released)}, next=click)
    hat('space', condition(allowed, setmode(1, wait)))
    # Only the hidden original handles focus, so clones cannot multiply moves.
    for key, delta in [('up arrow', -1), ('down arrow', 1)]:
        value = add('operator_add', {'NUM1': var('Xbox menu selection'), 'NUM2': literal(delta + 2)})
        wrap = add('operator_mod', {'NUM1': [3, value, [4, '0']], 'NUM2': literal(3)})
        onebased = add('operator_add', {'NUM1': [3, wrap, [4, '0']], 'NUM2': literal(1)})
        change = add('data_setvariableto', {'VALUE': [3, onebased, [4, '1']]}, {'VARIABLE': ['Xbox menu selection', focus]})
        hat(key, condition(both(state('MENU'), identity('')), setmode(1, change)))
    for key in ['left arrow', 'right arrow']:
        hat(key, condition(both(state('MENU LEVELS'), identity('')), setmode(1)))
    hat('l', condition(identity(''), setmode(0)))
    hat('b', condition(both(state('MENU LEVELS'), identity('BACK')), clone(original_hat['next'])))
    hover = next(b for b in blocks.values() if b['opcode'] == 'control_if_else' and
                 b.get('inputs', {}).get('CONDITION') == [2, '[Gs5_%4cfxuid9m#mwp('])
    keyboard = both(eq(var('Xbox controller menus'), literal(1)), either(state('MENU'), state('MENU LEVELS')))
    pointer = add('operator_not', {'OPERAND': ref(clone(keyboard))})
    hover['inputs']['CONDITION'] = ref(either(both(keyboard, clone(allowed)), both(pointer, '[Gs5_%4cfxuid9m#mwp(')))
    # Reset focus whenever the authored title setup runs.
    setup = next(b for b in blocks.values() if b['opcode'] == 'procedures_definition' and
                 blocks[b['inputs']['custom_block'][1]].get('mutation', {}).get('proccode') == 'Setup Main Menu %s')
    setup['next'] = setmode(1, setfocus(1, setup['next']))
    # Parent links are structural editor metadata but keep the new graphs valid.
    for key, block in list(blocks.items()):
        if not key.startswith('xbox-menu-'): continue
        if block.get('next'): blocks[block['next']]['parent'] = key
        for value in block.get('inputs', {}).values():
            if len(value) > 1 and isinstance(value[1], str) and value[1].startswith('xbox-menu-'):
                blocks[value[1]]['parent'] = key
    _prepare_victory_menu(project, stage)
    return project


def _prepare_victory_menu(project, stage):
    """Route victory focus through the authored show-menu action procedure."""
    menu = next(t for t in project['targets'] if t['name'] == 'in-game menu')
    blocks = menu['blocks']
    focus = 'xbox-victory-focus'
    stage['variables'][focus] = ['Xbox victory selection', 1]
    variables = {v[0]: k for k, v in stage['variables'].items()}
    local = {v[0]: k for k, v in menu['variables'].items()}
    number = 0

    def add(op, inputs=None, fields=None, next=None, **extra):
        nonlocal number
        number += 1
        key = 'xbox-victory-' + str(number)
        blocks[key] = dict(opcode=op, next=next, parent=None, inputs=inputs or {},
                           fields=fields or {}, shadow=False, topLevel=False, **extra)
        return key

    def literal(v): return [1, [10, str(v)]]
    def ref(v): return [2, v]
    def var(name): return [3, [12, name, local.get(name, variables.get(name))], [10, '']]
    def eq(a, b): return add('operator_equals', {'OPERAND1': a, 'OPERAND2': b})
    def both(a, b): return add('operator_and', {'OPERAND1': ref(a), 'OPERAND2': ref(b)})
    def either(a, b): return add('operator_or', {'OPERAND1': ref(a), 'OPERAND2': ref(b)})
    def identity(v): return eq(var('id'), literal(v))
    def selected(n): return eq(var('Xbox victory selection'), literal(n))
    def winning():
        active = add('operator_gt', {'OPERAND1': var('IN-GAME MENU'), 'OPERAND2': literal(0)})
        return both(eq(var('GAME STATE'), literal('WIN')), active)
    def controller_ready():
        white = add('sensing_keyoptions', fields={'KEY_OPTION': ['l', None]})
        pressed = add('sensing_keypressed', {'KEY_OPTION': [1, white]})
        return both(winning(), add('operator_not', {'OPERAND': ref(pressed)}))
    def keyboard():
        return both(controller_ready(), eq(var('Xbox controller menus'), literal(1)))
    def pointer(): return add('operator_not', {'OPERAND': ref(keyboard())})
    def allowed():
        choices = [both(identity(name), selected(n)) for n, name in enumerate(
            ['Continue3', 'Try Again', 'Level Select', 'Replay'], 1)]
        match = choices[0]
        for choice in choices[1:]: match = either(match, choice)
        return both(controller_ready(), match)
    def setvar(name, value, next=None):
        return add('data_setvariableto', {'VALUE': value},
                   {'VARIABLE': [name, variables[name]]}, next)
    def setmode(value, next=None):
        return setvar('Xbox controller menus', literal(value), next)
    def condition(test, body, next=None):
        return add('control_if', {'CONDITION': ref(test), 'SUBSTACK': ref(body)}, next=next)
    def hat(key, body):
        h = add('event_whenkeypressed', fields={'KEY_OPTION': [key, None]}, next=body)
        blocks[h].update(topLevel=True, x=8000, y=3000 + number)

    # Clones handle A only when their own authored button is selected. Recheck
    # after release so a menu change or focus move cannot activate an old choice.
    original_call = next(b for b in blocks.values() if b['opcode'] == 'procedures_call'
                         and b.get('mutation', {}).get('proccode') == 'show menu')
    action = add('procedures_call', copy.deepcopy(original_call['inputs']),
                 copy.deepcopy(original_call['fields']),
                 mutation=copy.deepcopy(original_call['mutation']))
    keymenu = add('sensing_keyoptions', fields={'KEY_OPTION': ['space', None]})
    pressed = add('sensing_keypressed', {'KEY_OPTION': [1, keymenu]})
    released = add('operator_not', {'OPERAND': ref(pressed)})
    wait = add('control_wait_until', {'CONDITION': ref(released)},
               next=condition(allowed(), action))
    hat('space', condition(allowed(), setmode(1, wait)))

    # The hidden original alone moves global focus; button clones cannot multiply
    # each key press. Up/down cycle all four choices; left/right cross the last row.
    for key, delta in [('up arrow', -1), ('down arrow', 1)]:
        value = add('operator_add', {'NUM1': var('Xbox victory selection'), 'NUM2': literal(delta + 3)})
        wrap = add('operator_mod', {'NUM1': [3, value, [4, '0']], 'NUM2': literal(4)})
        onebased = add('operator_add', {'NUM1': [3, wrap, [4, '0']], 'NUM2': literal(1)})
        change = setvar('Xbox victory selection', [3, onebased, [4, '1']])
        hat(key, condition(both(controller_ready(), identity('')), setmode(1, change)))
    for key, current, target in [('left arrow', 4, 3), ('right arrow', 3, 4)]:
        change = condition(selected(current), setvar('Xbox victory selection', literal(target)))
        hat(key, condition(both(controller_ready(), identity('')), setmode(1, change)))

    # Keep the authored pointer path for every other menu and mouse mode. In
    # controller mode only the selected victory clone may highlight; a stale
    # pointer cannot highlight or click a second button.
    vertical = blocks['X|iW.r0pMOpcby0vVm+8']
    horizontal = blocks['2p^0iQn$a`QmovdGC*!Z']
    mouse_press = blocks['cupJLhn*zW+h:$r2KN/Z']
    old_vertical = vertical['inputs']['CONDITION'][1]
    old_horizontal = horizontal['inputs']['CONDITION'][1]
    old_press = mouse_press['inputs']['CONDITION'][1]
    vertical['inputs']['CONDITION'] = ref(either(both(keyboard(), allowed()), both(pointer(), old_vertical)))
    horizontal['inputs']['CONDITION'] = ref(either(keyboard(), both(pointer(), old_horizontal)))
    mouse_press['inputs']['CONDITION'] = ref(both(pointer(), old_press))

    setup_key, setup = next((k, b) for k, b in blocks.items() if b['opcode'] == 'procedures_definition'
                           and blocks[b['inputs']['custom_block'][1]].get('mutation', {}).get('proccode')
                           == 'clone level complete menu')
    setup['next'] = setmode(1, setvar('Xbox victory selection', literal(1), setup['next']))
    blocks[setup['next']]['parent'] = setup_key
    for key, block in list(blocks.items()):
        if not key.startswith('xbox-victory-'): continue
        if block.get('next'): blocks[block['next']]['parent'] = key
        for value in block['inputs'].values():
            if len(value) > 1 and isinstance(value[1], str) and value[1] in blocks:
                blocks[value[1]]['parent'] = key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve() or args.output.exists():
        parser.error('Choose a new output; the original is never overwritten.')
    with zipfile.ZipFile(args.source) as original:
        project = prepare(json.loads(original.read('project.json')))
        with zipfile.ZipFile(args.output, 'x') as prepared:
            for info in original.infolist():
                prepared.writestr(info, json.dumps(project, separators=(',', ':')).encode() if info.filename == 'project.json' else original.read(info))
    print(json.dumps({'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
                      'prepared_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
