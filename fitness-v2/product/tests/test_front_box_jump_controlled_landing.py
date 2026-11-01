import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_JSON = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.json"
CATALOG_JS = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2/product/tools/build_catalog.py"

EXPECTED = {
    "en": [
        "Place a low, stable box on a non-slip surface with clear space around it; choose a height you can reach with control.",
        "Stand facing the box with feet about hip-width apart, knees soft, and eyes on the landing surface.",
        "Dip through the hips and knees, swing the arms, and jump with both feet onto the box; use only enough height to land quietly.",
        "Land with the whole foot and knees tracking over the toes; stand tall and regain balance, then step down one foot at a time—do not jump off the box.",
        "Repeat only while every landing remains quiet and stable; use a lower box or stop if balance or knee alignment slips or pain develops.",
    ],
    "ar": [
        "ضع صندوقًا منخفضًا وثابتًا على سطح غير زلق وأخلِ المساحة حوله؛ اختر ارتفاعًا تستطيع الوصول إليه بتحكم.",
        "قف أمام الصندوق والقدمان بعرض الوركين تقريبًا والركبتان مرتخيتان، وانظر إلى سطح الهبوط.",
        "اثنِ الوركين والركبتين قليلًا، وحرّك الذراعين ثم اقفز بكلتا القدمين إلى الصندوق؛ استخدم ارتفاعًا يكفي لهبوط هادئ.",
        "اهبط بكامل القدم مع توجيه الركبتين نحو أصابع القدم، واعتدل واستعد التوازن، ثم انزل قدمًا بعد الأخرى—لا تقفز من الصندوق إلى الأرض.",
        "كرر فقط ما دام كل هبوط هادئًا وثابتًا؛ اخفض الصندوق أو توقف إذا اختل التوازن أو محاذاة الركبتين أو ظهر ألم.",
    ],
}

def load_builder():
    spec = importlib.util.spec_from_file_location("build_catalog_front_box_jump", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FrontBoxJumpControlledLandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_JSON.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = CATALOG_JS.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.builder = load_builder()
        cls.target = next(item for item in cls.catalog if item["sourceItemId"] == "Front_Box_Jump")

    def test_five_bilingual_steps_match_builder_json_and_runtime(self):
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len({item["id"] for item in self.catalog}))
        self.assertEqual(EXPECTED, self.builder.STEP_OVERRIDES["Front_Box_Jump"])
        self.assertEqual(EXPECTED, self.target["steps"])
        runtime_target = next(item for item in self.runtime if item["sourceItemId"] == "Front_Box_Jump")
        self.assertEqual(EXPECTED, runtime_target["steps"])
        self.assertEqual(len(EXPECTED["en"]), len(EXPECTED["ar"]))
        self.assertTrue(all(step.strip() for step in EXPECTED["en"] + EXPECTED["ar"]))

    def test_jump_cues_bound_effort_and_require_a_controlled_step_down(self):
        english = " ".join(EXPECTED["en"]).lower()
        for phrase in ("as high as possible", "rebound out of this position", "jump from the box back to the ground"):
            self.assertNotIn(phrase, english)
        self.assertIn("step down one foot at a time", english)
        self.assertIn("quiet and stable", english)
        self.assertIn("stop", english)
        arabic = " ".join(EXPECTED["ar"])
        self.assertIn("انزل قدمًا بعد الأخرى", arabic)
        self.assertIn("لا تقفز من الصندوق إلى الأرض", arabic)
        self.assertIn("توقف", arabic)

    def test_offline_demo_and_prescription_are_preserved(self):
        self.assertEqual(self.target["demo"]["assets"], [
            "media/free-exercise-db/Front_Box_Jump/0.jpg",
            "media/free-exercise-db/Front_Box_Jump/1.jpg",
        ])
        self.assertTrue(self.target["demo"]["offline"])
        self.assertEqual(self.target["prescription"]["sets"], 3)
        self.assertEqual(self.target["prescription"]["reps"], "5–8")
        self.assertEqual(self.target["prescription"]["restSeconds"], 90)
        self.assertFalse(self.target["tracking"]["load"])
        self.assertTrue(self.target["tracking"]["volume"])

    def test_runtime_payload_and_manifest_match_exact_catalog_bytes(self):
        self.assertEqual(self.catalog, self.runtime)
        self.assertEqual(hashlib.sha256(self.catalog_bytes).hexdigest(), self.manifest["catalogSha256"])

if __name__ == "__main__":
    unittest.main()
