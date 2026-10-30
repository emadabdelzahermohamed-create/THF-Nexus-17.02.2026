import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
RUNTIME_PATH = PULSE / "data" / "exercises.js"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"

EXPECTED = {
    "straight-arm-dumbbell-pullover": (
        "Straight-Arm_Dumbbell_Pullover",
        "Pause briefly with the dumbbell steady over your chest, then repeat the same controlled arc only through a comfortable shoulder range; stop if the weight becomes unstable or shoulder pain occurs.",
        "توقف لحظة والدمبل ثابت فوق الصدر، ثم كرر القوس نفسه بمدى مريح للكتف؛ توقف إذا تعذر تثبيت الوزن أو ظهر ألم بالكتف.",
    ),
    "90-90-hamstring": (
        "90_90_Hamstring",
        "Extend the knee only until you feel a gentle hamstring stretch, then bend it back with control; keep the thigh supported and switch sides without forcing the range.",
        "مدّ الركبة حتى تشعر بشد لطيف في خلفية الفخذ، ثم اثنها بتحكم مع دعم الفخذ؛ بدّل الساق دون إجبار مدى الحركة.",
    ),
}


class ExerciseCueSafetyBatch13Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_PATH.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.by_id = {exercise["id"]: exercise for exercise in cls.catalog}

    def test_two_bilingual_cues_are_exact_and_step_counts_match(self):
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len(self.by_id))
        for exercise_id, (_, english, arabic) in EXPECTED.items():
            exercise = self.by_id[exercise_id]
            self.assertEqual(english, exercise["steps"]["en"][-1])
            self.assertEqual(arabic, exercise["steps"]["ar"][-1])
            self.assertEqual(len(exercise["steps"]["en"]), len(exercise["steps"]["ar"]))
            self.assertTrue(all(step.strip() for step in exercise["steps"]["en"] + exercise["steps"]["ar"]))

    def test_catalog_runtime_and_offline_demo_mapping_remain_consistent(self):
        self.assertEqual(self.catalog, self.runtime)
        for exercise_id, (source_id, _, _) in EXPECTED.items():
            exercise = self.by_id[exercise_id]
            self.assertEqual(source_id, exercise["sourceItemId"])
            self.assertTrue(exercise["demo"]["offline"])
            self.assertEqual(2, len(exercise["demo"]["assets"]))
            self.assertTrue(all(
                asset.startswith(f"media/free-exercise-db/{source_id}/")
                for asset in exercise["demo"]["assets"]
            ))

    def test_builder_preserves_both_reviewed_bilingual_cues(self):
        for exercise_id, (source_id, english, arabic) in EXPECTED.items():
            start = self.builder.index(f'    "{source_id}": {{')
            end = self.builder.find("\\n    },", start)
            self.assertGreaterEqual(start, 0, exercise_id)
            self.assertGreater(end, start, exercise_id)
            block = self.builder[start:end]
            self.assertIn(english, block, exercise_id)
            self.assertIn(arabic, block, exercise_id)

    def test_manifest_matches_exact_catalog_bytes(self):
        self.assertEqual(hashlib.sha256(self.catalog_bytes).hexdigest(), self.manifest["catalogSha256"])


if __name__ == "__main__":
    unittest.main()
