#!/usr/bin/env python3
"""Run the prepared SB2 loops: special catches, missed fruit and replay resets."""
import copy
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_catch", root / "scripts/prepare-catch-apples.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


def original_sprite(name, speed, points, sound):
    # Original SB2 shapes, including the two independent collision checks.
    return {"objName": name, "costumes": [{"baseLayerMD5": "unchanged"}], "scripts": [
        [27, 262, [["whenGreenFlag"], ["setVar:to:", "Score", 0], ["doForever", [
            ["doIf", ["touching:", "Bowl"], [["playSound:", sound],
                ["changeVar:by:", "Score", points], ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180]]]]]]],
        [334, 52, [["whenGreenFlag"], ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180],
            ["doForever", [["changeYposBy:", speed], ["doIf", ["|", ["<", ["ypos"], "-180"],
                ["touching:", "Bowl"]], [["hide"], ["wait:elapsed:from:", 5], ["show"],
                    ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180]]]]]]],
    ]}


def value(expression, state):
    if not isinstance(expression, list):
        return expression
    op, *args = expression
    if op == "ypos": return state["y"]
    if op == "touching:": return state["visible"] and state["aligned"] and state["y"] <= -80
    if op == "<": return float(value(args[0], state)) < float(value(args[1], state))
    if op == "|": return bool(value(args[0], state) or value(args[1], state))
    raise AssertionError(expression)


def execute(blocks, state):
    for op, *args in blocks:
        if op == "changeYposBy:": state["y"] += args[0]
        elif op == "changeVar:by:": state["score"] += args[1]
        elif op == "setVar:to:": state["score"] = args[1]
        elif op == "playSound:": state["sounds"].append(args[0])
        elif op == "gotoSpriteOrMouse:": state["repositions"] += 1
        elif op == "ypos:": state["y"] = args[0]
        elif op == "hide": state["visible"] = False
        elif op == "show": state["visible"] = True
        elif op == "wait:elapsed:from:": yield args[0]
        elif op in ("doIf", "doIfElse"):
            if value(args[0], state): yield from execute(args[1], state)
            elif op == "doIfElse": yield from execute(args[2], state)
        else: raise AssertionError(op)


def state(y=-75, aligned=True, visible=True):
    return dict(y=y, aligned=aligned, visible=visible, score=5, sounds=[], repositions=0)


for name, speed, points, sound in [("Sprite1", -8, 2, "A-Tone-His_Self-1266414414.mp3"),
                                    ("Sprite3", -4, -2, "pop")]:
    original = original_sprite(name, speed, points, sound)
    other_name = "Sprite3" if name == "Sprite1" else "Sprite1"
    other = original_sprite(other_name, -4 if other_name == "Sprite3" else -8,
                            -2 if other_name == "Sprite3" else 2,
                            "pop" if other_name == "Sprite3" else "A-Tone-His_Self-1266414414.mp3")
    project = {"children": [original, other, {"objName": "Apple", "scripts": []}], "credits": "preserved"}
    before = copy.deepcopy(project)
    prepare.repair_special_apples(project)
    # Reproduce the original loss: movement enters contact and hides before
    # the separate scoring thread sees it. Both legal thread orders fail.
    old_loops = [s[2][-1][1] for s in before["children"][0]["scripts"]]
    start_y = -80 - speed / 2
    for order in [(0, 1), (1, 0)]:
        old = state(y=start_y)
        for index in order:
            next(execute(old_loops[index], old), None)
        assert old["score"] == 5 and not old["visible"]
    sprite = project["children"][0]
    assert sprite["costumes"] == before["children"][0]["costumes"]
    assert project["children"][2] == before["children"][2] and project["credits"] == "preserved"
    assert sprite["scripts"][0][2] == [["whenGreenFlag"], ["setVar:to:", "Score", 0]]
    loop = sprite["scripts"][1][2][-1][1]
    caught = state(y=start_y)
    assert list(execute(loop, caught)) == []
    assert caught == dict(y=180, aligned=True, visible=True, score=5+points, sounds=[sound], repositions=1)
    # Another frame cannot double-award a catch after it was repositioned.
    list(execute(loop, caught))
    assert caught["score"] == 5+points and caught["repositions"] == 1
    # A miss keeps its original five-second hidden interval, with no points.
    missed = state(y=-179, aligned=False)
    run = execute(loop, missed)
    assert next(run) == 5 and not missed["visible"] and missed["score"] == 5
    assert next(run, None) is None
    assert missed["visible"] and missed["y"] == 180 and missed["repositions"] == 1
    hidden = state(y=start_y, visible=False)
    assert list(execute(loop, hidden)) == [] and hidden["score"] == 5
    replay = state()
    list(execute(sprite["scripts"][0][2][1:], replay))
    assert replay["score"] == 0
    try:
        prepare.repair_special_apples(project)
        raise AssertionError("Must refuse a second preparation")
    except ValueError:
        pass
print("PASS: original scoring race reproduced in both orders; +2/-2 once, miss cooldown, hidden fruit, replay and unchanged metadata")
