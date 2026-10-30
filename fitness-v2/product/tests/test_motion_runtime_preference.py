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
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("if (control) return Boolean(control.checked);", script)
        self.assertIn("return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);", script)
        self.assertNotIn("return Boolean(control?.checked) || Boolean(window.matchMedia", script)

    def test_reference_sequence_names_each_visible_phase_bilingually(self):
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("const assets = loaded ? loaded.map(frame => frame.asset) : item?.demo?.assets;", script)
        self.assertIn("const phaseIndex = frameIndex % assets.length;", script)
        self.assertIn("const sourceIndex = loaded ? loaded[phaseIndex].index : phaseIndex;", script)
        self.assertIn("sourceIndex === 0 ? 'البداية' : 'النهاية'", script)
        self.assertIn("sourceIndex === 0 ? 'Start' : 'Finish'", script)
        self.assertIn("image.alt =", script)

    def test_reference_frames_are_preloaded_once_before_automatic_cycling(self):
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("const preloadPromises = new Map();", script)
        self.assertIn("function preloadFrames(item)", script)
        self.assertIn("if (preloadPromises.has(item.id)) return preloadPromises.get(item.id);", script)
        self.assertIn("item.demo.assets.map(asset =>", script)
        self.assertIn("const preload = new Image();", script)
        self.assertIn("preload.src = './' + asset;", script)
        self.assertIn("const results = await preloadFrames(item);", script)
        self.assertLess(script.index("const results = await preloadFrames(item);"), script.index("timer = window.setInterval"))

    def test_reference_sequence_waits_for_both_frames_and_ignores_stale_start(self):
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("return new Promise(resolve =>", script)
        self.assertIn("const onLoad = () => finish(true);", script)
        self.assertIn("const onError = () => finish(false);", script)
        self.assertIn("preload.addEventListener('load', onLoad, {once: true});", script)
        self.assertIn("preload.addEventListener('error', onError, {once: true});", script)
        self.assertIn("timeoutId = window.setTimeout(() => finish(false), PRELOAD_TIMEOUT_MS);", script)
        self.assertIn("const ready = Promise.all(framePromises);", script)
        self.assertIn("pendingExerciseId = item.id;", script)
        self.assertIn("if (activeExerciseId !== item.id || pendingExerciseId !== item.id", script)
        self.assertIn("if (readyFrames.length < 2)", script)

    def test_reference_image_alt_identifies_the_visible_phase_bilingually(self):
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("const phaseName = isArabic", script)
        self.assertIn("sourceIndex === 0 ? 'البداية' : 'النهاية'", script)
        self.assertIn("image.alt =", script)
        self.assertIn("phase.setAttribute('aria-hidden', 'true');", script)

    def test_one_loaded_frame_is_truthfully_labeled_static(self):
        script = MOTION_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("const loadedCount = Array.isArray(loaded) ? loaded.length : null;", script)
        self.assertIn("loadedCount === 1", script)
        self.assertIn("'إطار مرجعي ثابت'", script)
        self.assertIn("'Static reference frame'", script)
        self.assertIn("phaseStatus", script)


if __name__ == "__main__":
    unittest.main()
