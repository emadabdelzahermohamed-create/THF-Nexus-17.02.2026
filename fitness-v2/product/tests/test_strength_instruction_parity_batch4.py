import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"

EXPECTED_COUNTS = {
    "Standing_Calf_Raises": 5,
    "Tricep_Dumbbell_Kickback": 4,
    "Triceps_Pushdown_-_Rope_Attachment": 5,
    "Pushups": 4,
    "Single_Leg_Glute_Bridge": 4,
    "90_90_Hamstring": 4,
    "Inchworm": 5,
    "Standing_Hip_Circles": 4,
    "Calves-SMR": 2,
    "Latissimus_Dorsi-SMR": 2,
}

REQUIRED_ARABIC_TERMS = {
    "Standing_Calf_Raises": ("جهاز رفع السمانة", "الكعبين", "الكاحلين"),
    "Tricep_Dumbbell_Kickback": ("العضدين", "المرفقين", "دمبل"),
    "Triceps_Pushdown_-_Rope_Attachment": ("الحبل", "العضدين", "المرفقين"),
    "Pushups": ("بلانك", "الصدر", "الحوض"),
    "Single_Leg_Glute_Bridge": ("ساق", "الألوية", "الحوض"),
    "90_90_Hamstring": ("خلفية الفخذ", "الركبة", "بدّل الساق"),
    "Inchworm": ("امشِ باليدين", "بلانك", "القدمين"),
    "Standing_Hip_Circles": ("الركبة", "الورك", "بدّل الساق"),
    "Calves-SMR": ("الفوم رول", "السمانة", "تنميل"),
    "Latissimus_Dorsi-SMR": ("الفوم رول", "الظهر العريض", "الإبط"),
}

GENERIC_FILLER = {
    "حرّك المفصل المستهدف فقط قدر الإمكان.",
    "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.",
    "عد ببطء وحافظ على شد العضلة.",
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح.",
    "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.",
    "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا.",
    "ادفع الحوض للخلف مع ظهر محايد.",
    "توقف قبل أن تفقد ثبات الجذع أو موضع الحمل.",
    "اضغط بالأقدام ومد الحوض للعودة دون فرط تقوس الظهر.",
    "ادخل المدى ببطء حتى شد خفيف لا ألم.",
    "حافظ على الوضع والتنفس من دون ارتداد.",
    "اخرج من الوضع تدريجيًا وكرر على الجهة الأخرى عند الحاجة.",
    "تحرك ببطء على مساحة صغيرة.",
    "توقف فوق المنطقة المشدودة وتنفس من دون ضغط حاد.",
    "خفف الوزن فور ظهور تنميل أو ألم عصبي.",
}


class StrengthInstructionParityBatch4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in cls.catalog}

    def test_catalog_keeps_112_exercises_and_all_ten_cues_are_bilingual(self):
        self.assertEqual(112, len(self.catalog))
        for source_id, expected_count in EXPECTED_COUNTS.items():
            with self.subTest(source_id=source_id):
                steps = self.by_source_id[source_id]["steps"]
                self.assertEqual(expected_count, len(steps["en"]))
                self.assertEqual(expected_count, len(steps["ar"]))
                self.assertTrue(all(step.strip() for step in steps["en"]))
                self.assertTrue(all(step.strip() for step in steps["ar"]))
                self.assertFalse(any(step in GENERIC_FILLER for step in steps["ar"]))
                combined_arabic = " ".join(steps["ar"])
                for term in REQUIRED_ARABIC_TERMS[source_id]:
                    self.assertIn(term, combined_arabic)

    def test_runtime_javascript_matches_catalog_for_the_reviewed_batch(self):
        raw = RUNTIME_PATH.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        self.assertTrue(raw.startswith(prefix))
        payload_end = raw.rfind("];")
        runtime = json.loads(raw[len(prefix):payload_end + 1])
        runtime_by_id = {item["sourceItemId"]: item for item in runtime}
        self.assertEqual(112, len(runtime))
        for source_id in EXPECTED_COUNTS:
            with self.subTest(source_id=source_id):
                self.assertEqual(
                    self.by_source_id[source_id]["steps"],
                    runtime_by_id[source_id]["steps"],
                )

    def test_foam_roller_recovery_steps_stay_two_step_and_safety_specific(self):
        for source_id in ("Calves-SMR", "Latissimus_Dorsi-SMR"):
            with self.subTest(source_id=source_id):
                steps = self.by_source_id[source_id]["steps"]
                self.assertEqual(2, len(steps["en"]))
                self.assertEqual(2, len(steps["ar"]))
                arabic = " ".join(steps["ar"])
                self.assertIn("10–30", arabic)
                self.assertIn("تنميل", arabic)


if __name__ == "__main__":
    unittest.main()
