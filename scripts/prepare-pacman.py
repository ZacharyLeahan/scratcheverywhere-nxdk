#!/usr/bin/env python3
"""Prepare cdaniels7088 PacMan with final high-score updates before stop-all.

The periodic high-score script can miss the last score change when an ending
stops every thread. Update the record before each ending, preserving a higher
previous record, original gameplay, assets, controls and credits.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile

SOURCE_SHA256 = "283feafd4c25cec72c09e9de3b76722aba3997c788342e340212f797fc7081d9"


def repair_end_score(project):
    if project.get("objName") != "Stage":
        raise ValueError("Expected the original PacMan stage")
    names = [v.get("name") for v in project.get("variables", [])]
    if any(names.count(n) != 1 for n in ("Score", "High Score")):
        raise ValueError("Expected unique global Score and High Score variables")
    endings = []
    for message, backdrop in [("GAME OVER", "backdrop1"), ("GAME WIN", "backdrop2")]:
        expected = [["whenIReceive", message], ["startScene", backdrop], ["stopScripts", "all"]]
        found = [s for s in project.get("scripts", []) if len(s) == 3 and s[2] == expected]
        if len(found) != 1:
            raise ValueError("Unexpected original ending script: " + message)
        endings.append(found[0])
    update = ["doIf", [">", ["readVariable", "Score"], ["readVariable", "High Score"]],
              [["setVar:to:", "High Score", ["readVariable", "Score"]]]]
    # Validate both original handlers before changing either one.
    for script in endings:
        script[2].insert(1, copy.deepcopy(update))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.source.resolve() == args.output.resolve():
        parser.error("Choose a new output archive; the original is preserved.")
    source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if source_hash != SOURCE_SHA256:
        parser.error("Expected the tested original cdaniels7088 PacMan archive.")
    with zipfile.ZipFile(args.source) as original:
        project = json.loads(original.read("project.json"))
        repair_end_score(project)
        with zipfile.ZipFile(args.output, "x") as prepared:
            for info in original.infolist():
                data = (json.dumps(project, separators=(",", ":")).encode()
                        if info.filename == "project.json" else original.read(info))
                prepared.writestr(info, data)
    print(json.dumps({"source": str(args.source), "output": str(args.output),
                      "source_sha256": source_hash,
                      "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "change": "Update final high score before Win/loss stop-all"}, indent=2))


if __name__ == "__main__":
    main()
