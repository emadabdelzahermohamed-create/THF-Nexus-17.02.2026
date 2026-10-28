import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"

GENERIC_ARABIC_FILLER = {
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


class CatalogBilingualInstructionQualityBatch6Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        raw = RUNTIME_PATH.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
            raise AssertionError("Runtime catalog wrapper is invalid")
        cls.runtime = json.loads(raw[len(prefix):raw.rfind(";")])

    def test_all_112_exercises_have_nonblank_bilingual_steps_with_equal_counts(self):
        self.assertEqual(112, len(self.catalog))
        ids = [item["sourceItemId"] for item in self.catalog]
        self.assertEqual(len(ids), len(set(ids)), "Exercise source IDs must be unique")
        for item in self.catalog:
            with self.subTest(source_id=item["sourceItemId"]):
                steps = item["steps"]
                self.assertTrue(steps["en"] and steps["ar"])
                self.assertEqual(len(steps["en"]), len(steps["ar"]))
                self.assertTrue(all(isinstance(s, str) and s.strip() for s in steps["en"]))
                self.assertTrue(all(isinstance(s, str) and s.strip() for s in steps["ar"]))

    def test_known_generic_arabic_filler_is_absent_from_the_full_catalog(self):
        offenders = [
            (item["sourceItemId"], step)
            for item in self.catalog
            for step in item["steps"]["ar"]
            if step in GENERIC_ARABIC_FILLER
        ]
        self.assertEqual([], offenders)

    def test_runtime_javascript_payload_matches_generated_json_for_all_exercises(self):
        self.assertEqual(self.catalog, self.runtime)


if __name__ == "__main__":
    unittest.main()
