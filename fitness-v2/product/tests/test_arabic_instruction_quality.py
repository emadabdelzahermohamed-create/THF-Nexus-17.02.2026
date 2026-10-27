import json
from pathlib import Path
import unittest


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "android/app/src/main/assets/pulse/data/exercises.js"
)

EXPECTED_ARABIC_CUES = {
    "barbell-deadlift": (
        "منتصف القدمين",
        "ادفع الأرض بالقدمين",
        "ادفع الورك للخلف",
    ),
    "romanian-deadlift": (
        "اثنِ الركبتين قليلًا",
        "ادفع الورك للخلف",
        "دون تحويل الحركة إلى سكوات",
    ),
    "barbell-bench-press---medium-grip": (
        "تثبيت القدمين ولوحي الكتف",
        "يلامس منتصف الصدر",
        "الحواجز أو مساعد عند الحاجة",
    ),
    "pullups": (
        "قبضة أمامية",
        "اسحب المرفقين لأسفل والخلف",
        "اخفض الجذع ببطء",
    ),
    "handstand-push-ups": (
        "واجهًا للجدار",
        "وسادة ثابتة",
        "انزل بمساعدة",
    ),
    "barbell-shoulder-press": (
        "ارفع البار أمام الرأس",
        "شد البطن وثبات القدمين",
        "اخفض البار ببطء إلى الكتفين",
    ),
    "front-box-jump": (
        "صندوقًا ثابتًا بارتفاع مناسب",
        "اهبط على الصندوق بركبتين مثنيتين",
        "انزل خطوة خطوة",
    ),
}


EXPECTED_STEP_COUNTS = {
    "barbell-deadlift": 5,
    "romanian-deadlift": 5,
    "barbell-bench-press---medium-grip": 5,
    "pullups": 5,
    "handstand-push-ups": 5,
    "barbell-shoulder-press": 5,
    "front-box-jump": 4,
}


class ArabicInstructionQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = DATA_PATH.read_text(encoding="utf-8")
        payload = source.split("=", 1)[1].strip().removesuffix(";")
        cls.exercises = json.loads(payload)
        cls.by_id = {item["id"]: item for item in cls.exercises}

    def test_key_movements_have_specific_arabic_steps(self):
        for exercise_id, phrases in EXPECTED_ARABIC_CUES.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(exercise_id, self.by_id)
                steps = self.by_id[exercise_id]["steps"]["ar"]
                self.assertEqual(len(steps), EXPECTED_STEP_COUNTS[exercise_id])
                joined = " ".join(steps)
                for phrase in phrases:
                    self.assertIn(phrase, joined)
                self.assertNotIn("اخفض الحمل أو الجسم بتحكم حتى مدى مريح", joined)

    def test_selected_movements_do_not_share_one_generic_step_template(self):
        step_sets = [
            tuple(self.by_id[exercise_id]["steps"]["ar"])
            for exercise_id in EXPECTED_ARABIC_CUES
        ]
        self.assertEqual(len(step_sets), len(set(step_sets)))


if __name__ == "__main__":
    unittest.main()
