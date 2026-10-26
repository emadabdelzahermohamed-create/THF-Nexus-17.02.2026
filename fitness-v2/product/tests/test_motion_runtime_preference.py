from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
MOTION_RUNTIME = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "assets"
    / "pulse"
    / "data"
    / "motion-manifest.js"
)


class MotionRuntimePreferenceTest(unittest.TestCase):
    def test_explicit_app_preference_overrides_system_reduced_motion(self):
        script = MOTION_RUNTIME.read_text()

        self.assertIn(
            "if (control) return Boolean(control.checked);",
            script,
        )
        self.assertIn(
            "return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);",
            script,
        )
        self.assertNotIn(
            "return Boolean(control?.checked) || Boolean(window.matchMedia",
            script,
        )

    def test_reference_sequence_names_each_visible_phase_bilingually(self):
        script = MOTION_RUNTIME.read_text()

        self.assertIn("const phaseIndex = frameIndex % item.demo.assets.length;", script)
        self.assertIn("phaseIndex === 0 ? 'البداية' : 'النهاية'", script)
        self.assertIn("phaseIndex === 0 ? 'Start' : 'Finish'", script)
        self.assertIn("const reduced = reduceMotion();", script)
        self.assertIn("reduced ? 'صورة ثابتة — تقليل الحركة'", script)
        self.assertIn("reduced ? 'Static image — reduced motion'", script)

    def test_reference_frames_are_preloaded_once_before_automatic_cycling(self):
        script = MOTION_RUNTIME.read_text()

        self.assertIn("const preloadedExercises = new Set();", script)
        self.assertIn("function preloadFrames(item)", script)
        self.assertIn("if (preloadedExercises.has(item.id)) return;", script)
        self.assertIn("item.demo.assets.forEach(asset =>", script)
        self.assertIn("const preload = new Image();", script)
        self.assertIn("preload.src = './' + asset;", script)
        self.assertLess(script.index("preloadFrames(item);"), script.index("timer = window.setInterval"))


if __name__ == "__main__":
    unittest.main()
