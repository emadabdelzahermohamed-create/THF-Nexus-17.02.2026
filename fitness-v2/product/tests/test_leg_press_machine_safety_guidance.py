import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_JSON = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.json"
CATALOG_JS = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2/product/tools/build_catalog.py"

EXPECTED = {
    "regression": {
        "en": "Reduce the load and range; keep the pelvis and lower back supported against the pad. Ask gym staff to adjust the seat or safety lock if the setup is unclear.",
        "ar": "خفّض الحمل ومدى الحركة، وأبقِ الحوض وأسفل الظهر مسنودين إلى الوسادة. اطلب من موظف الجيم ضبط المقعد أو قفل الأمان إذا لم يكن الإعداد واضحًا.",
    },
    "progression": {
        "en": "Increase load in small steps only after every rep stays controlled with the pelvis supported; change load or range one at a time.",
        "ar": "زد الحمل بخطوات صغيرة فقط بعد ثبات التحكم وإسناد الحوض في كل عدة؛ غيّر الحمل أو مدى الحركة واحدًا في كل مرة.",
    },
    "safety": {
        "en": "Check and set the machine’s safety lock before loading; keep the pelvis and lower back supported, avoid locking the knees, and stop if the pelvis lifts or knee/back pain occurs.",
        "ar": "تحقق من قفل الأمان واضبطه قبل تحميل الجهاز؛ أبقِ الحوض وأسفل الظهر مسنودين، وتجنب قفل الركبتين، وتوقف إذا ارتفع الحوض أو ظهر ألم في الركبة أو الظهر.",
    },
}


def load_builder():
    spec = importlib.util.spec_from_file_location("build_catalog", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LegPressMachineGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_JSON.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        cls.runtime = json.loads(CATALOG_JS.read_text(encoding="utf-8").split("=", 1)[1].strip().removesuffix(";"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.builder = load_builder()
        cls.target = next(item for item in cls.catalog if item["sourceItemId"] == "Leg_Press")

    def test_machine_specific_bilingual_guidance_matches_builder(self):
        self.assertEqual(self.builder.guidance_for("Leg_Press", "squat"), {
            "regression_en": EXPECTED["regression"]["en"],
            "regression_ar": EXPECTED["regression"]["ar"],
            "progression_en": EXPECTED["progression"]["en"],
            "progression_ar": EXPECTED["progression"]["ar"],
            "safety_en": EXPECTED["safety"]["en"],
            "safety_ar": EXPECTED["safety"]["ar"],
        })
        for field, expected in EXPECTED.items():
            self.assertEqual(self.target[field], expected)

    def test_runtime_payload_and_manifest_match_exact_catalog_bytes(self):
        self.assertEqual(self.runtime, self.catalog)
        self.assertEqual(self.manifest["catalogSha256"], hashlib.sha256(self.catalog_bytes).hexdigest())

    def test_machine_setup_and_offline_demo_mapping_are_preserved(self):
        self.assertEqual(self.target["id"], "leg-press")
        self.assertEqual(self.target["demo"]["assets"], [
            "media/free-exercise-db/Leg_Press/0.jpg",
            "media/free-exercise-db/Leg_Press/1.jpg",
        ])
        self.assertEqual(len(self.target["steps"]["en"]), 5)
        self.assertEqual(len(self.target["steps"]["ar"]), 5)
        self.assertTrue(self.target["tracking"]["load"])
        self.assertTrue(self.target["tracking"]["volume"])


if __name__ == "__main__":
    unittest.main()
