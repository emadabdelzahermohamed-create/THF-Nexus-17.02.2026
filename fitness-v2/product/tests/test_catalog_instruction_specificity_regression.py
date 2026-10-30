import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SOURCE_ID = "Medicine_Ball_Full_Twist"
EXPECTED_FINAL_ENGLISH_CUE = (
    "Pass the ball to your partner at chest height. Both partners turn the shoulders and hips "
    "together in the opposite direction to receive the next pass; let the feet pivot naturally, "
    "keep the knees soft, and stop if balance or comfort is lost."
)
GENERIC_ENGLISH_FILLER = (
    re.compile(r"\\brepeat the procedure\\b", re.IGNORECASE),
    re.compile(r"\\bperform the (?:amount|number) of repetitions\\b", re.IGNORECASE),
)


SPEC = importlib.util.spec_from_file_location("thf_build_catalog_instruction_specificity", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class CatalogInstructionSpecificityRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        raw = RUNTIME_PATH.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
            raise AssertionError("Runtime catalog wrapper is invalid")
        cls.runtime = json.loads(raw[len(prefix):raw.rfind(";")])
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in cls.catalog}

    def test_medicine_ball_full_twist_final_cue_is_movement_specific_and_bilingual(self):
        item = self.by_source_id[SOURCE_ID]
        self.assertEqual(EXPECTED_FINAL_ENGLISH_CUE, item["steps"]["en"][-1])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[SOURCE_ID])
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("توقف", item["steps"]["ar"][-1])

    def test_generic_repetition_filler_is_absent_from_english_catalog_steps(self):
        offenders = [
            (item["sourceItemId"], index, step)
            for item in self.catalog
            for index, step in enumerate(item["steps"]["en"], start=1)
            if any(pattern.search(step) for pattern in GENERIC_ENGLISH_FILLER)
        ]
        self.assertEqual([], offenders)

    def test_runtime_javascript_payload_matches_generated_json(self):
        self.assertEqual(self.catalog, self.runtime)

    def test_catalog_manifest_digest_matches_exact_json_bytes(self):
        digest = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, self.manifest["catalogSha256"])


if __name__ == "__main__":
    unittest.main()
