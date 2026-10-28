import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"


class CatalogBilingualMuscleMetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_catalog_count_and_ids_match_manifest_contract(self):
        self.assertEqual(self.manifest["exerciseCount"], len(self.catalog))
        ids = [item.get("id", "").strip() for item in self.catalog]
        self.assertTrue(all(ids), "Every exercise must have a nonblank stable id")
        self.assertEqual(len(ids), len(set(ids)), "Exercise ids must be unique")

    def test_every_exercise_has_bilingual_name_and_primary_muscles(self):
        for item in self.catalog:
            with self.subTest(exercise=item.get("id")):
                for locale in ("en", "ar"):
                    self.assertTrue(item.get("name", {}).get(locale, "").strip())
                    primary = item.get("muscles", {}).get("primary", {}).get(locale, [])
                    self.assertTrue(primary, f"{locale} primary muscles must be present")

    def test_primary_muscle_labels_are_paired_between_locales(self):
        for item in self.catalog:
            with self.subTest(exercise=item.get("id")):
                primary = item.get("muscles", {}).get("primary", {})
                self.assertEqual(
                    len(primary.get("en", [])),
                    len(primary.get("ar", [])),
                    "Primary muscle labels must remain paired across English and Arabic",
                )

    def test_secondary_muscles_are_paired_or_absent_in_both_locales(self):
        for item in self.catalog:
            with self.subTest(exercise=item.get("id")):
                secondary = item.get("muscles", {}).get("secondary", {})
                self.assertEqual(
                    len(secondary.get("en", [])),
                    len(secondary.get("ar", [])),
                    "Secondary muscle labels must remain paired across English and Arabic",
                )

    def test_muscle_labels_are_nonblank_and_not_duplicated_per_locale(self):
        for item in self.catalog:
            with self.subTest(exercise=item.get("id")):
                for group in ("primary", "secondary"):
                    labels = item.get("muscles", {}).get(group, {})
                    for locale in ("en", "ar"):
                        values = labels.get(locale, [])
                        self.assertTrue(
                            all(isinstance(value, str) and value.strip() for value in values),
                            f"{group} {locale} labels must be nonblank strings",
                        )
                        self.assertEqual(
                            len(values),
                            len(set(values)),
                            f"{group} {locale} labels must not repeat within one exercise",
                        )


if __name__ == "__main__":
    unittest.main()
