#!/usr/bin/env python3
"""Reconnect Candy Caves v1.2's detached map-clone initialization.

Creates a separate SB3 and controller sidecar. The source archive, artwork,
credits, generation rules and gameplay remain intact. No engine patch is used.
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
    target = next(t for t in project["targets"] if t["name"] == "map")
    blocks = target["blocks"]
    hats = [(key, b) for key, b in blocks.items()
            if isinstance(b, dict) and b.get("opcode") == "control_start_as_clone"]
    setters = [(key, b) for key, b in blocks.items()
               if isinstance(b, dict) and b.get("opcode") == "data_setvariableto"
               and b.get("fields", {}).get("VARIABLE", [None])[0] == "clone"
               and b.get("inputs", {}).get("VALUE") == [1, [10, "1"]]
               and b.get("topLevel") and b.get("parent") is None and b.get("next") is None]
    if len(hats) != 1 or len(setters) != 1 or hats[0][1].get("next") is not None:
        raise ValueError("Expected v1.2's empty map-clone hat and detached clone=1 block.")
    hat_id, hat = hats[0]
    setter_id, setter = setters[0]
    hat["next"] = setter_id
    setter.update(parent=hat_id, topLevel=False)
    setter.pop("x", None)
    setter.pop("y", None)
    for before, after in zip(original["targets"], project["targets"]):
        restored = copy.deepcopy(after)
        if after["name"] == "map":
            restored["blocks"][hat_id] = before["blocks"][hat_id]
            restored["blocks"][setter_id] = before["blocks"][setter_id]
        assert restored == before
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("project.json", json.dumps(project, ensure_ascii=False, separators=(",", ":")).encode()), *sorted(assets.items())]:
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    profile = {"controls": {
        "left arrow": ["dpadLeft", "LeftStickLeft"], "right arrow": ["dpadRight", "LeftStickRight"],
        "up arrow": ["dpadUp", "LeftStickUp"], "down arrow": ["dpadDown", "LeftStickDown"],
        "space": "A", "e": "X", "q": "Y"}}
    paths[1].write_text(json.dumps(profile, indent=2) + "\n")
    receipt = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
               "scope": "Prepared project: reconnect existing map clone=1 block to its empty clone-start hat",
               "changed_original_blocks": [hat_id, setter_id], "all_assets_preserved": True,
               "hardware_tested": False, "emulator_tested": False}
    paths[2].write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
