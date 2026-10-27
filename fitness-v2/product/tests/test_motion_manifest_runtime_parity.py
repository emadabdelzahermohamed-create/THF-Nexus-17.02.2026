import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
JSON_MANIFEST_PATH = PULSE / "data" / "motion-manifest.json"
JS_MANIFEST_PATH = PULSE / "data" / "motion-manifest.js"


def load_runtime_manifest():
    source = JS_MANIFEST_PATH.read_text(encoding="utf-8")
    marker = "window.THF_MOTION_MANIFEST = "
    start = source.find(marker)
    if start < 0:
        raise AssertionError("runtime motion manifest assignment is missing")
    object_start = start + len(marker)
    end = source.find("\n};", object_start)
    if end < 0:
        raise AssertionError("runtime motion manifest object terminator is missing")
    return json.loads(source[object_start:end + 2].strip())


class MotionManifestRuntimeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json_manifest = json.loads(JSON_MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.runtime_manifest = load_runtime_manifest()

    def test_runtime_manifest_matches_json_runtime_fields_exactly(self):
        # The JSON manifest may carry editorial review notes; runtime JS should not.
        expected = {
            exercise_id: {
                key: value
                for key, value in entry.items()
                if key != "review"
            }
            for exercise_id, entry in self.json_manifest.items()
        }
        self.assertEqual(expected, self.runtime_manifest)

    def test_every_manifest_entry_has_a_supported_kind_and_local_asset_contract(self):
        self.assertEqual(7, len(self.json_manifest))
        self.assertEqual(set(self.json_manifest), set(self.runtime_manifest))
        for exercise_id, entry in self.json_manifest.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(entry.get("kind"), {"offline_video", "verified_frame_sequence"})
                self.assertRegex(entry.get("asset", ""), r"^media/motion/[a-z0-9-]+\.(mp4|webm)$")
                self.assertRegex(entry.get("sha256", ""), r"^[0-9a-f]{64}$")
                self.assertEqual(entry["asset"], self.runtime_manifest[exercise_id]["asset"])
                self.assertEqual(entry["sha256"], self.runtime_manifest[exercise_id]["sha256"])

    def test_editorial_review_notes_are_nonblank_json_only_metadata(self):
        reviewed = {
            exercise_id
            for exercise_id, entry in self.json_manifest.items()
            if "review" in entry
        }
        self.assertEqual({"bodyweight-squat", "pushups"}, reviewed)
        self.assertTrue(all(self.json_manifest[key]["review"].strip() for key in reviewed))
        self.assertTrue(all("review" not in entry for entry in self.runtime_manifest.values()))


if __name__ == "__main__":
    unittest.main()
