"""Archive integrity and revision guards for the Xbox Jumper preparation."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


PREPARE = Path(__file__).resolve().parents[1] / "scripts/prepare-jumper.py"
WON = ["=", ["readVariable", "level"], "21"]


def project():
    clock = [
        ["whenIReceive", "Start"], ["setVar:to:", "Timer", 0],
        ["wait:elapsed:from:", 1],
        ["doUntil", False, [
            ["changeVar:by:", "Timer", 0.1], ["wait:elapsed:from:", 0.1],
            ["doIf", copy.deepcopy(WON), [["stopScripts", "this script"]]],
            ["doIf", ["=", ["readVariable", "back"], "1"],
             [["hideVariable:", "Timer"], ["stopScripts", "this script"]]],
        ]],
    ]
    children = [{"objName": name, "scripts": []}
                for name in ["Play", "Player", "Line", "Platform", "Text1"]]
    children[0]["scripts"] = [[10, 10, [
        ["whenIReceive", "Back"], ["show"], ["gotoX:y:", 0, -180],
        ["wait:elapsed:from:", 0.8], ["doRepeat", 25, [["changeYposBy:", 1]]],
    ]]]
    children[-1]["scripts"] = [
        [10, 10, clock],
        [10, 100, [["whenIReceive", "Restart"], ["setVar:to:", "Timer", 0]]],
        [10, 200, [["whenIReceive", "Start"], ["setVar:to:", "play1", 10],
                   ["doUntil", False, [["hide"], ["stopScripts", "this script"]]]]],
    ]
    return {"objName": "Stage", "scripts": [], "children": children,
            "variables": [{"name": name, "value": 0, "isPersistent": False}
                          for name in ["Start", "Highscore?!", "Timer", "level", "back"]]}


class PrepareJumperTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "original.sb2"
        self.profile = self.root / "original.sb2.json"
        self.output = self.root / "xbox.sb2"
        self.profile.write_text(json.dumps({"controls": {
            "space": "A", "up arrow": ["DPAD_UP"], "y": "Y", "r": "BLACK"}}))

    def prepare(self, data):
        with zipfile.ZipFile(self.source, "w") as archive:
            archive.writestr("project.json", json.dumps(data))
            archive.writestr("asset.bin", b"unchanged asset and credits\x00")
        self.source_bytes = self.source.read_bytes()
        self.profile_bytes = self.profile.read_bytes()
        return subprocess.run([sys.executable, str(PREPARE), str(self.source),
                               str(self.profile), str(self.output)], capture_output=True, text=True)

    def assert_inputs_preserved(self):
        self.assertEqual(self.source.read_bytes(), self.source_bytes)
        self.assertEqual(self.profile.read_bytes(), self.profile_bytes)

    def test_only_victory_stop_changes_in_clock(self):
        original = project()
        result = self.prepare(original)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output) as archive:
            prepared = json.loads(archive.read("project.json"))
            self.assertEqual(archive.read("asset.bin"), b"unchanged asset and credits\x00")
        old_clock = original["children"][-1]["scripts"]
        clock = prepared["children"][-1]["scripts"]
        self.assertEqual(clock[1], old_clock[1])  # Existing Restart still only resets Timer.
        win_body = clock[0][2][-1][2][2][2]
        self.assertEqual(win_body[-1], ["doWaitUntil", ["not", WON]])
        win_body[-1] = ["stopScripts", "this script"]
        self.assertEqual(clock, old_clock)  # Includes the separate Back stop and waits.
        controls = json.loads(Path(str(self.output) + ".json").read_text())["controls"]
        self.assertIn("A", controls["up arrow"])
        self.assertEqual(controls["g"], "Y")
        self.assert_inputs_preserved()

    def test_rejects_changed_victory_semantics(self):
        data = project()
        data["children"][-1]["scripts"][0][2][-1][2][2][2][-1] = ["stopScripts", "all"]
        result = self.prepare(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("original victory timer stop", result.stderr)
        self.assertFalse(self.output.exists())
        self.assertFalse(Path(str(self.output) + ".json").exists())
        self.assert_inputs_preserved()

    def test_rejects_missing_clock(self):
        data = project()
        data["children"][-1]["scripts"] = []
        result = self.prepare(data)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("original Start timer script", result.stderr)
        self.assertFalse(self.output.exists())
        self.assert_inputs_preserved()

    def test_does_not_overwrite_existing_output(self):
        self.output.write_bytes(b"keep this file")
        result = self.prepare(project())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), b"keep this file")
        self.assert_inputs_preserved()


if __name__ == "__main__":
    unittest.main()
