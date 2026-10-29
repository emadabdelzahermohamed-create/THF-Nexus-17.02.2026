import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
RUNTIME_PATH = PULSE / "data" / "exercises.js"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"

EXPECTED = {
    "standing-dumbbell-calf-raise": (
        "Standing_Dumbbell_Calf_Raise",
        "Keep your torso upright and the dumbbells still at your sides; repeat each heel raise without bouncing or rolling onto the outer edges of your feet.",
        "اخفض الكعبين ببطء مع إبقاء الركبتين والجذع ثابتين.",
    ),
    "leg-extensions": (
        "Leg_Extensions",
        "Keep your hips against the seat and repeat with the same controlled range, without swinging your torso or snapping the knees straight.",
        "اخفض الوزن ببطء مع الشهيق إلى مدى مريح، وقلّل الحمل أو المدى إذا ظهر ألم بالركبة.",
    ),
    "fast-skipping": (
        "Fast_Skipping",
        "Perform fast skips by maintaining close contact with the ground and reduce air time, moving as quickly as possible.",
        "زد سرعة القفز مع إبقاء زمن الطيران قصيرًا والقدمين قريبين من الأرض.",
    ),
    "machine-bench-press": (
        "Machine_Bench_Press",
        "Return the handles to the start under control without letting the weight stack collide; keep your shoulders down and stop if you feel pain.",
        "أعد المقابض إلى وضع البداية بتحكم دون اصطدام الأوزان، وتوقف إذا ظهر ألم.",
    ),
    "barbell-deadlift": (
        "Barbell_Deadlift",
        "Reset your brace before each repetition, keep the bar close to your legs, and stop the set if you cannot maintain a neutral spine or secure grip.",
        "أعد ضبط شد الجذع قبل كل عدة، وأبقِ البار قريبًا من الساقين؛ أوقف المجموعة إذا تعذر الحفاظ على ظهر محايد أو قبضة ثابتة.",
    ),
    "lying-leg-curls": (
        "Lying_Leg_Curls",
        "Lower the pad slowly until your knees reach a comfortable extension; keep your hips against the bench and reduce the load if you feel knee pain.",
        "أنزل الوسادة ببطء حتى امتداد مريح للركبتين، وأبقِ الوركين على المقعد؛ خفّف الحمل إذا ظهر ألم بالركبة.",
    ),
}

FAST_SKIPPING_ARABIC_STEPS = [
    "ابدأ في وضع مريح مع تقديم إحدى القدمين قليلًا.",
    "نفّذ نمط خطوة وقفزة بالتبادل: يمين–يمين–خطوة انتقال، ثم يسار–يسار–خطوة انتقال.",
    "زد سرعة القفز مع إبقاء زمن الطيران قصيرًا والقدمين قريبين من الأرض.",
]


class ExerciseSpecificFinalCuesBatch11Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_PATH.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_final_english_cues_are_exercise_specific(self):
        by_id = {item["id"]: item for item in self.catalog}
        for exercise_id, (_, cue, _) in EXPECTED.items():
            self.assertEqual(cue, by_id[exercise_id]["steps"]["en"][-1])
            self.assertNotEqual("Repeat for the recommended amount of times.", cue)

    def test_arabic_cues_and_step_counts_are_preserved(self):
        by_id = {item["id"]: item for item in self.catalog}
        for exercise_id, (_, _, arabic_final) in EXPECTED.items():
            exercise = by_id[exercise_id]
            self.assertEqual(arabic_final, exercise["steps"]["ar"][-1])
            self.assertEqual(len(exercise["steps"]["en"]), len(exercise["steps"]["ar"]))
            self.assertTrue(all(step.strip() for step in exercise["steps"]["en"] + exercise["steps"]["ar"]))

    def test_fast_skipping_arabic_steps_match_the_reviewed_bilingual_override(self):
        by_id = {item["id"]: item for item in self.catalog}
        self.assertEqual(FAST_SKIPPING_ARABIC_STEPS, by_id["fast-skipping"]["steps"]["ar"])
        self.assertEqual(len(by_id["fast-skipping"]["steps"]["en"]), len(FAST_SKIPPING_ARABIC_STEPS))
        for cue in FAST_SKIPPING_ARABIC_STEPS:
            self.assertIn(cue, self.builder)

    def test_catalog_and_runtime_payload_match(self):
        self.assertEqual(self.catalog, self.runtime)

    def test_builder_keeps_reviewed_steps_on_regeneration(self):
        for _, (source_id, cue, _) in EXPECTED.items():
            self.assertIn(f'"{source_id}": {{', self.builder)
            self.assertIn(cue, self.builder)

    def test_manifest_matches_exact_catalog_bytes(self):
        self.assertEqual(hashlib.sha256(self.catalog_bytes).hexdigest(), self.manifest["catalogSha256"])


if __name__ == "__main__":
    unittest.main()
