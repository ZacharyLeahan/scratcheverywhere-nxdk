#!/usr/bin/env python3
"""Allow Space/A to activate Mushroom Valley's existing mouse-only Retry.

Keeps the authored restart sequence, physics, scoring, assets and mouse control.
Adds a small controller hint that appears alongside the original Retry icon.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile


def prepare(source, output):
    paths = [output, Path(str(output) + ".json"), Path(str(output) + ".preparation.json")]
    if source.resolve() == output.resolve() or any(path.exists() for path in paths):
        raise ValueError("Choose new output paths; existing files are never overwritten.")
    with zipfile.ZipFile(source) as archive:
        project = json.loads(archive.read("project.json"))
        assets = {name: archive.read(name) for name in archive.namelist() if name != "project.json"}
    original = copy.deepcopy(project)
    retry = next(target for target in project["targets"] if target["name"] == "スプライト1")
    blocks = retry["blocks"]
    candidates = []
    for key, block in blocks.items():
        if not isinstance(block, dict) or block.get("opcode") != "control_wait_until":
            continue
        condition = block["inputs"]["CONDITION"][1]
        test = blocks[condition]
        children = [blocks.get(value[1], {}) for value in test.get("inputs", {}).values() if isinstance(value[1], str)]
        if test.get("opcode") == "operator_and" and {child.get("opcode") for child in children} == {"sensing_mousedown", "sensing_touchingobject"}:
            candidates.append((key, condition))
    if len(candidates) != 1 or any(target["name"] == "Xbox retry hint" for target in project["targets"]):
        raise ValueError("Expected one original mouse-only Retry gate in an unprepared project.")
    wait, condition = candidates[0]

    def block(opcode, parent=None, inputs=None, fields=None, next_block=None, hat=False):
        result = dict(opcode=opcode, next=next_block, parent=parent, inputs=inputs or {},
                      fields=fields or {}, shadow=False, topLevel=hat)
        if hat:
            result.update(x=20, y=20)
        return result

    ids = ["xbox_retry_or", "xbox_retry_space", "xbox_retry_key"]
    if any(key in blocks for key in ids):
        raise ValueError("Unexpected prepared block ID collision.")
    blocks[ids[0]] = block("operator_or", wait, {"OPERAND1": [2, condition], "OPERAND2": [2, ids[1]]})
    blocks[ids[1]] = block("sensing_keypressed", ids[0], {"KEY_OPTION": [1, ids[2]]})
    blocks[ids[2]] = block("sensing_keyoptions", ids[1], fields={"KEY_OPTION": ["space", None]})
    blocks[ids[2]]["shadow"] = True
    blocks[condition]["parent"] = ids[0]
    blocks[wait]["inputs"]["CONDITION"] = [2, ids[0]]
    broadcasts = {}
    for target in project["targets"]:
        broadcasts.update({name: key for key, name in target["broadcasts"].items()})
    if not all(name in broadcasts for name in ["miss", "start"]):
        raise ValueError("Unexpected project revision: missing original loss/start broadcasts.")
    helper = {
        "xbox_hint_flag": block("event_whenflagclicked", next_block="xbox_hint_hide0", hat=True),
        "xbox_hint_hide0": block("looks_hide", "xbox_hint_flag"),
        "xbox_hint_miss": block("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": ["miss", broadcasts["miss"]]}, next_block="xbox_hint_wait", hat=True),
        "xbox_hint_wait": block("control_wait", "xbox_hint_miss", {"DURATION": [1, [5, "1"]]}, next_block="xbox_hint_show"),
        "xbox_hint_show": block("looks_show", "xbox_hint_wait"),
        "xbox_hint_start": block("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": ["start", broadcasts["start"]]}, next_block="xbox_hint_hide1", hat=True),
        "xbox_hint_hide1": block("looks_hide", "xbox_hint_start"),
    }
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="380" height="30"><rect width="380" height="30" rx="6" fill="#172238"/><text x="190" y="20" text-anchor="middle" font-family="sans-serif" font-size="16" fill="white">A: Retry | Hold/release A to jump</text></svg>'
    digest = hashlib.md5(svg).hexdigest()
    assets[digest + ".svg"] = svg
    project["targets"].append(dict(isStage=False, name="Xbox retry hint", variables={}, lists={}, broadcasts={},
                                   blocks=helper, comments={}, currentCostume=0,
                                   costumes=[dict(name="Xbox controls", bitmapResolution=1, dataFormat="svg", assetId=digest,
                                                  md5ext=digest + ".svg", rotationCenterX=190, rotationCenterY=15)],
                                   sounds=[], volume=100, layerOrder=1000, visible=False, x=0, y=-140,
                                   size=100, direction=90, draggable=False, rotationStyle="don't rotate"))
    for before, after in zip(original["targets"], project["targets"]):
        if before["name"] != retry["name"]:
            assert before == after
        else:
            restored = copy.deepcopy(after)
            for key in ids:
                del restored["blocks"][key]
            restored["blocks"][wait] = before["blocks"][wait]
            restored["blocks"][condition] = before["blocks"][condition]
            assert restored == before
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("project.json", json.dumps(project, ensure_ascii=False, separators=(",", ":")).encode()), *sorted(assets.items())]:
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    paths[1].write_text(json.dumps({"controls": {"space": "A"}}, indent=2) + "\n")
    receipt = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
               "scope": "Prepared-project Retry accepts Space in addition to original mouse gate; hint/profile added",
               "original_restart_sequence_and_physics_preserved": True, "hardware_tested": False, "emulator_tested": False}
    paths[2].write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
