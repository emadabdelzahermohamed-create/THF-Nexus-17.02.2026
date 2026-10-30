import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
RUNTIME_PATH = PULSE / "data" / "exercises.js"
CATALOG_PATH = PULSE / "data" / "exercises.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_strength_cues", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = {
    "Barbell_Squat": ("barbell-squat", "safety pins", "مسامير الأمان"),
    "Bent_Over_Barbell_Row": ("bent-over-barbell-row", "lower ribs", "الأضلاع السفلية"),
    "Dumbbell_Bench_Press": ("dumbbell-bench-press", "dumbbells", "الدمبل"),
    "Dumbbell_Bicep_Curl": ("dumbbell-bicep-curl", "upper arms", "العضدين"),
    "Dumbbell_Shoulder_Press": ("dumbbell-shoulder-press", "back support", "مسند ظهر"),
    "Parallel_Bar_Dip": ("parallel-bar-dip", "parallel bars", "العارضتين المتوازيتين"),
    "Barbell_Hip_Thrust": ("barbell-hip-thrust", "stable bench", "مقعد ثابت"),
    "Dumbbell_Step_Ups": ("dumbbell-step-ups", "whole working foot", "القدم العاملة كاملة"),
    "Seated_Cable_Rows": ("seated-cable-rows", "cable station", "جهاز الكيبل"),
    "Leg_Press": ("leg-press", "safety lever", "ذراع الأمان"),
}

GENERIC_ARABIC = {
    "ابدأ من جذع ثابت وتنفس دون حبس طويل.",
    "نفّذ الحركة ببطء ومن دون شد الرقبة.",
    "توقف قبل فقدان وضع الحوض أو أسفل الظهر.",
    "حرّك المفصل المستهدف فقط قدر الإمكان.",
    "توقف لحظة عند الانقباض من دون دفع أو رمي الحمل.",
    "عد ببطء وحافظ على شد العضلة.",
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح.",
    "أبقِ الساعد ثابتًا والكتف بعيدًا عن الأذن.",
    "ادفع بسلاسة مع الحفاظ على الجذع ثابتًا.",
    "اسحب المرفقين للخلف دون هز الجذع.",
    "قرّب لوحي الكتف مع إبقاء الرقبة مرتاحة.",
    "مد الذراعين بتحكم من دون إسقاط الحمل.",
    "ادفع الحمل لأعلى في مسار مريح.",
    "لا ترفع الكتفين نحو الأذنين ولا تقوس أسفل الظهر.",
    "اخفض الحمل ببطء إلى وضع البداية.",
    "انزل بالحوض بتحكم مع بقاء القدم كاملة على الأرض.",
    "حافظ على ثبات الجذع وتتبع الركبة لاتجاه القدم.",
    "ادفع الأرض واصعد من دون قفل الركبتين بعنف.",
    "ادفع الحوض للخلف مع ظهر محايد.",
    "توقف قبل أن تفقد ثبات الجذع أو موضع الحمل.",
    "اضغط بالأقدام ومد الحوض للعودة دون فرط تقوس الظهر.",
}


def load_runtime():
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("runtime exercise assignment wrapper changed")
    return json.loads(source[len(prefix):].strip().removesuffix(";"))


class StrengthInstructionSpecificityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = {item["sourceItemId"]: item for item in load_runtime()}
        cls.catalog = {item["sourceItemId"]: item for item in json.loads(CATALOG_PATH.read_text(encoding="utf-8"))}

    def test_ten_common_strength_exercises_have_specific_aligned_steps(self):
        self.assertEqual(112, len(self.runtime))
        self.assertEqual(112, len(self.catalog))
        for source_id, (runtime_id, english_cue, arabic_cue) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, BUILDER.STEP_OVERRIDES)
                steps = BUILDER.STEP_OVERRIDES[source_id]
                self.assertEqual(steps, self.catalog[source_id]["steps"])
                self.assertEqual(steps, self.runtime[source_id]["steps"])
                self.assertEqual(runtime_id, self.runtime[source_id]["id"])
                self.assertEqual(len(steps["en"]), len(steps["ar"]))
                self.assertGreaterEqual(len(steps["en"]), 4)
                self.assertTrue(all(cue.strip() for lang in ("en", "ar") for cue in steps[lang]))
                self.assertFalse(set(steps["ar"]) & GENERIC_ARABIC)
                self.assertIn(english_cue.lower(), " ".join(steps["en"]).lower())
                self.assertIn(arabic_cue, " ".join(steps["ar"]))


if __name__ == "__main__":
    unittest.main()
