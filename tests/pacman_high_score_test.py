"""Exercise SB2 ending handlers against the final-pellet scheduling regression."""
import copy
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_pacman", root / "scripts/prepare-pacman.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


def original():
    return {"objName": "Stage", "variables": [{"name": "Score"}, {"name": "High Score"}],
            "scripts": [[92, 58, [["whenIReceive", "GAME OVER"], ["startScene", "backdrop1"], ["stopScripts", "all"]]],
                        [89, 177, [["whenIReceive", "GAME WIN"], ["startScene", "backdrop2"], ["stopScripts", "all"]]],
                        [7, 8, [["whenGreenFlag"], ["setVar:to:", "Dots", 0]]]],
            "children": [{"objName": "Pacman", "costumes": ["original"], "scripts": []}],
            "info": {"projectID": "preserved"}}


class StopAll(Exception):
    pass


def value(expr, state):
    if not isinstance(expr, list):
        return expr
    if expr[0] == "readVariable":
        return state[expr[1]]
    if expr[0] == ">":
        return float(value(expr[1], state)) > float(value(expr[2], state))
    raise AssertionError(expr)


def execute(blocks, state):
    for op, *args in blocks:
        if op == "doIf":
            if value(args[0], state):
                execute(args[1], state)
        elif op == "setVar:to:":
            state[args[0]] = value(args[1], state)
        elif op == "startScene":
            state["backdrop"] = args[0]
        elif op == "stopScripts":
            assert args == ["all"]
            raise StopAll
        else:
            raise AssertionError(op)


def ending(project, message, score, record):
    script = next(s[2] for s in project["scripts"] if s[2][0] == ["whenIReceive", message])
    state = {"Score": score, "High Score": record, "Dots": 92, "untouched": 123}
    try:
        execute(script[1:], state)
    except StopAll:
        return state
    raise AssertionError("Ending must still stop every thread")


before = original()
after = copy.deepcopy(before)
prepare.repair_end_score(after)
# Last pellet changed 1370 -> 1380 since the periodic high-score thread ran.
assert ending(before, "GAME WIN", 1380, 1370)["High Score"] == 1370
assert ending(after, "GAME WIN", 1380, 1370)["High Score"] == 1380
cases = 0
for message, backdrop in [("GAME WIN", "backdrop2"), ("GAME OVER", "backdrop1")]:
    for score, record, expected in [(1380, 1370, 1380), (100, 20, 100), (0, 1380, 1380),
                                    (10, 1380, 1380), (1380, 1380, 1380), (0, 0, 0)]:
        state = ending(after, message, score, record)
        assert state == {"Score": score, "High Score": expected, "Dots": 92,
                         "untouched": 123, "backdrop": backdrop}, state
        cases += 1
# The periodic script and other gameplay/metadata remain byte-structurally equal.
reconstructed = copy.deepcopy(after)
for script in reconstructed["scripts"][:2]:
    del script[2][1]
assert reconstructed == before
# Refuse unfamiliar/duplicate/previously prepared handlers without partial edits.
for kind in ("missing-loss", "duplicate-win", "modified-win", "missing-global", "prepared"):
    bad = original()
    if kind == "missing-loss": bad["scripts"].pop(0)
    if kind == "duplicate-win": bad["scripts"].append(copy.deepcopy(bad["scripts"][1]))
    if kind == "modified-win": bad["scripts"][1][2][-1] = ["stopScripts", "this script"]
    if kind == "missing-global": bad["variables"].pop()
    if kind == "prepared": bad = copy.deepcopy(after)
    saved = copy.deepcopy(bad)
    try:
        prepare.repair_end_score(bad)
    except ValueError:
        assert bad == saved
    else:
        raise AssertionError("Accepted unfamiliar project: " + kind)
print(f"PASS: original final-pellet gap reproduced; {cases} Win/loss record checks; gameplay preservation and atomic input rejection")
