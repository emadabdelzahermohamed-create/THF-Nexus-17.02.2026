import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"

EXPECTED_COUNTS = {
    "Incline_Dumbbell_Press": 6,
    "Lateral_Raise_-_With_Bands": 4,
    "Leg_Extensions": 4,
    "Leverage_High_Row": 4,
    "Lying_Leg_Curls": 4,
    "Machine_Bench_Press": 6,
    "One-Arm_Dumbbell_Row": 6,
    "Side_Lateral_Raise": 4,
    "Smith_Machine_Bench_Press": 5,
    "Smith_Machine_Squat": 6,
}
GENERIC_FILLER = {
    "حرّك المفصل المستهدف فقط قدر الإمكان.",
    "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.",
    "عد ببطء وحافظ على شد العضلة.",
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح.",
    "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.",
    "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا.",
    "اسحب المرفقين للخلف دون هز الجذع.",
    "قرّب لوحي الكتف مع إبقاء الرقبة مرتاحة.",
    "مد الذراعين بتحكم من دون إسقاط الحمل.",
    "انزل بالحوض بتحكم مع بقاء القدم كاملة على الأرض.",
    "حافظ على ثبات الجذع وتتبع الركبة لاتجاه القدم.",
    "ادفع الأرض واصعد من دون قفل الركبتين بعنف.",
}
REQUIRED_ARABIC_TERMS = {
    "Incline_Dumbbell_Press": ("المقعد المائل", "الدمبلين", "لوحي الكتف"),
    "Lateral_Raise_-_With_Bands": ("المطاط", "الكتفين", "الرسغين"),
    "Leg_Extensions": ("الوسادة", "الركبتين", "الظهر"),
    "Leverage_High_Row": ("المرفقين", "المقبضين", "الكتفين"),
    "Lying_Leg_Curls": ("الكعبين", "الركبتين", "الحوض"),
    "Machine_Bench_Press": ("منتصف الصدر", "المقابض", "المرفقين"),
    "One-Arm_Dumbbell_Row": ("المقعد", "الدمبل", "الجذع"),
    "Side_Lateral_Raise": ("الدمبلين", "الكتفين", "الرسغين"),
    "Smith_Machine_Bench_Press": ("جهاز سميث", "الصدر", "الخطافات"),
    "Smith_Machine_Squat": ("البار", "الركبتين", "الخطافات"),
}


class StrengthInstructionParityBatch3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in catalog}

    def test_targeted_bilingual_step_counts_match_and_are_nonempty(self):
        for source_id, expected_count in EXPECTED_COUNTS.items():
            with self.subTest(source_id=source_id):
                steps = self.by_source_id[source_id]["steps"]
                self.assertEqual(expected_count, len(steps["en"]))
                self.assertEqual(expected_count, len(steps["ar"]))
                self.assertTrue(all(step.strip() for step in steps["en"]))
                self.assertTrue(all(step.strip() for step in steps["ar"]))

    def test_targeted_arabic_steps_are_specific_not_generic_filler(self):
        for source_id, terms in REQUIRED_ARABIC_TERMS.items():
            with self.subTest(source_id=source_id):
                steps = self.by_source_id[source_id]["steps"]["ar"]
                self.assertTrue(GENERIC_FILLER.isdisjoint(steps))
                joined = " ".join(steps)
                for term in terms:
                    self.assertIn(term, joined)


if __name__ == "__main__":
    unittest.main()
