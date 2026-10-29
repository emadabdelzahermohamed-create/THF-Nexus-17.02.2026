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
    "one-arm-dumbbell-row": (
        "One-Arm_Dumbbell_Row",
        "Lower the dumbbell slowly until your arm is extended beneath the shoulder; keep your torso square, then finish the reps and switch sides.",
        "اخفض الدمبل ببطء حتى تمتد الذراع أسفل الكتف مع ثبات الجذع، ثم أكمل العدات وبدّل الجهة.",
    ),
    "cable-crossover": (
        "Cable_Crossover",
        "Return the handles along the same controlled arc without letting the weight stack collide; keep a slight elbow bend and stop if the shoulder hurts.",
        "أعد المقبضين بالقوس المتحكم نفسه دون اصطدام الأوزان؛ حافظ على ثني بسيط للمرفقين وتوقف إذا ظهر ألم بالكتف.",
    ),
    "close-grip-front-lat-pulldown": (
        "Close-Grip_Front_Lat_Pulldown",
        "Return the bar slowly until your arms are extended without shrugging or swinging; keep the bar in front of you and stop if shoulder pain develops.",
        "أعد البار ببطء حتى تمتد الذراعان دون رفع الكتفين أو تأرجح الجذع؛ أبقِ البار أمامك وتوقف إذا ظهر ألم بالكتف.",
    ),
    "one-arm-medicine-ball-slam": (
        "One-Arm_Medicine_Ball_Slam",
        "Control the rebound only if the ball is designed to rebound; otherwise let it settle before retrieving it. Reset your stance and clear the area before the next slam.",
        "سيطر على الارتداد فقط إذا كانت الكرة مصممة لذلك؛ وإلا فاتركها تستقر قبل التقاطها. أعد ضبط الوقفة وأخلِ المنطقة قبل الرمية التالية.",
    ),
    "pushups": (
        "Pushups",
        "Keep your head, hips, and heels aligned as you lower your chest under control; press back up without letting your hips sag, and stop when you cannot maintain that line.",
        "حافظ على استقامة الرأس والحوض والكعبين أثناء خفض الصدر بتحكم؛ ادفع للأعلى دون هبوط الحوض، وتوقف إذا تعذر الحفاظ على استقامة الجسم.",
    ),
}


class ExerciseCueSafetyBatch12Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_PATH.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.by_id = {exercise["id"]: exercise for exercise in cls.catalog}

    def test_five_bilingual_cues_are_exact_and_step_counts_match(self):
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len(self.by_id))
        for exercise_id, (_, english, arabic) in EXPECTED.items():
            exercise = self.by_id[exercise_id]
            self.assertEqual(english, exercise["steps"]["en"][-1])
            self.assertEqual(arabic, exercise["steps"]["ar"][-1])
            self.assertEqual(len(exercise["steps"]["en"]), len(exercise["steps"]["ar"]))
            self.assertTrue(all(step.strip() for step in exercise["steps"]["en"] + exercise["steps"]["ar"]))

    def test_close_grip_pulldown_numbering_artifact_is_removed(self):
        cue = self.by_id["close-grip-front-lat-pulldown"]["steps"]["en"][-1]
        self.assertFalse(cue.startswith("6."))
        self.assertIn("return the bar slowly", cue.lower())

    def test_medicine_ball_retrieval_does_not_assume_a_bouncing_ball(self):
        english = self.by_id["one-arm-medicine-ball-slam"]["steps"]["en"][-1]
        arabic = self.by_id["one-arm-medicine-ball-slam"]["steps"]["ar"][-1]
        self.assertIn("only if the ball is designed to rebound", english)
        self.assertIn("مصممة لذلك", arabic)
        self.assertIn("let it settle before retrieving it", english)

    def test_catalog_runtime_and_offline_demo_mapping_remain_consistent(self):
        self.assertEqual(self.catalog, self.runtime)
        self.assertTrue(all(item["demo"]["offline"] for item in self.catalog))
        self.assertTrue(all(len(item["demo"]["assets"]) == 2 for item in self.catalog))
        self.assertTrue(all(
            all(f'/{item["sourceItemId"]}/' in asset for asset in item["demo"]["assets"])
            for item in self.catalog
        ))
        self.assertEqual(224, sum(len(item["demo"]["assets"]) for item in self.catalog))

    def test_builder_preserves_all_five_reviewed_bilingual_cues(self):
        for exercise_id, (source_id, english, arabic) in EXPECTED.items():
            start = self.builder.index(f'    "{source_id}": {{')
            end = self.builder.find("\n    },", start)
            self.assertGreaterEqual(start, 0)
            self.assertGreater(end, start)
            block = self.builder[start:end]
            self.assertIn(english, block, exercise_id)
            self.assertIn(arabic, block, exercise_id)

    def test_manifest_matches_exact_catalog_bytes(self):
        self.assertEqual(
            hashlib.sha256(self.catalog_bytes).hexdigest(),
            self.manifest["catalogSha256"],
        )


if __name__ == "__main__":
    unittest.main()
