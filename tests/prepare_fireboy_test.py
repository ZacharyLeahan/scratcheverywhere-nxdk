"""Archive preservation and authored-menu revision checks for Fireboy preparation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


PREPARE = Path(__file__).resolve().parents[1] / "scripts/prepare-fireboy-watergirl.py"


def block(opcode, **kwargs):
    return dict(opcode=opcode, next=None, parent=None, inputs={}, fields={},
                shadow=False, topLevel=False, **kwargs)


def project():
    home = {
        "click": block("event_whenthisspriteclicked"),
        "guard": block("control_if"),
        "condition": block("operator_equals"),
        "identify": block("procedures_call"),
        "reporter": block("operator_join"),
    }
    home["click"].update(next="guard", topLevel=True, x=20, y=30)
    home["guard"].update(parent="click", inputs={"CONDITION": [2, "condition"],
                                               "SUBSTACK": [2, "identify"]})
    home["condition"].update(parent="guard", inputs={"OPERAND1": [3, [12, "clone id", "clone"], [10, ""]],
                                                    "OPERAND2": [1, [10, "1"]]})
    home["identify"].update(parent="guard", mutation={"proccode": "identify %s", "argumentids": '["arg"]', "warp": "true"},
                            inputs={"arg": [3, "reporter", [10, "fallback"]]})
    home["reporter"].update(parent="identify", inputs={"STRING1": [1, [10, "original "]], "STRING2": [1, [10, "argument"]]})
    sign = {
        "click": block("event_whenthisspriteclicked"), "choice": block("control_if_else"),
        "is-menu": block("operator_equals"), "costume": block("looks_costumenumbername"),
        "wait": block("control_wait"), "menu": block("data_setvariableto"),
        "hide": block("event_broadcast"), "retry": block("event_broadcast"),
    }
    sign["click"].update(next="choice", topLevel=True, x=100, y=200)
    sign["choice"].update(parent="click", inputs={"CONDITION": [2, "is-menu"],
                                                "SUBSTACK": [2, "wait"], "SUBSTACK2": [2, "retry"]})
    sign["is-menu"].update(parent="choice", inputs={"OPERAND1": [3, "costume", [10, ""]], "OPERAND2": [1, [10, "button"]]})
    sign["costume"].update(parent="is-menu", fields={"NUMBER_NAME": ["name", None]})
    sign["wait"].update(parent="choice", next="menu", inputs={"DURATION": [1, [5, "0.1"]]})
    sign["menu"].update(parent="wait", next="hide", fields={"VARIABLE": ["page", "page"]}, inputs={"VALUE": [1, [10, "menu"]]})
    sign["hide"].update(parent="menu", inputs={"BROADCAST_INPUT": [1, [11, "hide signs", "hide"]]})
    sign["retry"].update(parent="choice", inputs={"BROADCAST_INPUT": [1, [11, "retry", "retry"]]})
    return {"targets": [
        {"isStage": True, "name": "Stage", "variables": {"page": ["page", "menu"], "progress": ["earned progress", "keep"]},
         "broadcasts": {"ready": "ready", "hide": "hide signs", "won": "game won", "lost": "game lost"}, "blocks": {},
         "lists": {}, "comments": {"credit": {"text": "original author credits"}}},
        {"isStage": False, "name": "home", "variables": {"clone": ["clone id", 1]}, "blocks": home,
         "broadcasts": {}, "costumes": [{"name": "authored level icon"}], "x": 12, "y": 34},
        {"isStage": False, "name": "sign", "variables": {}, "blocks": sign,
         "broadcasts": {}, "costumes": [{"name": n} for n in ["lost", "won", "button", "retry"]], "x": 0, "y": -300},
    ], "meta": {"agent": "original project metadata"}}


def canonical(blocks, root):
    """Compare copied graph content without relying on generated block IDs."""
    item = copy.deepcopy(blocks[root])
    for key in ["parent", "topLevel", "x", "y"]:
        item.pop(key, None)
    if item.get("next"):
        item["next"] = canonical(blocks, item["next"])
    for value in item["inputs"].values():
        for index in range(1, len(value)):
            if isinstance(value[index], str) and value[index] in blocks:
                value[index] = canonical(blocks, value[index])
    return item


class PrepareFireboyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "original.sb3"
        self.output = self.root / "xbox.sb3"

    def prepare(self, data, output=None):
        with zipfile.ZipFile(self.source, "w") as archive:
            archive.writestr("project.json", json.dumps(data))
            archive.writestr("authored-asset.bin", b"original artwork/audio\x00")
        self.original_bytes = self.source.read_bytes()
        return subprocess.run([sys.executable, str(PREPARE), str(self.source), str(output or self.output)],
                              capture_output=True, text=True)

    def test_assets_original_graphs_and_progress_survive(self):
        original = project()
        result = self.prepare(original)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output) as archive:
            prepared = json.loads(archive.read("project.json"))
            self.assertEqual(archive.read("authored-asset.bin"), b"original artwork/audio\x00")
        self.assertEqual(self.source.read_bytes(), self.original_bytes)
        for before, after in zip(original["targets"], prepared["targets"]):
            for field in ["blocks", "variables"]:
                self.assertTrue(all(after[field][key] == value for key, value in before[field].items()))
            self.assertEqual({k: v for k, v in before.items() if k not in ["blocks", "variables"]},
                             {k: v for k, v in after.items() if k not in ["blocks", "variables"]})
        # Both copied authored stacks retain reporters, mutations, waits and the
        # original Menu/Retry branch structure; no custom replacement action.
        for name, prefix, old_root in [("home", "xbox_level_home_", "guard"), ("sign", "xbox_results_sign_", "choice")]:
            old = next(t for t in original["targets"] if t["name"] == name)["blocks"]
            new = next(t for t in prepared["targets"] if t["name"] == name)["blocks"]
            hat = next(b for k, b in new.items() if k.startswith(prefix) and b["opcode"] == "event_whenkeypressed")
            guard = new[hat["next"]]
            self.assertEqual(canonical(new, guard["inputs"]["SUBSTACK"][1]), canonical(old, old_root))
        controls = json.loads(Path(str(self.output) + ".json").read_text())["controls"]
        self.assertIn("B", controls["a"])
        self.assertEqual(controls["r"], "shoulderR")

    def test_changed_menu_costume_is_rejected_without_output(self):
        data = project()
        data["targets"][2]["blocks"]["is-menu"]["inputs"]["OPERAND2"][1][1] = "retry"
        result = self.prepare(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authored results Menu button", result.stderr)
        self.assertFalse(self.output.exists())
        self.assertFalse(Path(str(self.output) + ".json").exists())
        self.assertEqual(self.source.read_bytes(), self.original_bytes)

    def test_existing_output_is_not_overwritten(self):
        self.output.write_bytes(b"keep")
        result = self.prepare(project())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), b"keep")

    def test_preparation_is_deterministic(self):
        data = project()
        result = self.prepare(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        other = self.root / "second.sb3"
        result = self.prepare(data, other)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_bytes(), other.read_bytes())


if __name__ == "__main__":
    unittest.main()
