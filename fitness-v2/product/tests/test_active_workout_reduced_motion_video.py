"""Regression contracts for reduced motion in the active workout demo.

Full-motion exercise clips must not override the user's reduced-motion setting.
The active workout should use its local static reference frame while reduced
motion is enabled, and restore the reviewed clip only when the setting is off.
"""
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
APP_JS = REPO_ROOT / "fitness-v2/android/app/src/main/assets/pulse/app.js"
MOTION_JS = REPO_ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/motion-manifest.js"


class ActiveWorkoutReducedMotionVideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_JS.read_text(encoding="utf-8")
        cls.motion = MOTION_JS.read_text(encoding="utf-8")

    def test_active_full_motion_clip_is_gated_by_reduced_motion(self):
        self.assertIn("const reducedMotion = document.documentElement.classList.contains('motion-reduced')", self.app)
        self.assertIn("&& !reducedMotion) {", self.app)

    def test_preference_change_rerenders_the_active_exercise(self):
        self.assertIn("if(activeWorkout?.classList.contains('active') && activeItem) renderActiveMotion(activeItem);", self.app)

    def test_navigation_does_not_restart_active_video_when_reduced(self):
        self.assertIn("&& !document.documentElement.classList.contains('motion-reduced')) demoVideo.play()", self.app)

    def test_visibility_resume_reconciles_preference_instead_of_forcing_video_play(self):
        self.assertIn("if(item) renderActiveMotion(item);", self.app)
        self.assertNotIn("if($('activeWorkoutScreen').classList.contains('active')&&!video.classList.contains('hidden'))video.play()", self.app)

    def test_reference_motion_controller_holds_a_static_frame_when_reduced(self):
        self.assertIn("if (reduceMotion() || document.hidden)", self.motion)
        self.assertIn("if (timer || pendingExerciseId) stop();", self.motion)
        self.assertIn("renderFrame(item);", self.motion)


if __name__ == "__main__":
    unittest.main()
