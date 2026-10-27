import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP = PULSE / "app.js"
CSS = PULSE / "styles.css"
MOTION = PULSE / "data" / "motion-manifest.json"
LICENSES = PULSE / "data" / "video-licenses.json"
EXERCISES = PULSE / "data" / "exercises.js"


def load_js_array(path):
    source = path.read_text(encoding="utf-8")
    payload = source.split("=", 1)[1].strip().removesuffix(";")
    return json.loads(payload)


class ExerciseVideoRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.motion = json.loads(MOTION.read_text(encoding="utf-8"))
        cls.licenses = json.loads(LICENSES.read_text(encoding="utf-8"))["videos"]
        cls.exercises = {item["id"]: item for item in load_js_array(EXERCISES)}

    def test_motion_manifest_entries_map_to_catalog_and_local_assets(self):
        self.assertEqual(7, len(self.motion))
        self.assertTrue(set(self.motion).issubset(self.exercises))
        for exercise_id, entry in self.motion.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(entry["kind"], {"offline_video", "verified_frame_sequence"})
                self.assertRegex(entry["asset"], r"^media/motion/[a-z0-9-]+\.(mp4|webm)$")
                asset = PULSE / entry["asset"]
                self.assertTrue(asset.is_file())
                self.assertEqual(entry["sha256"], hashlib.sha256(asset.read_bytes()).hexdigest())

    def test_video_license_registry_matches_every_offline_video(self):
        videos = {key: value for key, value in self.motion.items() if value["kind"] == "offline_video"}
        licenses = {entry["exerciseId"]: entry for entry in self.licenses}
        self.assertEqual(len(self.licenses), len(licenses))
        self.assertEqual(set(videos), set(licenses))
        for exercise_id, video in videos.items():
            with self.subTest(exercise_id=exercise_id):
                license_entry = licenses[exercise_id]
                for field in ("asset", "sha256", "source", "sourceUrl", "author", "license", "licenseUrl"):
                    self.assertEqual(video.get(field), license_entry.get(field))
                self.assertTrue(license_entry["author"].strip())
                self.assertTrue(license_entry["sourceUrl"].startswith("https://"))
                self.assertTrue(license_entry["licenseUrl"].startswith("https://"))

    def test_cards_and_details_use_manifest_media_with_reference_fallback(self):
        for marker in (
            "function motionAsset(item)",
            "motionPlayer(item, 'card')",
            "motionPlayer(item, 'detail')",
            "function referenceMotionPlayer(item",
            "function motionCoverageLabel(item",
            "video.addEventListener('error'",
            "motionCoverageLabel(item, true)",
            "function motionCredit(item)",
            'data-clip-limit="6"',
            "const preload = context === 'card' ? 'none' : 'metadata';",
        ):
            self.assertIn(marker, self.app)
        self.assertNotIn("item.demo.assets.map((asset,index)", self.app)

    def test_video_playback_is_viewport_and_lifecycle_gated(self):
        for marker in (
            "function shouldPlayExerciseDemoVideo(video)",
            "new window.IntersectionObserver(",
            "entry.intersectionRatio >= 0.25",
            "video.dataset.inViewport",
            "video.removeAttribute('autoplay')",
            "video.closest('.hidden')",
            "document.hidden",
            "unobserveExerciseDemoVideos($('exerciseGrid'))",
            "unobserveExerciseDemoVideos($('detailDemo'))",
            "syncExerciseDemoVideos();",
            "window.addEventListener('scroll', refresh, {passive:true})",
            "video.pause()",
        ):
            self.assertIn(marker, self.app)
        self.assertNotIn("const autoplay = reduced ? '' : 'autoplay';", self.app)

    def test_bilingual_credits_and_reduced_motion_fallback_are_preserved(self):
        for marker in (
            "Video source:",
            "مصدر الفيديو:",
            "CC BY-SA 4.0 license",
            "ترخيص CC BY-SA 4.0",
            "thf-reference-start",
            "prefers-reduced-motion:reduce",
            "motion-reduced",
        ):
            self.assertIn(marker, self.app + self.css)
        self.assertIn("motion-reduced", self.app + self.css)


if __name__ == "__main__":
    unittest.main()
