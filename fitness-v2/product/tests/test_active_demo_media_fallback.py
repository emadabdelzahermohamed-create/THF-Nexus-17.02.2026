import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
EXERCISES_PATH = PULSE / "data" / "exercises.js"
MOTION_PATH = PULSE / "data" / "motion-manifest.json"


def load_exercises():
    source = EXERCISES_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("exercise runtime data must keep its known assignment wrapper")
    return json.loads(source[len(prefix):].strip().rstrip(";"))


class ActiveDemoMediaFallbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.exercises = {item["id"]: item for item in load_exercises()}
        cls.motion = json.loads(MOTION_PATH.read_text(encoding="utf-8"))

    def test_error_handler_is_scoped_to_current_exercise_and_exact_asset(self):
        start = self.app.index("function armActiveDemoMediaError(item, expectedSource)")
        end = self.app.index("function fallbackActiveDemoToReference(item, expectedSource)", start)
        handler = self.app[start:end]
        self.assertIn("activeDemoExerciseId !== exerciseId", handler)
        self.assertIn("video.getAttribute('src') !== expectedSource", handler)
        self.assertIn("video.addEventListener('error', handler, { once: true })", handler)

    def test_failed_video_falls_back_to_local_reference_frames(self):
        start = self.app.index("function fallbackActiveDemoToReference(item, expectedSource)")
        end = self.app.index("function renderActiveMotion(item)", start)
        fallback = self.app[start:end]
        for expected in (
            "video.classList.add('hidden')",
            "video.removeAttribute('src')",
            "referenceMotionPlayer(item, 'detail')",
            "reference.classList.remove('hidden')",
            "$('activeDemoCredit')?.classList.add('hidden')",
            "if (playOnce) playOnce.disabled = true",
            "syncActiveReferenceMotionLabel(item)",
        ):
            self.assertIn(expected, fallback)

    def test_fallback_persists_for_same_exercise_and_resets_on_switch(self):
        start = self.app.index("function renderActiveMotion(item)")
        end = self.app.index("function syncActiveReferenceMotionLabel", start)
        render = self.app[start:end]
        self.assertIn("video.dataset.referenceFallbackExerciseId === item.id", render)
        self.assertIn("delete video.dataset.referenceFallbackExerciseId", render)
        self.assertIn("armActiveDemoMediaError(item, nextSource)", render)

    def test_manifest_backed_exercises_have_safe_local_fallback_frames(self):
        for exercise_id in self.motion:
            item = self.exercises.get(exercise_id)
            self.assertIsNotNone(item, f"manifest ID missing from catalog: {exercise_id}")
            assets = item.get("demo", {}).get("assets", [])[:2]
            self.assertEqual(2, len(assets), f"{exercise_id} needs two fallback frames")
            for asset in assets:
                self.assertRegex(asset, r"^media/free-exercise-db/[A-Za-z0-9_/-]+\.jpg$")

    def test_fallback_uses_existing_reduced_motion_label_policy(self):
        start = self.app.index("function syncActiveReferenceMotionLabel")
        end = self.app.index("function renderActiveWorkout()", start)
        label_sync = self.app[start:end]
        self.assertIn("preferredReducedMotion()", label_sync)
        self.assertIn("referenceMotionStatic", label_sync)
        self.assertIn("referenceMotionAuto", label_sync)


if __name__ == "__main__":
    unittest.main()
