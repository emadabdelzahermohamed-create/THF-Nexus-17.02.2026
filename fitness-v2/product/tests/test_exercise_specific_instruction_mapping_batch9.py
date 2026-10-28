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

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_batch9", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = {
    "Bodyweight_Squat": {
        "id": "bodyweight-squat",
        "en": [
            "Stand with feet about shoulder-width apart and turn the toes slightly outward; extend your arms forward for balance.",
            "Brace your trunk, send your hips back, and bend your knees while keeping both heels on the floor.",
            "Lower to a comfortable depth you can control, with your knees tracking over your toes and your back staying neutral.",
            "Push through the whole foot and exhale to stand tall without bouncing out of the bottom."
        ],
        "ar": [
            "قف والقدمان بعرض الكتفين مع توجيه أصابع القدمين للخارج قليلًا، ومد الذراعين أمامك للتوازن.",
            "شد الجذع وابدأ بدفع الوركين للخلف وثني الركبتين مع إبقاء الكعبين على الأرض.",
            "انزل إلى عمق مريح يمكن التحكم فيه، مع توجيه الركبتين نحو أصابع القدمين والحفاظ على ظهر محايد.",
            "ادفع الأرض بالقدم كاملة وازفر للعودة إلى الوقوف، دون ارتداد من أسفل الحركة."
        ]
    },
    "Goblet_Squat": {
        "id": "goblet-squat",
        "en": [
            "Stand with feet about shoulder-width apart and hold a dumbbell or kettlebell close to your chest, elbows pointing down.",
            "Brace your trunk and sit your hips between your knees, keeping the load close to your chest.",
            "Lower only as far as you can control while keeping your heels grounded and knees tracking over your toes.",
            "Exhale and drive through the whole foot to stand without letting your knees collapse inward."
        ],
        "ar": [
            "قف والقدمان بعرض الكتفين، وامسك دمبلًا أو كيتل بيل أمام الصدر مع إبقاء المرفقين إلى أسفل.",
            "شد الجذع وادفع الوركين للخلف مع ثني الركبتين، وأبقِ الحمل قريبًا من الصدر.",
            "انزل إلى مدى تستطيع التحكم فيه مع بقاء الكعبين على الأرض والركبتين في اتجاه أصابع القدمين.",
            "ازفر وادفع الأرض بالقدم كاملة للوقوف، دون السماح للركبتين بالانهيار إلى الداخل."
        ]
    },
    "One-Arm_Kettlebell_Swings": {
        "id": "one-arm-kettlebell-swings",
        "en": [
            "Stand with feet about shoulder-width apart, hold the kettlebell in one hand, and keep the free arm available for balance.",
            "Hinge at the hips and guide the bell between your thighs, keeping a neutral spine and soft knees.",
            "Drive the hips forward to send the bell to about chest height; let the hip snap power the swing rather than lifting with the shoulder.",
            "Allow the bell to fall, then hinge back to guide it between your thighs without turning the movement into a deep squat.",
            "Finish with control, park the bell safely, and switch hands only after the bell has settled."
        ],
        "ar": [
            "قف والقدمان بعرض الكتفين، وأمسك الكيتل بيل بيد واحدة مع إبقاء الذراع الحرة للمساعدة في التوازن.",
            "ادفع الوركين للخلف ومرّر الجرس بين الفخذين مع ثني بسيط للركبتين والحفاظ على ظهر محايد.",
            "مد الوركين للأمام بحركة قوية ومضبوطة لإرسال الجرس إلى مستوى الصدر؛ دع قوة الورك تولّد المرجحة بدل رفع الحمل بالكتف وحده.",
            "دع الجرس يهبط ثم ادفع الوركين للخلف ليمر بين الفخذين، دون تحويل الحركة إلى قرفصاء عميقة.",
            "أنه المجموعة بتحكم وضع الجرس بأمان، ولا تبدّل اليد إلا بعد استقرار الجرس."
        ]
    },
    "Catch_and_Overhead_Throw": {
        "id": "catch-and-overhead-throw",
        "en": [
            "Stand facing a partner or a sturdy wall with a clear rebound area, holding the medicine ball securely with both hands.",
            "Bring the ball behind your head only within a comfortable shoulder range, then extend your arms to throw it forward toward the partner or target.",
            "Track the rebound and prepare to receive the ball with both hands; choose a distance that allows a safe catch, then reset before repeating."
        ],
        "ar": [
            "قف مقابل شريك أو جدار ثابت مع إخلاء مساحة الارتداد، وامسك الكرة الطبية بإحكام بكلتا اليدين.",
            "ارفع الكرة خلف الرأس ضمن مدى مريح للكتفين، ثم مد الذراعين لرميها إلى الأمام باتجاه الشريك أو الهدف.",
            "تابع مسار ارتداد الكرة واستعد لاستقبالها بكلتا اليدين؛ اختر مسافة تسمح بالتقاط آمن ثم ثبّت وقفتك قبل التكرار."
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

class ExerciseSpecificInstructionBatch9Test(unittest.TestCase):
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

    def test_all_steps_remain_bilingual_nonblank_and_count_aligned(self):
        for item in self.catalog:
            with self.subTest(exercise_id=item["id"]):
                en, ar = item["steps"]["en"], item["steps"]["ar"]
                self.assertTrue(en and ar)
                self.assertEqual(len(en), len(ar))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in en))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in ar))

    def test_reviewed_exercise_cues_match_catalog_and_builder(self):
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                item = self.by_id[expected["id"]]
                self.assertEqual(source_id, item["sourceItemId"])
                self.assertEqual(expected["en"], item["steps"]["en"])
                self.assertEqual(expected["ar"], item["steps"]["ar"])
                self.assertEqual(expected["en"], BUILDER.STEP_OVERRIDES[source_id]["en"])
                self.assertEqual(expected["ar"], BUILDER.STEP_OVERRIDES[source_id]["ar"])

    def test_squat_variants_are_not_using_the_same_generic_cues(self):
        self.assertNotEqual(self.by_id["goblet-squat"]["steps"]["ar"], self.by_id["bodyweight-squat"]["steps"]["ar"])
        self.assertIn("الحمل قريبًا من الصدر", self.by_id["goblet-squat"]["steps"]["ar"][1])
        self.assertIn("دون ارتداد", self.by_id["bodyweight-squat"]["steps"]["ar"][3])

    def test_one_arm_swing_is_distinct_from_a_single_leg_deadlift(self):
        swing = self.by_id["one-arm-kettlebell-swings"]["steps"]["ar"]
        deadlift = self.by_id["kettlebell-one-legged-deadlift"]["steps"]["ar"]
        self.assertNotEqual(swing, deadlift)
        self.assertIn("بين الفخذين", swing[1])
        self.assertIn("مستوى الصدر", swing[2])
        self.assertIn("مرجحة", swing[2])

    def test_overhead_throw_describes_throw_and_safe_rebound_not_an_overhead_press(self):
        throw = self.by_id["catch-and-overhead-throw"]["steps"]["ar"]
        self.assertIn("رميها إلى الأمام", throw[1])
        self.assertIn("ارتداد الكرة", throw[2])
        self.assertIn("safe catch", self.by_id["catch-and-overhead-throw"]["steps"]["en"][2])

if __name__ == "__main__":
    unittest.main()
