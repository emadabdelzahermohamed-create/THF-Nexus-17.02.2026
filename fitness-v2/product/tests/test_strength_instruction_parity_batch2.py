import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
RUNTIME_PATH = PULSE / "data" / "exercises.js"
CATALOG_PATH = PULSE / "data" / "exercises.json"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_strength_parity_batch2", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = {
    "Dips_-_Triceps_Version": ("dips---triceps-version", "elbows close to your sides", "المرفقين قريبين"),
    "Barbell_Step_Ups": ("barbell-step-ups", "elevated platform", "الصندوق"),
    "Platform_Hamstring_Slides": ("platform-hamstring-slides", "gym towel", "الكعبين"),
    "Standing_Dumbbell_Calf_Raise": ("standing-dumbbell-calf-raise", "contracting the calves", "السمانة"),
    "Cable_Crossover": ("cable-crossover", "pulleys", "البكرتين"),
    "Close-Grip_Front_Lat_Pulldown": ("close-grip-front-lat-pulldown", "knee pad", "وسادة الفخذين"),
    "Dip_Machine": ("dip-machine", "press the handles down", "مقابض الجهاز"),
    "Face_Pull": ("face-pull", "forehead", "الجبهة"),
    "Front_Barbell_Squat": ("front-barbell-squat", "squat rack", "مسامير الأمان"),
    "Hammer_Curls": ("hammer-curls", "elbows close to your torso", "الكفان في وضع محايد"),
}

RENAMED_AND_RECATEGORIZED = {
    "Barbell_Step_Ups": "صعود الصندوق بالبار",
    "Platform_Hamstring_Slides": "انزلاق الكعبين لثني خلفية الفخذ",
    "Standing_Dumbbell_Calf_Raise": "رفع السمانة واقفًا بالدمبل",
}
GENERIC_ARABIC = {
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح.",
    "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.",
    "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا.",
    "حرّك المفصل المستهدف فقط قدر الإمكان.",
    "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.",
    "عد ببطء وحافظ على شد العضلة.",
    "اسحب المرفقين للخلف دون هز الجذع.",
    "قرّب لوحي الكتف مع إبقاء الرقبة مرتاحة.",
    "مد الذراعين بتحكم من دون إسقاط الحمل.",
    "انزل بالحوض بتحكم مع بقاء القدم كاملة على الأرض.",
    "حافظ على ثبات الجذع وتتبع الركبة لاتجاه القدم.",
    "ادفع الأرض واصعد من دون قفل الركبتين بعنف.",
}

def load_runtime():
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("runtime exercise assignment wrapper changed")
    return json.loads(source[len(prefix):].strip().removesuffix(";"))

class StrengthInstructionParityBatchTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = {item["sourceItemId"]: item for item in load_runtime()}
        cls.catalog = {item["sourceItemId"]: item for item in json.loads(CATALOG_PATH.read_text(encoding="utf-8"))}
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_ten_targeted_exercises_have_specific_bilingual_step_parity(self):
        self.assertEqual(112, len(self.runtime))
        self.assertEqual(112, len(self.catalog))
        for source_id, (runtime_id, en_cue, ar_cue) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, BUILDER.STEP_OVERRIDES)
                steps = BUILDER.STEP_OVERRIDES[source_id]
                self.assertEqual(steps, self.catalog[source_id]["steps"])
                self.assertEqual(steps, self.runtime[source_id]["steps"])
                self.assertEqual(runtime_id, self.runtime[source_id]["id"])
                self.assertEqual(len(steps["en"]), len(steps["ar"]))
                self.assertGreaterEqual(len(steps["en"]), 4)
                self.assertTrue(all(step.strip() for lang in ("en", "ar") for step in steps[lang]))
                self.assertFalse(set(steps["ar"]) & GENERIC_ARABIC)
                self.assertIn(en_cue.lower(), " ".join(steps["en"]).lower())
                self.assertIn(ar_cue, " ".join(steps["ar"]))

    def test_three_strength_exercises_are_not_misclassified_as_cycling(self):
        for source_id, expected_name in RENAMED_AND_RECATEGORIZED.items():
            with self.subTest(source_id=source_id):
                for item in (self.catalog[source_id], self.runtime[source_id]):
                    self.assertEqual(expected_name, item["name"]["ar"])
                    self.assertEqual("gym", item["section"]["id"])
                    self.assertEqual("gym", item["sport"])
                    self.assertNotIn("للدراجات", item["name"]["ar"])
                    self.assertIn(expected_name, item["demo"]["alt"]["ar"])
        self.assertEqual(39, self.manifest["sectionCounts"]["gym"])
        self.assertEqual(3, self.manifest["sectionCounts"]["cycling"])

if __name__ == "__main__":
    unittest.main()
