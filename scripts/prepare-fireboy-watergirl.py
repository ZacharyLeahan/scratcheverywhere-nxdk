#!/usr/bin/env python3
"""Add controller level selection to a separate Fireboy/Watergirl SB3 copy.

Retains authored level locks and the existing click/identify procedure. Supplies
a single-controller dual-stick profile; this does not add two-controller support.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile


class Blocks:
    def __init__(self, prefix):
        self.blocks = {}
        self.prefix = prefix

    def add(self, opcode, inputs=None, fields=None):
        key = self.prefix + str(len(self.blocks) + 1)
        self.blocks[key] = dict(opcode=opcode, next=None, parent=None,
                                inputs=inputs or {}, fields=fields or {},
                                shadow=False, topLevel=False)
        for value in (inputs or {}).values():
            for child in value[1:]:
                if isinstance(child, str) and child in self.blocks:
                    self.blocks[child]["parent"] = key
        return key

    def chain(self, *keys):
        for left, right in zip(keys, keys[1:]):
            self.blocks[left]["next"] = right
            self.blocks[right]["parent"] = left
        return keys[0]

    def hat(self, opcode, fields, body):
        key = self.add(opcode, fields=fields)
        self.blocks[key].update(topLevel=True, x=20, y=20, next=body)
        self.blocks[body]["parent"] = key
        return key


def literal(value):
    return [1, [10, str(value)]]


def variable(name, key):
    return [3, [12, name, key], [10, ""]]


def prepare(source, output):
    paths = [output, Path(str(output) + ".json"), Path(str(output) + ".preparation.json")]
    if source.resolve() == output.resolve() or any(path.exists() for path in paths):
        raise ValueError("Choose new output paths; originals and existing prepared files are preserved.")
    with zipfile.ZipFile(source) as archive:
        project = json.loads(archive.read("project.json"))
        assets = {name: archive.read(name) for name in archive.namelist() if name != "project.json"}
    original = copy.deepcopy(project)
    stage = next(target for target in project["targets"] if target.get("isStage"))
    home = next(target for target in project["targets"] if target["name"] == "home")
    page = next(key for key, value in stage["variables"].items() if value[0] == "page")
    clone_id = next(key for key, value in home["variables"].items() if value[0] == "clone id")
    click = next(block for block in home["blocks"].values()
                 if isinstance(block, dict) and block.get("opcode") == "event_whenthisspriteclicked")
    root = click["next"]
    if home["blocks"][root]["opcode"] != "control_if":
        raise ValueError("Unexpected project revision: expected the authored guarded level click.")
    choice = "xbox_level_choice"
    if choice in stage["variables"] or any(t["name"] == "Xbox level menu" for t in project["targets"]):
        raise ValueError("This project already has the Xbox level menu.")
    stage["variables"][choice] = ["Xbox level choice", 1]

    # Copy the original guarded click chain, preserving its lock checks and
    # identify call. Only the selected menu clone receives the new key shortcut.
    extra = Blocks("xbox_level_home_")
    mapping = {}

    def clone_block(key):
        if key in mapping:
            return mapping[key]
        block = copy.deepcopy(home["blocks"][key])
        new_key = extra.add(block["opcode"])
        mapping[key] = new_key
        extra.blocks[new_key] = block
        block.update(parent=None, topLevel=False)
        if block.get("next"):
            block["next"] = clone_block(block["next"])
            extra.blocks[block["next"]]["parent"] = new_key
        for value in block.get("inputs", {}).values():
            for index in range(1, len(value)):
                if isinstance(value[index], str) and value[index] in home["blocks"]:
                    value[index] = clone_block(value[index])
                    extra.blocks[value[index]]["parent"] = new_key
        return new_key

    body = clone_block(root)
    is_menu = extra.add("operator_equals", {"OPERAND1": variable("page", page), "OPERAND2": literal("menu")})
    selected = extra.add("operator_equals", {"OPERAND1": variable("clone id", clone_id),
                                            "OPERAND2": variable("Xbox level choice", choice)})
    condition = extra.add("operator_and", {"OPERAND1": [2, is_menu], "OPERAND2": [2, selected]})
    guard = extra.add("control_if", {"CONDITION": [2, condition], "SUBSTACK": [2, body]})
    extra.hat("event_whenkeypressed", {"KEY_OPTION": ["up arrow", None]}, guard)
    if set(extra.blocks) & set(home["blocks"]):
        raise ValueError("Unexpected block ID collision.")
    home["blocks"].update(extra.blocks)

    helper = Blocks("xbox_level_menu_")
    reset = helper.add("data_setvariableto", {"VALUE": literal(1)}, {"VARIABLE": ["Xbox level choice", choice]})
    helper.hat("event_whenflagclicked", {}, reset)
    for key, delta, limit, wrap in [("right arrow", 1, 8, 1), ("left arrow", -1, 1, 8)]:
        change = helper.add("data_changevariableby", {"VALUE": literal(delta)}, {"VARIABLE": ["Xbox level choice", choice]})
        outside = helper.add("operator_gt" if delta > 0 else "operator_lt",
                             {"OPERAND1": variable("Xbox level choice", choice), "OPERAND2": literal(limit)})
        reset_wrap = helper.add("data_setvariableto", {"VALUE": literal(wrap)}, {"VARIABLE": ["Xbox level choice", choice]})
        check = helper.add("control_if", {"CONDITION": [2, outside], "SUBSTACK": [2, reset_wrap]})
        menu = helper.add("operator_equals", {"OPERAND1": variable("page", page), "OPERAND2": literal("menu")})
        guarded = helper.add("control_if", {"CONDITION": [2, menu], "SUBSTACK": [2, helper.chain(change, check)]})
        helper.hat("event_whenkeypressed", {"KEY_OPTION": [key, None]}, guarded)
    costume = helper.add("looks_switchcostumeto", {"COSTUME": literal(1)})
    show = helper.add("looks_show")
    front = helper.add("looks_gotofrontback", fields={"FRONT_BACK": ["front", None]})
    label = helper.add("operator_join", {"STRING1": literal("Level "), "STRING2": variable("Xbox level choice", choice)})
    hint = helper.add("operator_join", {"STRING1": [2, label], "STRING2": literal("\nD-pad: choose; A: play\nFireboy: left/A\nWatergirl: right/X")})
    say = helper.add("looks_say", {"MESSAGE": [2, hint]})
    clear = helper.add("looks_say", {"MESSAGE": literal("")})
    hide = helper.add("looks_hide")
    menu = helper.add("operator_equals", {"OPERAND1": variable("page", page), "OPERAND2": literal("menu")})
    toggle = helper.add("control_if_else", {"CONDITION": [2, menu], "SUBSTACK": [2, helper.chain(costume, show, front, say)], "SUBSTACK2": [2, helper.chain(hide, clear)]})
    loop = helper.add("control_forever", {"SUBSTACK": [2, toggle]})
    helper.hat("event_whenflagclicked", {}, loop)
    costumes = []
    for number in [1]:
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"><rect width="4" height="4" fill="#172238"/></svg>'
        digest = hashlib.md5(svg).hexdigest()
        name = digest + ".svg"
        assets[name] = svg
        costumes.append(dict(name=str(number), bitmapResolution=1, dataFormat="svg", assetId=digest,
                             md5ext=name, rotationCenterX=2, rotationCenterY=2))
    project["targets"].append(dict(isStage=False, name="Xbox level menu", variables={}, lists={}, broadcasts={},
                                   blocks=helper.blocks, comments={}, currentCostume=0, costumes=costumes,
                                   sounds=[], volume=100, layerOrder=1000, visible=True, x=-220, y=-140,
                                   size=100, direction=90, draggable=False, rotationStyle="don't rotate"))
    # Verify every original block, variable and asset survives unchanged.
    for before, after in zip(original["targets"], project["targets"]):
        for field in ["blocks", "variables"]:
            assert all(after[field][key] == value for key, value in before[field].items())
        assert all(after[key] == value for key, value in before.items() if key not in ["blocks", "variables"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("project.json", json.dumps(project, separators=(",", ":")).encode()), *sorted(assets.items())]:
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    profile = {"controls": {"left arrow": ["dpadLeft", "LeftStickLeft"], "right arrow": ["dpadRight", "LeftStickRight"],
                            "up arrow": ["dpadUp", "LeftStickUp", "A"], "down arrow": ["dpadDown", "LeftStickDown"],
                            "a": ["RightStickLeft", "B"], "d": ["RightStickRight", "Y"],
                            "w": ["RightStickUp", "X"], "s": "RightStickDown", "r": "shoulderR"}}
    paths[1].write_text(json.dumps(profile, indent=2) + "\n")
    receipt = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
               "scope": "Controller level selection reuses authored locks/identify; one-controller dual-stick profile",
               "all_original_blocks_and_assets_preserved": True, "hardware_tested": False, "emulator_tested": False}
    paths[2].write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
