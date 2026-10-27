import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
MOTION_MANIFEST = PULSE / "data" / "motion-manifest.json"
VIDEO_LICENSES = PULSE / "data" / "video-licenses.json"


class OfflineVideoLicenseManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.motion = json.loads(MOTION_MANIFEST.read_text(encoding="utf-8"))
        cls.license_doc = json.loads(VIDEO_LICENSES.read_text(encoding="utf-8"))
        cls.licenses = cls.license_doc["videos"]

    def test_offline_video_manifest_and_license_registry_match_one_to_one(self):
        video_entries = {
            exercise_id: entry
            for exercise_id, entry in self.motion.items()
            if entry.get("kind") == "offline_video"
        }
        license_by_id = {entry["exerciseId"]: entry for entry in self.licenses}

        self.assertEqual(len(self.licenses), len(license_by_id), "duplicate exercise IDs in video license registry")
        self.assertEqual(set(video_entries), set(license_by_id), "video entries and license registry must match exactly")

        required_metadata = ("asset", "sha256", "source", "sourceUrl", "author", "license", "licenseUrl")
        for exercise_id, video in video_entries.items():
            with self.subTest(exercise_id=exercise_id):
                license_entry = license_by_id[exercise_id]
                for field in required_metadata:
                    self.assertEqual(video.get(field), license_entry.get(field), f"{exercise_id}: {field} mismatch")
                self.assertRegex(video["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(video["author"].strip())
                self.assertTrue(video["sourceUrl"].startswith("https://"))
                self.assertTrue(video["licenseUrl"].startswith("https://"))

    def test_every_licensed_offline_video_asset_exists_and_matches_its_sha256(self):
        for entry in self.licenses:
            with self.subTest(exercise_id=entry["exerciseId"]):
                asset = PULSE / entry["asset"]
                self.assertTrue(asset.is_file(), f"missing offline video asset: {entry['asset']}")
                actual = hashlib.sha256(asset.read_bytes()).hexdigest()
                self.assertEqual(entry["sha256"], actual, f"asset hash mismatch: {entry['asset']}")

    def test_reference_frame_sequences_are_not_misrepresented_as_licensed_videos(self):
        frame_sequences = {
            exercise_id
            for exercise_id, entry in self.motion.items()
            if entry.get("kind") == "verified_frame_sequence"
        }
        licensed_video_ids = {entry["exerciseId"] for entry in self.licenses}
        self.assertTrue(frame_sequences.isdisjoint(licensed_video_ids))


if __name__ == "__main__":
    unittest.main()
