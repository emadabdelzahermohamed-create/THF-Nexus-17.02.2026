from pathlib import Path
import hashlib
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
PULSE = ROOT / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
MOTION_PATH = PULSE / "data" / "motion-manifest.json"
LICENSE_PATH = PULSE / "data" / "video-licenses.json"
MEDIA_ROOT = PULSE / "media"


class OfflineMotionMappingIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.motion = json.loads(MOTION_PATH.read_text(encoding="utf-8"))
        cls.license_ledger = json.loads(LICENSE_PATH.read_text(encoding="utf-8"))
        cls.catalog_by_id = {item["id"]: item for item in cls.catalog}
        cls.licenses_by_exercise = {
            item["exerciseId"]: item for item in cls.license_ledger["videos"]
        }

    def test_every_motion_manifest_key_maps_to_a_real_catalog_exercise(self):
        self.assertEqual(len(self.motion), len(set(self.motion)))
        self.assertTrue(self.motion)
        for exercise_id in self.motion:
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(exercise_id, self.catalog_by_id)

    def test_every_offline_video_has_one_matching_license_and_asset_hash(self):
        videos = {
            exercise_id: entry
            for exercise_id, entry in self.motion.items()
            if entry.get("kind") == "offline_video"
        }
        self.assertEqual(set(videos), set(self.licenses_by_exercise))

        for exercise_id, entry in videos.items():
            with self.subTest(exercise_id=exercise_id):
                license_entry = self.licenses_by_exercise[exercise_id]
                self.assertEqual(entry["asset"], license_entry["asset"])
                self.assertEqual(entry["sha256"], license_entry["sha256"])
                self.assertEqual(entry["licenseId"], f"wger-{exercise_id}")
                self.assertEqual(license_entry["source"], "wger")
                self.assertTrue(license_entry["author"].strip())
                self.assertTrue(
                    license_entry["sourceUrl"].startswith(
                        "https://wger.de/media/exercise-video/"
                    )
                )
                self.assertEqual(license_entry["license"], "CC-BY-SA-4.0")
                self.assertEqual(
                    license_entry["licenseUrl"],
                    "https://creativecommons.org/licenses/by-sa/4.0/",
                )
                asset = MEDIA_ROOT / entry["asset"].removeprefix("media/")
                self.assertTrue(asset.is_file(), exercise_id)
                self.assertLess(asset.stat().st_size, 12 * 1024 * 1024, exercise_id)
                self.assertEqual(
                    entry["sha256"],
                    hashlib.sha256(asset.read_bytes()).hexdigest(),
                )

    def test_verified_frame_sequences_have_explicit_review_and_real_timing(self):
        sequences = {
            exercise_id: entry
            for exercise_id, entry in self.motion.items()
            if entry.get("kind") == "verified_frame_sequence"
        }
        self.assertTrue(sequences)
        for exercise_id, entry in sequences.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertGreaterEqual(entry.get("sourceFrameCount", 0), 2)
                self.assertGreater(entry.get("fps", 0), 0)
                self.assertGreater(entry.get("durationSeconds", 0), 0)
                self.assertTrue(entry.get("review", "").strip())
                self.assertNotIn(exercise_id, self.licenses_by_exercise)


if __name__ == "__main__":
    unittest.main()
