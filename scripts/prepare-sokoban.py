#!/usr/bin/env python3
"""Prepare a separate Gammastr20 Sokoban archive with audited puzzle repairs.

The default repairs puzzle ten. --all-puzzles also repairs the completed-goal
scan and the final puzzles' height/start metadata. Preserve the source archive
and every asset; only the documented project data and counter are changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument(
    "--all-puzzles", action="store_true",
    help="Also repair the completed-goal counter, puzzle twelve height and puzzle thirteen start.")
args = parser.parse_args()
if args.source.resolve() == args.output.resolve() or args.output.exists():
    parser.error("Choose a new output archive; the original is preserved.")
source_sha = hashlib.sha256(args.source.read_bytes()).hexdigest()
if source_sha != "6b2ea446a14651efe37bc6589172a05309371d1c8db1d9ce8a267848827e5013":
    parser.error("Expected the tested original Gammastr20 Sokoban archive.")

changes = [(12, 3), (12, 4), (7, 5)]
with zipfile.ZipFile(args.source) as original:
    project = json.loads(original.read("project.json"))
    data_lists = [x for x in project.get("lists", []) if x.get("listName") == "Data"]
    if len(data_lists) != 1 or len(data_lists[0]["contents"]) != 13:
        parser.error("Expected the original thirteen-puzzle Data list.")
    levels = data_lists[0]["contents"]
    level = levels[9]
    if level[:8] != "08151300" or len(level[8:]) != 8 * 15:
        parser.error("Unexpected tenth-puzzle dimensions or player start.")
    cells = list(level[8:])
    for x, y in changes:
        index = y * 15 + x
        if cells[index] != "0":
            parser.error("Expected an inaccessible cell at the repair location.")
        cells[index] = "1"
    levels[9] = level[:8] + "".join(cells)

    if args.all_puzzles:
        # The final floor row is loaded but never drawn with the authored height.
        level12 = levels[11]
        if level12[:8] != "09070105" or len(level12[8:]) != 10 * 7:
            parser.error("Unexpected twelfth-puzzle dimensions or player start.")
        levels[11] = "10" + level12[2:]

        # Move one cell up onto existing floor; preserve every map cell.
        level13 = levels[12]
        if (level13[:8] != "09170907" or len(level13[8:]) != 9 * 17 or
                level13[8:][7 * 17 + 9] != "0" or level13[8:][6 * 17 + 9] != "1"):
            parser.error("Unexpected thirteenth-puzzle start or support tile.")
        levels[12] = level13[:6] + "06" + level13[8:]

        # Count every one-based map item, including the first goal in puzzles nine/twelve.
        tiles = next(child for child in project["children"] if child.get("objName") == "Tiles")
        tick = next(script[2] for script in tiles["scripts"] if script[2][0][:2] == ["procDef", "Tick"])
        counters = [i for i, block in enumerate(tick[:-2])
                    if block == ["setVar:to:", "t_i", "1"] and
                    tick[i + 1] == ["setVar:to:", "t_cCube", 0] and
                    tick[i + 2][:2] == ["doRepeat", ["lineCountOfList:", "Level"]]]
        if len(counters) != 1 or tick[counters[0] + 2][2][0] != ["changeVar:by:", "t_i", 1]:
            parser.error("Unexpected completed-goal scan in Tiles Tick.")
        tick[counters[0]][2] = "0"

    with zipfile.ZipFile(args.output, "x") as prepared:
        for info in original.infolist():
            data = json.dumps(project, separators=(",", ":")).encode() if info.filename == "project.json" else original.read(info)
            prepared.writestr(info, data)

print(json.dumps({
    "source": str(args.source), "output": str(args.output),
    "source_sha256": source_sha,
    "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    "change": ("Repair puzzles ten/twelve/thirteen and completed-goal counter" if args.all_puzzles
               else "Open three access cells in puzzle ten; preserve crates and goals"),
    "floor_cells_zero_based": changes,
    "additional_puzzle_repairs": ([
        {"level": 12, "height": [9, 10]},
        {"level": 13, "start": [[9, 7], [9, 6]]},
        {"levels": [9, 12], "goal_scan_first_index": [2, 1]},
    ] if args.all_puzzles else []),
}, indent=2))
