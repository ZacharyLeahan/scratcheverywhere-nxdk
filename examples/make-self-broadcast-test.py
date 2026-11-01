#!/usr/bin/env python3
"""Make a bounded scheduler fixture for broadcasts which restart their sender.

Expected after Green Flag: STARTS=TAIL=CLEARS=3. A tests self-broadcast-and-wait:
WAIT STARTS=2, WAIT TAIL=1. X/Y test explicit stop-this/stop-all: both tails stay 0.
This diagnostic is not a pack game. It never changes a game's project data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def make(output):
    blocks = {}
    variables = {name: [name, 0] for name in ["STARTS", "TAIL", "CLEARS", "WAIT STARTS", "WAIT TAIL", "STOP THIS TAIL", "STOP ALL TAIL"]}
    broadcasts = {name: name for name in ["Reset", "Clear", "WaitSelf"]}

    def add(opcode, inputs=None, fields=None, hat=False):
        key = "b" + str(len(blocks) + 1)
        blocks[key] = dict(opcode=opcode, next=None, parent=None, inputs=inputs or {}, fields=fields or {}, shadow=False, topLevel=hat)
        if hat:
            blocks[key].update(x=20, y=20)
        for inp in (inputs or {}).values():
            for child in inp[1:]:
                if isinstance(child, str) and child in blocks:
                    blocks[child]["parent"] = key
        return key

    def chain(*keys):
        for left, right in zip(keys, keys[1:]):
            blocks[left]["next"] = right
            blocks[right]["parent"] = left
        return keys[0]

    def change(name):
        return add("data_changevariableby", {"VALUE": [1, [4, "1"]]}, {"VARIABLE": [name, name]})

    def broadcast(name, wait=False):
        return add("event_broadcastandwait" if wait else "event_broadcast", {"BROADCAST_INPUT": [1, [11, name, name]]})

    flag = add("event_whenflagclicked", hat=True)
    reset = [add("data_setvariableto", {"VALUE": [1, [4, "0"]]}, {"VARIABLE": [name, name]}) for name in variables]
    chain(flag, *reset, broadcast("Reset"))
    hat = add("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": ["Reset", "Reset"]}, hat=True)
    body = chain(change("STARTS"), broadcast("Reset"), change("TAIL"), broadcast("Clear"))
    test = add("operator_lt", {"OPERAND1": [3, [12, "STARTS", "STARTS"], [10, ""]], "OPERAND2": [1, [4, "3"]]})
    chain(hat, add("control_if", {"CONDITION": [2, test], "SUBSTACK": [2, body]}))
    chain(add("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": ["Clear", "Clear"]}, hat=True), change("CLEARS"))
    chain(add("event_whenkeypressed", fields={"KEY_OPTION": ["space", None]}, hat=True), broadcast("WaitSelf"))
    wait_hat = add("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": ["WaitSelf", "WaitSelf"]}, hat=True)
    test = add("operator_lt", {"OPERAND1": [3, [12, "WAIT STARTS", "WAIT STARTS"], [10, ""]], "OPERAND2": [1, [4, "2"]]})
    branch = add("control_if", {"CONDITION": [2, test], "SUBSTACK": [2, broadcast("WaitSelf", True)]})
    chain(wait_hat, change("WAIT STARTS"), branch, change("WAIT TAIL"))
    for key, mode, counter in [("x", "this script", "STOP THIS TAIL"), ("y", "all", "STOP ALL TAIL")]:
        chain(add("event_whenkeypressed", fields={"KEY_OPTION": [key, None]}, hat=True),
              add("control_stop", fields={"STOP_OPTION": [mode, None]}), change(counter))
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#183044"/><text x="20" y="335" font-size="16" fill="white">Self-broadcast: expect STARTS / TAIL / CLEARS = 3</text></svg>'
    digest = hashlib.md5(svg).hexdigest()
    stage = dict(isStage=True, name="Stage", variables=variables, lists={}, broadcasts=broadcasts, blocks=blocks, comments={},
                 currentCostume=0, costumes=[dict(name="test", assetId=digest, md5ext=digest + ".svg", dataFormat="svg", bitmapResolution=1, rotationCenterX=240, rotationCenterY=180)],
                 sounds=[], volume=100, layerOrder=0, tempo=60, videoTransparency=50, videoState="on", textToSpeechLanguage=None)
    monitors = [dict(id=name, mode="default", opcode="data_variable", params={"VARIABLE": name}, spriteName=None, value=0,
                     width=0, height=0, x=20, y=12 + i * 36, visible=True, sliderMin=0, sliderMax=100, isDiscrete=True)
                for i, name in enumerate(variables)]
    project = dict(targets=[stage], monitors=monitors, extensions=[], meta=dict(semver="3.0.0", vm="0.2.0", agent="SE scheduler fixture"))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("project.json", json.dumps(project))
        archive.writestr(digest + ".svg", svg)
    Path(str(output) + ".json").write_text(json.dumps({"controls": {"space": "A", "x": "X", "y": "Y"}}, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    make(args.output)
    print(args.output)
