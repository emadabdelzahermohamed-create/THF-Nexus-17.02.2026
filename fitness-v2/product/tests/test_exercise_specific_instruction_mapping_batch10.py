import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data"
CATALOG_PATH = DATA_DIR / "exercises.json"
RUNTIME_PATH = DATA_DIR / "exercises.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_batch10", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = {
    "Scapular_Pull-Up": {
        "id": "scapular-pull-up",
        "en": [
            "Hang from a pull-up bar with an overhand grip, arms straight and body still.",
            "Without bending your elbows, draw the shoulder blades down and slightly together to lift your body a few inches; do not swing or shrug toward your ears.",
            "Pause briefly, then slowly release the shoulder blades to return to a controlled hang before repeating."
        ],
        "ar": [
            "تعلّق بعارضة العقلة بقبضة علوية والذراعان ممدودتان، مع إبقاء الجسم ثابتًا.",
            "اسحب لوحي الكتف إلى أسفل وإلى الداخل قليلًا لرفع الجسم بضعة سنتيمترات دون ثني المرفقين أو التأرجح.",
            "توقف لحظة ثم أرخِ لوحي الكتف ببطء للعودة إلى تعليق متحكم فيه قبل التكرار."
        ]
    },
    "Kettlebell_One-Legged_Deadlift": {
        "id": "kettlebell-one-legged-deadlift",
        "en": [
            "Stand on one leg holding the kettlebell in the hand on the same side, keep a soft bend in the stance knee, and brace your trunk.",
            "Hinge at the hip while reaching the free leg straight behind you; keep your hips level and the bell close to the stance leg.",
            "Lower only as far as you can maintain balance and a neutral spine, keeping pressure through the whole stance foot.",
            "Drive through the stance foot and extend the hip to stand; reset your balance before the next repetition, then switch sides."
        ],
        "ar": [
            "قف على ساق واحدة وامسك الكيتل بيل باليد من الجهة نفسها، مع ثني بسيط لركبة الارتكاز وشد الجذع.",
            "ادفع الورك للخلف ومد الساق الحرة خلفك، مع إبقاء الحوض مستويًا والجرس قريبًا من ساق الارتكاز.",
            "اخفض الجرس بقدر ما يسمح بالحفاظ على التوازن والظهر المحايد، مع توزيع الضغط على القدم الداعمة كاملة.",
            "ادفع بالأرض بقدم الارتكاز ومد الورك للعودة إلى الوقوف؛ استعد للتوازن قبل التكرار التالي ثم بدّل الجهة."
        ]
    }
}

def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

def load_runtime():
    raw = RUNTIME_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
        raise AssertionError("Runtime exercise payload wrapper is invalid")
    return json.loads(raw[len(prefix):raw.rfind(";")].strip())

class ExerciseSpecificInstructionBatch10Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
        cls.catalog = load_catalog()
        cls.runtime = load_runtime()
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.by_id = {item["id"]: item for item in cls.catalog}

    def test_catalog_runtime_manifest_and_unique_ids_stay_synchronized(self):
        self.assertEqual(self.catalog, self.runtime)
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len(self.by_id))
        self.assertEqual(hashlib.sha256(self.catalog_text.encode("utf-8")).hexdigest(), self.manifest["catalogSha256"])

    def test_reviewed_steps_match_catalog_and_builder(self):
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                item = self.by_id[expected["id"]]
                self.assertEqual(source_id, item["sourceItemId"])
                self.assertEqual(expected["en"], item["steps"]["en"])
                self.assertEqual(expected["ar"], item["steps"]["ar"])
                self.assertEqual(expected["en"], BUILDER.STEP_OVERRIDES[source_id]["en"])
                self.assertEqual(expected["ar"], BUILDER.STEP_OVERRIDES[source_id]["ar"])

    def test_scapular_pullup_keeps_elbows_straight(self):
        steps = self.by_id["scapular-pull-up"]["steps"]
        self.assertEqual(3, len(steps["en"]))
        self.assertEqual(3, len(steps["ar"]))
        self.assertIn("Without bending your elbows", steps["en"][1])
        self.assertIn("دون ثني المرفقين", steps["ar"][1])
        self.assertNotIn("اسحب بالمرفقين", " ".join(steps["ar"]))

    def test_single_leg_deadlift_is_a_hip_hinge_with_balance_control(self):
        steps = self.by_id["kettlebell-one-legged-deadlift"]["steps"]
        self.assertEqual(4, len(steps["en"]))
        self.assertEqual(4, len(steps["ar"]))
        self.assertIn("Hinge at the hip", steps["en"][1])
        self.assertIn("مد الساق الحرة خلفك", steps["ar"][1])
        self.assertIn("neutral spine", steps["en"][2])
        self.assertIn("الظهر المحايد", steps["ar"][2])

    def test_all_bilingual_steps_remain_nonblank_and_count_aligned(self):
        for item in self.catalog:
            with self.subTest(exercise_id=item["id"]):
                en, ar = item["steps"]["en"], item["steps"]["ar"]
                self.assertTrue(en and ar)
                self.assertEqual(len(en), len(ar))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in en))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in ar))

if __name__ == "__main__":
    unittest.main()
