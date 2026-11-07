import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2/android/app/src/main/assets/pulse"
CATALOG_JSON = PULSE / "data/exercises.json"
CATALOG_JS = PULSE / "data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2/product/tools/build_catalog.py"

SPEC = importlib.util.spec_from_file_location("build_catalog", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class CatalogMuscleGroupDedupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_bytes = CATALOG_JSON.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes)
        runtime_text = CATALOG_JS.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_text.split("=", 1)[1].strip().removesuffix(";"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_builder_removes_duplicates_and_primary_secondary_overlap_in_order(self):
        self.assertEqual(
            BUILDER.normalize_muscle_groups(
                ["quadriceps", "quadriceps", "glutes"],
                ["calves", "quadriceps", "glutes", "hamstrings", "calves"],
            ),
            (["quadriceps", "glutes"], ["calves", "hamstrings"]),
        )

    def test_all_catalog_muscle_groups_are_unique_and_disjoint_in_both_languages(self):
        for item in self.catalog:
            for language in ("en", "ar"):
                primary = item["muscles"]["primary"][language]
                secondary = item["muscles"]["secondary"][language]
                combined = primary + secondary
                self.assertEqual(len(primary), len(set(primary)), item["id"])
                self.assertEqual(len(secondary), len(set(secondary)), item["id"])
                self.assertEqual(len(combined), len(set(combined)), item["id"])
            self.assertEqual(len(item["muscles"]["primary"]["en"]), len(item["muscles"]["primary"]["ar"]), item["id"])
            self.assertEqual(len(item["muscles"]["secondary"]["en"]), len(item["muscles"]["secondary"]["ar"]), item["id"])

    def test_barbell_step_ups_does_not_repeat_quadriceps_as_secondary(self):
        item = next(value for value in self.catalog if value["sourceItemId"] == "Barbell_Step_Ups")
        self.assertEqual(item["muscles"]["primary"]["en"], ["quadriceps"])
        self.assertEqual(item["muscles"]["primary"]["ar"], ["أمامية الفخذ"])
        self.assertNotIn("quadriceps", item["muscles"]["secondary"]["en"])
        self.assertNotIn("أمامية الفخذ", item["muscles"]["secondary"]["ar"])

    def test_runtime_and_manifest_match_exact_generated_catalog_bytes(self):
        self.assertEqual(self.runtime, self.catalog)
        self.assertEqual(self.manifest["catalogSha256"], hashlib.sha256(self.catalog_bytes).hexdigest())


if __name__ == "__main__":
    unittest.main()
