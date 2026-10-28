import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"
EXERCISES_PATH = PULSE / "data" / "exercises.js"
MOTION_PATH = PULSE / "data" / "motion-manifest.json"


def load_exercises():
    source = EXERCISES_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("exercise runtime data must keep its known assignment wrapper")
    return json.loads(source[len(prefix):].strip().rstrip(";"))


class MotionAccessibleLabelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.exercises = {item["id"]: item for item in load_exercises()}
        cls.motion = json.loads(MOTION_PATH.read_text(encoding="utf-8"))

    def test_motion_labels_are_localized_by_actual_media_kind(self):
        self.assertIn("function motionAccessibleLabel(item, entry = motionAsset(item))", self.app)
        for phrase in (
            "فيديو تمرين ${name} يعمل دون اتصال",
            "مقطع حركة موثّق لتمرين ${name}",
            "Offline exercise video: ${name}",
            "Verified motion clip: ${name}",
        ):
            self.assertIn(phrase, self.app)

    def test_card_detail_and_active_workout_use_motion_aware_labels(self):
        player_start = self.app.index("function motionPlayer(item, context = 'detail')")
        credit_start = self.app.index("function motionCredit(item)", player_start)
        player = self.app[player_start:credit_start]
        active_start = self.app.index("function renderActiveMotion(item)")
        workout_start = self.app.index("function renderActiveWorkout()", active_start)
        active = self.app[active_start:workout_start]

        self.assertIn("motionAccessibleLabel(item, entry)", player)
        self.assertIn("motionAccessibleLabel(item, motion)", active)
        self.assertNotIn("local(item.demo?.alt) || local(item.name)", player)
        self.assertNotIn("item.demo.alt[state.lang]", active)

    def test_all_manifest_entries_map_to_existing_exercises_and_avoid_stale_alt_for_video(self):
        self.assertEqual(7, len(self.motion))
        kinds = {}
        for exercise_id, entry in self.motion.items():
            kinds[entry["kind"]] = kinds.get(entry["kind"], 0) + 1
            item = self.exercises.get(exercise_id)
            self.assertIsNotNone(item, f"manifest exercise missing from catalog: {exercise_id}")
            self.assertIn("name", item)
            self.assertIn("en", item["name"])
            self.assertIn("ar", item["name"])
            if entry["kind"] == "offline_video":
                self.assertTrue(entry["asset"].endswith((".mp4", ".webm")))
                self.assertIn("licenseUrl", entry)
                self.assertIn("Start and finish positions", item["demo"]["alt"]["en"])
            elif entry["kind"] == "verified_frame_sequence":
                self.assertTrue(entry["asset"].endswith(".webm"))
                self.assertIn("Start and finish positions", item["demo"]["alt"]["en"])
            else:
                self.fail(f"unexpected motion kind: {entry['kind']}")
        self.assertEqual({"offline_video": 5, "verified_frame_sequence": 2}, kinds)


    def test_offline_banner_reports_actual_motion_demo_coverage(self):
        self.assertIn("offlineBanner:`مكتبة التمارين تعمل دون اتصال؛ العروض الحركية متاحة دون اتصال لـ${Object.keys(motionManifest).length} تمارين محددة.`", self.app)
        self.assertIn("offlineBanner:`The exercise library works offline; motion demos are available offline for ${Object.keys(motionManifest).length} selected exercises.`", self.app)
        self.assertEqual(2, self.app.count("${Object.keys(motionManifest).length}"))
        self.assertNotIn("The exercise library and visual demos work fully offline.", self.app)
        self.assertIn('data-i18n="offlineBanner">مكتبة التمارين تعمل دون اتصال، والعروض الحركية متاحة لتمارين محددة.</span>', self.html)
        self.assertEqual(7, len(self.motion))


if __name__ == "__main__":
    unittest.main()
