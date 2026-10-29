from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
PULSE = ROOT / "android/app/src/main/assets/pulse"
APP = PULSE / "app.js"
INDEX = PULSE / "index.html"
MANAGER = PULSE / "dialog-accessibility.js"
NODE_TEST = Path(__file__).with_name("dialog_focus_accessibility.test.cjs")


class DialogFocusAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")
        cls.index = INDEX.read_text(encoding="utf-8")
        cls.manager = MANAGER.read_text(encoding="utf-8")

    def test_manager_is_loaded_before_app(self):
        manager_tag = '<script src="./dialog-accessibility.js"></script>'
        app_tag = '<script src="./app.js"></script>'
        self.assertIn(manager_tag, self.index)
        self.assertLess(self.index.index(manager_tag), self.index.index(app_tag))

    def test_both_detail_dialogs_use_shared_focus_manager(self):
        self.assertIn("dialogFocus.open('exerciseDetail','detailCloseButton', returnTarget)", self.app)
        self.assertIn("dialogFocus.close('exerciseDetail', restoreFocus)", self.app)
        self.assertIn("dialogFocus.open('programDetail','programDetailCloseButton', returnTarget)", self.app)
        self.assertIn("dialogFocus.close('programDetail', restoreFocus)", self.app)

    def test_starting_workout_does_not_restore_focus_to_hidden_library(self):
        start_exercise = self.app[self.app.index("function startExercise("):self.app.index("function startProgramSession(")]
        start_program = self.app[self.app.index("function startProgramSession("):self.app.index("function activeExercise(")]
        self.assertIn("closeDetail(false)", start_exercise)
        self.assertIn("closeProgramDetail(false);closeDetail(false)", start_program)

    def test_global_keydown_routes_tab_to_active_dialog(self):
        self.assertIn("dialogFocus.handleKeydown(event,dialogId)", self.app)
        self.assertIn("openDetail(card.dataset.id, card)", self.app)
        self.assertIn("openProgramDetail(card.dataset.program, card)", self.app)
        self.assertIn("event.key!=='Escape'", self.app)

    def test_manager_has_tab_trap_and_scroll_restore(self):
        self.assertIn("event.shiftKey", self.manager)
        self.assertIn("event.preventDefault()", self.manager)
        self.assertIn("document.body.style.overflow = previousOverflow", self.manager)
        self.assertIn("target.focus()", self.manager)
        self.assertIn("target.getClientRects().length === 0", self.manager)

    def test_runtime_scenarios(self):
        result = subprocess.run(
            ["node", str(NODE_TEST)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("PASS: 5 dialog focus/lifecycle scenarios", result.stdout)


if __name__ == "__main__":
    unittest.main()