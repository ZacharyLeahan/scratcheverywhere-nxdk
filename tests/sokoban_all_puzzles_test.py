#!/usr/bin/env python3
"""Check prepared archives, complete routes and the actual goal-count script.

Supply the original Gammastr20 archive; no game assets are redistributed here.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).resolve()
original_sha = "6b2ea446a14651efe37bc6589172a05309371d1c8db1d9ce8a267848827e5013"
default_sha = "efdbc0055c6c97f1c525e4e5dd5273066e88f043127fb1c81d5276196df97f64"
full_sha = "8253ed9a8dc8106525d1121880549bfa24de969223f0a360e4cc331ec880d05b"
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source) == original_sha, "Supply the tested original archive."


def cli(script, *args, success=True):
    result = subprocess.run([sys.executable, str(root / 'scripts' / script), *map(str, args)],
                            text=True, capture_output=True)
    assert (result.returncode == 0) == success, result.stdout + result.stderr
    return result


def project(path):
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read('project.json'))


def levels(data):
    return next(row['contents'] for row in data['lists'] if row['listName'] == 'Data')


def scan(data):
    tick = next(script[2] for child in data['children'] if child.get('objName') == 'Tiles'
                for script in child['scripts'] if script[2][0][:2] == ['procDef', 'Tick'])
    indices = [i for i, block in enumerate(tick[:-2])
               if block[:2] == ['setVar:to:', 't_i'] and
               tick[i + 1] == ['setVar:to:', 't_cCube', 0] and
               tick[i + 2][:2] == ['doRepeat', ['lineCountOfList:', 'Level']]]
    assert len(indices) == 1
    i = indices[0]
    return tick, i


def execute_count(blocks, board):
    """Interpret the finite source loop, independently of the preparation code."""
    variables = {}

    def expr(value):
        if not isinstance(value, list):
            return value
        op = value[0]
        if op == 'readVariable':
            return variables[value[1]]
        if op == 'lineCountOfList:':
            assert value[1] == 'Level'
            return len(board)
        if op == 'getLine:ofList:':
            assert value[2] == 'Level'
            index = int(expr(value[1])) - 1
            return board[index] if 0 <= index < len(board) else ''
        if op == '=':
            return str(expr(value[1])) == str(expr(value[2]))
        raise AssertionError(value)

    def execute(sequence):
        for block in sequence:
            op = block[0]
            if op == 'setVar:to:':
                variables[block[1]] = expr(block[2])
            elif op == 'changeVar:by:':
                variables[block[1]] = int(float(variables[block[1]]) + float(expr(block[2])))
            elif op == 'doRepeat':
                for _ in range(int(expr(block[1]))):
                    execute(block[2])
            elif op == 'doIf':
                if expr(block[1]):
                    execute(block[2])
            else:
                raise AssertionError(block)

    execute(blocks)
    return variables['t_cCube']


with tempfile.TemporaryDirectory(prefix='sokoban-puzzles-') as directory:
    tmp = Path(directory)
    default, full, repeat = [tmp / name for name in ('default.sb2', 'full.sb2', 'repeat.sb2')]
    cli('prepare-sokoban.py', source, default)
    cli('prepare-sokoban.py', '--all-puzzles', source, full)
    cli('prepare-sokoban.py', '--all-puzzles', source, repeat)
    assert sha(default) == default_sha and sha(full) == sha(repeat) == full_sha
    original, prepared = project(source), project(full)
    before, after = levels(original), levels(prepared)
    assert [i + 1 for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]] == [10, 12, 13]
    for i, raw in enumerate(after):
        height, width, x, y = [int(raw[k:k + 2]) for k in range(0, 8, 2)]
        assert len(raw[8:]) == width * height
        assert raw[8:][y * width + x] in '13'
        assert sum(c in '24' for c in raw[8:]) == sum(c in '34' for c in raw[8:]) > 0
        assert sum(c in '24' for c in raw[8:]) == sum(c in '24' for c in before[i][8:])
        assert sum(c in '34' for c in raw[8:]) == sum(c in '34' for c in before[i][8:])
    assert after[11][8:] == before[11][8:] and after[12][8:] == before[12][8:]
    old_tick, oi = scan(original)
    new_tick, ni = scan(prepared)
    assert old_tick[oi][2] == '1' and new_tick[ni][2] == '0'
    for level, raw in enumerate(after, 1):
        won = ['4' if c in '34' else '1' if c == '2' else c for c in raw[8:]]
        expected = won.count('4')
        old_count = execute_count(old_tick[oi:oi + 3], won)
        new_count = execute_count(new_tick[ni:ni + 3], won)
        assert new_count == expected
        assert (old_count != expected) == (level in (9, 12))
    # Reverse precisely the documented edits; all other project content must match.
    new_tick[ni][2] = '1'
    for i in (9, 11, 12):
        after[i] = before[i]
    assert prepared == original
    with zipfile.ZipFile(source) as a, zipfile.ZipFile(full) as b:
        assert a.namelist() == b.namelist()
        for name in a.namelist():
            if name != 'project.json':
                assert a.read(name) == b.read(name)
    single = root / 'examples/sokoban-level10-solution.json'
    assert json.loads(cli('verify-sokoban-solution.py', default, single).stdout)['moves'] == 698
    bundle_path = root / 'examples/sokoban-all-puzzles-solutions.json'
    bundle = json.loads(bundle_path.read_text())
    report = json.loads(cli('verify-sokoban-solution.py', full, bundle_path).stdout)
    assert report['verified_all_puzzles'] and len(report['levels']) == 13
    assert report['moves'] == 2728 and report['pushes'] == 628
    assert 'Puzzle 10' in cli('verify-sokoban-solution.py', source, bundle_path, success=False).stderr
    variants = []
    missing = copy.deepcopy(bundle); missing['levels'].pop(); variants.append(missing)
    duplicate = copy.deepcopy(bundle); duplicate['levels'][-1]['level'] = 1; variants.append(duplicate)
    trailing = copy.deepcopy(bundle); trailing['levels'][0]['directions'] += 'L'; variants.append(trailing)
    wrong_pushes = copy.deepcopy(bundle); wrong_pushes['levels'][0]['pushes'] += 1; variants.append(wrong_pushes)
    wrong_route = copy.deepcopy(bundle); wrong_route['levels'][0]['directions'] = 'X'; variants.append(wrong_route)
    wrong_revision = copy.deepcopy(bundle); wrong_revision['prepared_sha256'] = '0' * 64; variants.append(wrong_revision)
    for i, bad in enumerate(variants):
        path = tmp / f'bad-{i}.json'; path.write_text(json.dumps(bad))
        cli('verify-sokoban-solution.py', full, path, success=False)
    # Guard checks use disposable copies, preserving the supplied original even on failure.
    same = tmp / 'same.sb2'; shutil.copy2(source, same)
    cli('prepare-sokoban.py', '--all-puzzles', same, same, success=False)
    assert sha(same) == original_sha
    cli('prepare-sokoban.py', '--all-puzzles', source, full, success=False)
    assert sha(full) == full_sha
    wrong = tmp / 'wrong.sb2'; wrong.write_bytes(b'wrong source')
    rejected = tmp / 'rejected.sb2'
    cli('prepare-sokoban.py', '--all-puzzles', wrong, rejected, success=False)
    assert not rejected.exists() and sha(source) == original_sha
print('PASS: default compatibility; deterministic full archive; precise edits/assets; all13 routes; first-goal scan; rejection guards')
