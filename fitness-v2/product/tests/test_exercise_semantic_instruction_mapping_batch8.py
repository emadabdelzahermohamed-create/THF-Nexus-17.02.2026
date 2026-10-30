import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE_DATA = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data"
CATALOG_PATH = PULSE_DATA / "exercises.json"
RUNTIME_PATH = PULSE_DATA / "exercises.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_semantic_mapping", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED_ARABIC = {
    "step-up-with-knee-raise": [
        "قف أمام صندوق أو مقعد ثابت بارتفاع مناسب، والقدمان على الأرض مع شد الجذع.",
        "ضع القدم اليسرى كاملة على الصندوق وادفع عبرها حتى تقف فوقه؛ أثناء الصعود ارفع الركبة اليمنى أمامك مع ثبات الجذع.",
        "انزل بالقدم اليمنى ثم اليسرى بتحكم، وكرر على الجهة الأخرى مع إبقاء الركبة بمحاذاة أصابع القدم.",
    ],
    "medicine-ball-scoop-throw": [
        "ابدأ من نصف قرفصاء والكرة الطبية بين يديك قرب القدمين، بعد التأكد من خلو المساحة خلفك.",
        "ادفع الأرض ومد الوركين والركبتين والكاحلين بسرعة مضبوطة للنهوض، مع إبقاء الجذع متماسكًا.",
        "أرجح الذراعين فوق الرأس وأطلق الكرة خلفك عند قمة الحركة، دون تقويس أسفل الظهر؛ لا تنفذ الرمية إلا في مساحة خالية.",
    ],
}


def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_runtime():
    raw = RUNTIME_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
        raise AssertionError("Runtime exercise payload wrapper is invalid")
    return json.loads(raw[len(prefix):raw.rfind(";")].strip())


class ExerciseSemanticInstructionMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
        cls.catalog = json.loads(cls.catalog_text)
        cls.runtime = load_runtime()
        cls.by_id = {item["id"]: item for item in cls.catalog}
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_catalog_runtime_and_manifest_hash_stay_synchronized(self):
        self.assertEqual(self.catalog, self.runtime)
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len(self.by_id))
        self.assertEqual(
            hashlib.sha256(self.catalog_text.encode("utf-8")).hexdigest(),
            self.manifest["catalogSha256"],
        )

    def test_step_up_cues_describe_box_step_and_opposite_knee_raise(self):
        item = self.by_id["step-up-with-knee-raise"]
        self.assertEqual(EXPECTED_ARABIC[item["id"]], item["steps"]["ar"])
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("الصندوق", item["steps"]["ar"][1])
        self.assertIn("ارفع الركبة اليمنى", item["steps"]["ar"][1])
        self.assertNotEqual(item["steps"]["ar"], self.by_id["goblet-squat"]["steps"]["ar"])
        self.assertNotEqual(item["steps"]["ar"], self.by_id["bodyweight-squat"]["steps"]["ar"])

    def test_scoop_throw_cues_describe_ballistic_throw_not_a_hinge_return(self):
        item = self.by_id["medicine-ball-scoop-throw"]
        self.assertEqual(EXPECTED_ARABIC[item["id"]], item["steps"]["ar"])
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("أطلق الكرة خلفك", item["steps"]["ar"][2])
        self.assertIn("مساحة خالية", item["steps"]["ar"][2])
        self.assertNotEqual(item["steps"]["ar"], self.by_id["kettlebell-one-legged-deadlift"]["steps"]["ar"])
        self.assertNotEqual(item["steps"]["ar"], self.by_id["one-arm-kettlebell-swings"]["steps"]["ar"])

    def test_reviewed_builder_overrides_match_the_runtime_records(self):
        for item_id, expected_steps in EXPECTED_ARABIC.items():
            with self.subTest(item_id=item_id):
                item = self.by_id[item_id]
                source_id = item["sourceItemId"]
                self.assertIn(source_id, BUILDER.STEP_OVERRIDES)
                self.assertEqual(expected_steps, BUILDER.STEP_OVERRIDES[source_id]["ar"])
                self.assertEqual(item["steps"]["en"], BUILDER.STEP_OVERRIDES[source_id]["en"])

    def test_all_catalog_instruction_sequences_remain_bilingual_and_nonblank(self):
        for item in self.catalog:
            with self.subTest(item_id=item["id"]):
                en, ar = item["steps"]["en"], item["steps"]["ar"]
                self.assertTrue(en and ar)
                self.assertEqual(len(en), len(ar))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in en))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in ar))


if __name__ == "__main__":
    unittest.main()
