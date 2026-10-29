import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
RUNTIME_PATH = PULSE / "data" / "exercises.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

EXPECTED_ID = "box-skip"
EXPECTED_SOURCE_ID = "Box_Skip"
EXPECTED_AR_NAME = "قفز متتابع بين الصناديق"
EXPECTED_AR_ALT = "وضعا البداية والنهاية لتمرين القفز المتتابع بين الصناديق"


class BoxSkipDemoAltParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_PATH.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = RUNTIME_PATH.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.builder = BUILDER_PATH.read_text(encoding="utf-8")
        cls.by_id = {item["id"]: item for item in cls.catalog}

    def test_arabic_demo_alt_matches_reviewed_exercise_name(self):
        item = self.by_id[EXPECTED_ID]
        self.assertEqual(EXPECTED_SOURCE_ID, item["sourceItemId"])
        self.assertEqual(EXPECTED_AR_NAME, item["name"]["ar"])
        self.assertEqual(EXPECTED_AR_ALT, item["demo"]["alt"]["ar"])
        self.assertNotIn("خطوات سريعة على الصندوق", item["demo"]["alt"]["ar"])
        self.assertEqual("two_frame_image_sequence", item["demo"]["type"])
        self.assertTrue(item["demo"]["offline"])
        self.assertEqual([
            "media/free-exercise-db/Box_Skip/0.jpg",
            "media/free-exercise-db/Box_Skip/1.jpg",
        ], item["demo"]["assets"])

    def test_runtime_payload_matches_catalog(self):
        self.assertEqual(self.catalog, self.runtime)

    def test_manifest_matches_exact_catalog_bytes(self):
        self.assertEqual(hashlib.sha256(self.catalog_bytes).hexdigest(), self.manifest["catalogSha256"])

    def test_builder_generates_alt_from_reviewed_arabic_name(self):
        self.assertIn('("Box_Skip", "قفز متتابع بين الصناديق", "football", "agility")', self.builder)
        self.assertIn('f"وضعا البداية والنهاية لتمرين {name_ar}"', self.builder)


if __name__ == "__main__":
    unittest.main()
