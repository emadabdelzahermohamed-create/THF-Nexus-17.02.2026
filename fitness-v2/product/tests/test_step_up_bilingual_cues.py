import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2/android/app/src/main/assets/pulse"
CATALOG_JSON = PULSE / "data/exercises.json"
CATALOG_JS = PULSE / "data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2/product/tools/build_catalog.py"

SPEC = importlib.util.spec_from_file_location("build_catalog", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = {
    "Barbell_Step_Ups": {
        "en": [
            "Set a low, stable, non-slip box in a clear area. Secure the bar across the upper back—not the neck—and brace before stepping.",
            "Place the whole lead foot on the box, keeping the knee aligned with the toes; drive through that planted foot rather than pushing hard from the trailing leg.",
            "Stand tall with control, then bring the trailing foot up only after balance is steady. Step down one foot at a time.",
            "Complete the planned reps on one lead leg, then switch. Lower the box or load, or use stable support, if balance or knee alignment slips; stop for pain."
        ],
        "ar": [
            "ضع صندوقًا منخفضًا وثابتًا وغير زلق في مساحة خالية. ثبّت البار على أعلى الظهر بعيدًا عن الرقبة، وشد الجذع قبل الصعود.",
            "ضع كامل القدم القائدة على الصندوق مع توجيه الركبة نحو أصابع القدم؛ ادفع بالقدم المرتكزة بدلًا من الدفع القوي بالساق الخلفية.",
            "قف باستقامة بتحكم، ثم ارفع القدم الخلفية بعد ثبات التوازن. انزل بقدم واحدة في كل مرة.",
            "أكمل العدات المقررة على ساق قائدة ثم بدّل. خفّض الصندوق أو الحمل أو استخدم دعمًا ثابتًا إذا اختل التوازن أو اتجاه الركبة، وتوقف عند الألم."
        ]
    },
    "Step-up_with_Knee_Raise": {
        "en": [
            "Choose a low, stable, non-slip step in a clear area; stand close with feet hip-width apart and brace the trunk.",
            "Place the whole lead foot on the step and rise by pressing through it; keep the knee tracking over the toes and avoid a forceful push from the trailing foot.",
            "At the top, lift the opposite knee only as high as balance allows, keeping the pelvis level and torso upright; pause briefly.",
            "Lower the raised foot, then step down one foot at a time under control. Alternate lead legs; reduce height or use support if balance or knee alignment slips, and stop for pain."
        ],
        "ar": [
            "اختر درجة منخفضة وثابتة وغير زلقة في مساحة خالية، وقف قريبًا والقدمان بعرض الورك مع شد الجذع.",
            "ضع كامل القدم القائدة على الدرجة واصعد بالدفع عبرها؛ اجعل الركبة في اتجاه أصابع القدم وتجنب الدفع القوي بالساق الخلفية.",
            "في الأعلى، ارفع الركبة المقابلة بقدر ما يسمح به التوازن، مع إبقاء الحوض مستويًا والجذع منتصبًا؛ اثبت لحظة.",
            "اخفض القدم المرفوعة ثم انزل بقدم واحدة في كل مرة بتحكم. بدّل الساق القائدة، وقلّل الارتفاع أو استخدم دعمًا إذا اختل التوازن أو اتجاه الركبة، وتوقف عند الألم."
        ]
    }
}


class StepUpBilingualCueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_JSON.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = CATALOG_JS.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_builder_overrides_have_aligned_bilingual_steps(self):
        self.assertEqual(BUILDER.STEP_INSTRUCTION_OVERRIDES, EXPECTED)
        for source_id, steps in EXPECTED.items():
            self.assertEqual(len(steps["en"]), 4, source_id)
            self.assertEqual(len(steps["ar"]), 4, source_id)
            self.assertTrue(all(value.strip() for value in steps["en"] + steps["ar"]))

    def test_generated_catalog_uses_the_exact_step_up_overrides(self):
        for source_id, expected in EXPECTED.items():
            item = next(value for value in self.catalog if value["sourceItemId"] == source_id)
            self.assertEqual(item["steps"], expected, source_id)
            self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]), source_id)

    def test_step_up_cues_cover_controlled_foot_placement_and_balance(self):
        barbell = next(value for value in self.catalog if value["sourceItemId"] == "Barbell_Step_Ups")
        knee_raise = next(value for value in self.catalog if value["sourceItemId"] == "Step-up_with_Knee_Raise")
        self.assertIn("whole lead foot", " ".join(barbell["steps"]["en"]))
        self.assertIn("أصابع القدم", " ".join(barbell["steps"]["ar"]))
        self.assertIn("only as high as balance allows", " ".join(knee_raise["steps"]["en"]))
        self.assertIn("بقدر ما يسمح به التوازن", " ".join(knee_raise["steps"]["ar"]))
        self.assertNotIn("as high as you can", " ".join(knee_raise["steps"]["en"]))

    def test_runtime_payload_and_manifest_match_exact_catalog(self):
        self.assertEqual(self.runtime, self.catalog)
        self.assertEqual(self.manifest["catalogSha256"], hashlib.sha256(self.catalog_bytes).hexdigest())


if __name__ == "__main__":
    unittest.main()
