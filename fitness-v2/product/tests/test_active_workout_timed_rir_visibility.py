from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_JS = (PULSE / "app.js").read_text(encoding="utf-8")
INDEX_HTML = (PULSE / "index.html").read_text(encoding="utf-8")
STYLES_CSS = (PULSE / "styles.css").read_text(encoding="utf-8")
POLICY_JS = (PULSE / "set-rir-policy.js").read_text(encoding="utf-8")


class ActiveWorkoutTimedRirVisibilityTest(unittest.TestCase):
    def test_policy_script_loads_before_application(self):
        self.assertLess(INDEX_HTML.index('./set-rir-policy.js'), INDEX_HTML.index('./app.js'))
        self.assertIn("window.THF_SET_RIR_POLICY", POLICY_JS)

    def test_active_workout_hides_rir_for_timed_or_untracked_work(self):
        self.assertIn("window.THF_SET_RIR_POLICY.shouldShow(item, state.active.sets)", APP_JS)
        self.assertIn("rirHeader.hidden = !showRir", APP_JS)
        self.assertIn("const rirField = showRir ?", APP_JS)

    def test_new_freeform_and_program_sets_use_semantic_rir_defaults(self):
        self.assertIn("defaultValue(item,durationSeconds,5)", APP_JS)
        self.assertIn("defaultValue(item,durationSeconds,3)", APP_JS)
        self.assertIn("defaultValue(item,durationSeconds,reference.targetRir)", APP_JS)

    def test_stale_persisted_rir_is_normalized_before_render(self):
        self.assertIn("window.THF_SET_RIR_POLICY.clear(state.active.sets)", APP_JS)
        self.assertIn("persistActive()", APP_JS)

    def test_rir_header_and_desktop_grid_collapse_are_present(self):
        self.assertIn('id="setTableHead"', INDEX_HTML)
        self.assertIn('id="setRirHeader"', INDEX_HTML)
        self.assertIn(".set-table-head.no-rir", STYLES_CSS)
        self.assertIn(".set-rows.no-rir .set-row", STYLES_CSS)


if __name__ == "__main__":
    unittest.main()
