#!/usr/bin/env python3
"""Add controller Play/Home shortcuts to a separate Paint the Maze copy.

Reuses the original click handlers; leaves puzzles, progression, artwork,
credits, save/load and mouse controls intact. Profile: A Play, B Home,
Y Reset, directions to roll. The author's Z+P tool is not exposed.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile


def prepare(source, output):
    paths = [output, Path(str(output) + ".json"), Path(str(output) + ".preparation.json")]
    if source.resolve() == output.resolve() or any(p.exists() for p in paths):
        raise ValueError("Choose new output paths; existing files are never overwritten.")
    with zipfile.ZipFile(source) as archive:
        project = json.loads(archive.read("project.json"))
        assets = {n: archive.read(n) for n in archive.namelist() if n != "project.json"}
    original = copy.deepcopy(project)
    stage = next(t for t in project["targets"] if t["isStage"])
    flag = "xbox_paint_menu_visible"
    if flag in stage["variables"]:
        raise ValueError("This project already has the Xbox menu shortcuts.")
    stage["variables"][flag] = ["Xbox menu visible", 0]
    variables = {v[0]: k for k, v in stage["variables"].items()}
    broadcasts = {v: k for t in project["targets"] for k, v in t["broadcasts"].items()}
    if not all(n in variables for n in ["Quit", "LevelDesigner"]):
        raise ValueError("Expected the original Quit/LevelDesigner state.")
    if not all(n in broadcasts for n in ["ShowMenu", "HideMenu"]):
        raise ValueError("Expected original menu broadcasts.")

    def value(n):
        return [1, [10, str(n)]]

    def var(n):
        return [3, [12, n, variables[n]], [10, ""]]

    for name, key in [("Play", "space"), ("Home", "h")]:
        target = next(t for t in project["targets"] if t["name"] == name)
        blocks = target["blocks"]
        prefix = "xbox_paint_" + name.lower() + "_"
        extra = {}

        def add(opcode, inputs=None, fields=None, hat=False, body=None):
            identifier = prefix + str(len(extra) + 1)
            b = dict(opcode=opcode, next=body, parent=None, inputs=inputs or {},
                     fields=fields or {}, shadow=False, topLevel=hat)
            if hat:
                b.update(x=20, y=20)
            extra[identifier] = b
            if body:
                extra[body]["parent"] = identifier
            for inp in (inputs or {}).values():
                for child in inp[1:]:
                    if isinstance(child, str) and child in extra:
                        extra[child]["parent"] = identifier
            return identifier

        mapping = {}

        def clone(identifier):
            if identifier in mapping:
                return mapping[identifier]
            new = add(blocks[identifier]["opcode"])
            mapping[identifier] = new
            b = copy.deepcopy(blocks[identifier])
            extra[new] = b
            b.update(parent=None, topLevel=False)
            if b.get("next"):
                b["next"] = clone(b["next"])
                extra[b["next"]]["parent"] = new
            for inp in b.get("inputs", {}).values():
                for i in range(1, len(inp)):
                    if isinstance(inp[i], str) and inp[i] in blocks:
                        inp[i] = clone(inp[i])
                        extra[inp[i]]["parent"] = new
            return new

        clicks = [b for b in blocks.values() if isinstance(b, dict)
                  and b.get("opcode") == "event_whenthisspriteclicked"]
        if len(clicks) != 1 or not clicks[0].get("next"):
            raise ValueError("Expected one original " + name + " click handler.")
        body = clone(clicks[0]["next"])
        if name == "Play":
            menu = add("operator_equals", {"OPERAND1": var("Xbox menu visible"), "OPERAND2": value(1)})
            normal = add("operator_equals", {"OPERAND1": var("LevelDesigner"), "OPERAND2": value("FALSE")})
            condition = add("operator_and", {"OPERAND1": [2, menu], "OPERAND2": [2, normal]})
            for event, state in [(None, 0), ("ShowMenu", 1), ("HideMenu", 0)]:
                setter = add("data_setvariableto", {"VALUE": value(state)}, {"VARIABLE": ["Xbox menu visible", flag]})
                add("event_whenbroadcastreceived" if event else "event_whenflagclicked",
                    fields={"BROADCAST_OPTION": [event, broadcasts[event]]} if event else {},
                    hat=True, body=setter)
        else:
            condition = add("operator_equals", {"OPERAND1": var("Quit"), "OPERAND2": value("FALSE")})
        guarded = add("control_if", {"CONDITION": [2, condition], "SUBSTACK": [2, body]})
        add("event_whenkeypressed", fields={"KEY_OPTION": [key, None]}, hat=True, body=guarded)
        if set(extra) & set(blocks):
            raise ValueError("Prepared block ID collision.")
        blocks.update(extra)
    for before, after in zip(original["targets"], project["targets"]):
        for field in ["blocks", "variables"]:
            assert all(after[field][k] == v for k, v in before[field].items())
        assert all(after[k] == v for k, v in before.items() if k not in ["blocks", "variables"])
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for n, data in [("project.json", json.dumps(project, ensure_ascii=False, separators=(",", ":")).encode()), *sorted(assets.items())]:
            info = zipfile.ZipInfo(n, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    profile = {"controls": {
        "left arrow": ["dpadLeft", "LeftStickLeft"], "right arrow": ["dpadRight", "LeftStickRight"],
        "up arrow": ["dpadUp", "LeftStickUp"], "down arrow": ["dpadDown", "LeftStickDown"],
        "space": "A", "h": "B", "r": "Y"}}
    paths[1].write_text(json.dumps(profile, indent=2) + "\n")
    receipt = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
               "scope": "Prepared project: guarded Play/Home shortcuts reuse authored click handlers; controller profile",
               "all_original_blocks_and_assets_preserved": True, "hardware_tested": False, "emulator_tested": False}
    paths[2].write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
