import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"

EXPECTED_COUNTS = {
    "Piriformis-SMR": 2,
    "Quadriceps-SMR": 2,
    "External_Rotation_with_Band": 5,
    "Full_Range-Of-Motion_Lat_Pulldown": 2,
    "One_Arm_Lat_Pulldown": 4,
    "Straight-Arm_Dumbbell_Pullover": 6,
    "Medicine_Ball_Chest_Pass": 5,
    "Single-Leg_Lateral_Hop": 4,
    "Dancers_Stretch": 4,
    "Spinal_Stretch": 4,
}

REQUIRED_ARABIC_TERMS = {
    "Piriformis-SMR": ("الفوم رول", "الألوية", "10–30", "تنميل"),
    "Quadriceps-SMR": ("الفوم رول", "مقدمة الفخذ", "10–30", "تنميل"),
    "External_Rotation_with_Band": ("المطاط", "90 درجة", "المرفق", "الساعد"),
    "Full_Range-Of-Motion_Lat_Pulldown": ("البكرتين", "المقبضين", "الكفان"),
    "One_Arm_Lat_Pulldown": ("وسادة الفخذ", "المرفق", "لوح الكتف"),
    "Straight-Arm_Dumbbell_Pullover": ("الدمبل", "المقعد", "أسفل الظهر"),
    "Medicine_Ball_Chest_Pass": ("الكرة الطبية", "الصدر", "الشريك"),
    "Single-Leg_Lateral_Hop": ("حاجز", "الركبة", "اهبط"),
    "Dancers_Stretch": ("اجلس على الأرض", "الفخذ الأيمن", "10–20"),
    "Spinal_Stretch": ("كرسي", "الحوض", "الرقبة"),
}

GENERIC_FILLER = {
    "حرّك المفصل المستهدف فقط قدر الإمكان.",
    "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.",
    "عد ببطء وحافظ على شد العضلة.",
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح.",
    "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.",
    "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا.",
    "ادخل المدى ببطء حتى شد خفيف لا ألم.",
    "حافظ على الوضع والتنفس من دون ارتداد.",
    "اخرج من الوضع تدريجيًا وكرر على الجهة الأخرى عند الحاجة.",
    "تحرك ببطء على مساحة صغيرة.",
    "توقف فوق المنطقة المشدودة وتنفس من دون ضغط حاد.",
    "خفف الوزن فور ظهور تنميل أو ألم عصبي.",
}


class StrengthInstructionParityBatch5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in cls.catalog}

    def test_catalog_has_112_exercises_and_ten_bilingual_sequences_match_english_counts(self):
        self.assertEqual(112, len(self.catalog))
        for source_id, expected_count in EXPECTED_COUNTS.items():
            with self.subTest(source_id=source_id):
                steps = self.by_source_id[source_id]["steps"]
                self.assertEqual(expected_count, len(steps["en"]))
                self.assertEqual(expected_count, len(steps["ar"]))
                self.assertTrue(all(step.strip() for step in steps["en"]))
                self.assertTrue(all(step.strip() for step in steps["ar"]))
                self.assertFalse(any(step in GENERIC_FILLER for step in steps["ar"]))
                arabic = " ".join(steps["ar"])
                for term in REQUIRED_ARABIC_TERMS[source_id]:
                    self.assertIn(term, arabic)

    def test_runtime_javascript_matches_generated_json_for_all_target_exercises(self):
        raw = RUNTIME_PATH.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        self.assertTrue(raw.startswith(prefix))
        payload_end = raw.rfind("];")
        runtime = json.loads(raw[len(prefix):payload_end + 1])
        self.assertEqual(112, len(runtime))
        runtime_by_id = {item["sourceItemId"]: item for item in runtime}
        for source_id in EXPECTED_COUNTS:
            with self.subTest(source_id=source_id):
                self.assertEqual(self.by_source_id[source_id]["steps"], runtime_by_id[source_id]["steps"])

    def test_foam_roller_cues_include_duration_and_stop_conditions(self):
        for source_id in ("Piriformis-SMR", "Quadriceps-SMR"):
            with self.subTest(source_id=source_id):
                arabic = " ".join(self.by_source_id[source_id]["steps"]["ar"])
                self.assertIn("10–30", arabic)
                self.assertIn("تنميل", arabic)
                self.assertIn("الفوم رول", arabic)


if __name__ == "__main__":
    unittest.main()
