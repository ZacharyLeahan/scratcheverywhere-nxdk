#!/usr/bin/env python3
"""Prepare Catch Apples with special-apple scoring in its movement script.

The original's separate hide-on-contact loop can run before its scoring loop.
Handle a catch once before repositioning; retain the original five-second hide
on a miss, fall speeds, score values, sounds, assets, controls and credits.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile

SOURCE_SHA256 = "dfdc129664dff3a9b65f1c3523ba5d05f162e0b198b474cccc2cfd58cf7c1ede"


def repair_special_apples(project):
    for name, speed, points, sound in [
        ("Sprite1", -8, 2, "A-Tone-His_Self-1266414414.mp3"),
        ("Sprite3", -4, -2, "pop"),
    ]:
        sprites = [c for c in project["children"] if c.get("objName") == name]
        if len(sprites) != 1:
            raise ValueError("Expected one " + name)
        scripts = sprites[0]["scripts"]
        scoring = [["whenGreenFlag"], ["setVar:to:", "Score", 0], ["doForever", [
            ["doIf", ["touching:", "Bowl"], [
                ["playSound:", sound], ["changeVar:by:", "Score", points],
                ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180],
            ]],
        ]]]
        miss = [["hide"], ["wait:elapsed:from:", 5], ["show"],
                ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180]]
        movement = [["whenGreenFlag"], ["gotoSpriteOrMouse:", "_random_"], ["ypos:", 180],
                    ["doForever", [["changeYposBy:", speed], ["doIf",
                        ["|", ["<", ["ypos"], "-180"], ["touching:", "Bowl"]], miss]]]]
        scores = [s for s in scripts if s[2] == scoring]
        moves = [s for s in scripts if s[2] == movement]
        if len(scores) != 1 or len(moves) != 1:
            raise ValueError("Unexpected original scoring/movement scripts for " + name)
        # Retain the flag reset; only one thread may now award a special catch.
        scores[0][2] = copy.deepcopy(scoring[:2])
        moves[0][2][-1][1] = [
            ["changeYposBy:", speed],
            ["doIfElse", ["touching:", "Bowl"], copy.deepcopy(scoring[2][1][0][2]),
                [["doIf", ["<", ["ypos"], "-180"], copy.deepcopy(miss)]]],
        ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.source.resolve() == args.output.resolve():
        parser.error("Choose a new output archive; the original is preserved.")
    source_sha = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if source_sha != SOURCE_SHA256:
        parser.error("Expected the tested original superd1 Catch Apples archive.")
    with zipfile.ZipFile(args.source) as original:
        project = json.loads(original.read("project.json"))
        try:
            repair_special_apples(project)
        except (ValueError, KeyError) as error:
            parser.error(str(error))
        with zipfile.ZipFile(args.output, "x") as prepared:
            for info in original.infolist():
                data = (json.dumps(project, separators=(",", ":")).encode()
                        if info.filename == "project.json" else original.read(info))
                prepared.writestr(info, data)
    print(json.dumps({"source": str(args.source), "output": str(args.output),
                      "source_sha256": source_sha,
                      "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "change": "Handle each special catch and score in one script"}, indent=2))


if __name__ == "__main__":
    main()
