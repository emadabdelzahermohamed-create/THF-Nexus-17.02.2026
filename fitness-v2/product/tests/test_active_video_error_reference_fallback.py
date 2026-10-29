"""Regression contracts for active-workout video failure fallback.

The fallback must reuse the audited offline reference frames and let the existing
motion-manifest lifecycle controller animate them when motion is allowed.
"""
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
APP_JS = REPO_ROOT / "fitness-v2/android/app/src/main/assets/pulse/app.js"
MOTION_JS = REPO_ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/motion-manifest.js"


class ActiveVideoErrorReferenceFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_JS.read_text(encoding="utf-8")
        cls.motion = MOTION_JS.read_text(encoding="utf-8")

    def test_active_workout_pins_exact_exercise_identity(self):
        self.assertIn("$('activeWorkoutScreen').dataset.exerciseId = item.id;", self.app)

    def test_video_error_and_play_rejection_use_the_same_fallback(self):
        self.assertIn("video.addEventListener('error', activeMotionErrorHandler, {once:true});", self.app)
        self.assertIn("playback.catch(() => fallbackActiveMotion(item, nextSource))", self.app)

    def test_failed_video_is_cached_to_prevent_retry_loop(self):
        self.assertIn("const failedMotionExerciseIds = new Set();", self.app)
        self.assertIn("motion?.asset && !failedMotionExerciseIds.has(item.id)", self.app)
        self.assertIn("failedMotionExerciseIds.add(item.id);", self.app)

    def test_fallback_uses_local_reference_assets_and_clears_video(self):
        self.assertIn("video.removeAttribute('src');", self.app)
        self.assertIn("const referenceAssets = Array.isArray(item.demo?.assets) ? item.demo.assets : [];", self.app)
        self.assertIn("if (referenceAssets.length) image.src = './' + referenceAssets[0];", self.app)
        self.assertIn("image.classList.remove('hidden');", self.app)

    def test_failed_video_does_not_leave_stale_source_or_license_links(self):
        self.assertIn("$('activeDemoCredit')?.classList.add('hidden');", self.app)
        self.assertIn("$('activeDemoSource')?.removeAttribute('href');", self.app)
        self.assertIn("$('activeDemoLicense')?.removeAttribute('href');", self.app)

    def test_reference_motion_still_obeys_reduced_motion_and_visibility(self):
        self.assertIn("byId('reduceMotion')?.addEventListener('change', reconcile);", self.motion)
        self.assertIn("document.addEventListener('visibilitychange', reconcile);", self.motion)
        self.assertIn("if (reduceMotion() || document.hidden)", self.motion)
        self.assertIn("if (!video.classList.contains('hidden'))", self.motion)


if __name__ == "__main__":
    unittest.main()
