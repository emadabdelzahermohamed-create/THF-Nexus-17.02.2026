import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
MODULE = PULSE / "rest-timer.js"
APP = PULSE / "app.js"
INDEX = PULSE / "index.html"
CSS = PULSE / "styles.css"


class RestCompletionFeedbackTest(unittest.TestCase):
    def run_node(self, body: str):
        script = f"""
const {{ createRestTimer }} = require({json.dumps(str(MODULE))});
{body}
"""
        return subprocess.run(
            ["node", "-e", script],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_only_valid_elapsed_deadlines_are_naturally_expired(self):
        result = self.run_node(
            """
let clock = 100_000;
const timer = createRestTimer({now: () => clock});
const endsAt = timer.deadline(5);
clock += 5_000;
console.log(JSON.stringify([
  timer.expired(endsAt),
  timer.expired(endsAt + 1_000),
  timer.expired(0),
  timer.expired('invalid')
]));
"""
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([True, False, False, False], json.loads(result.stdout))

    def test_completion_status_is_bilingual_and_accessible(self):
        app = APP.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")

        self.assertIn("restComplete:'Rest complete — ready for the next set.'", app)
        self.assertIn("restComplete:'انتهت الراحة — أنت جاهز للمجموعة التالية.'", app)
        self.assertIn("function showRestComplete(){ $('restCompleteNotice').classList.remove('hidden'); }", app)
        self.assertIn('id="restCompleteNotice" class="rest-complete-notice hidden" role="status" aria-live="polite" aria-atomic="true" data-i18n="restComplete"', index)
        self.assertIn(".rest-complete-notice{", css)
        self.assertIn(".rest-complete-notice:not(.hidden){display:block}", css)

    def test_natural_expiry_and_expired_resume_show_notice(self):
        app = APP.read_text(encoding="utf-8")

        self.assertIn(
            "if(seconds<=0){if(restTimer.expired(state.active?.restEndsAtMs))showRestComplete();stopRest();}",
            app,
        )
        self.assertIn(
            "if(restTimer.expired(state.active.restEndsAtMs))showRestComplete()",
            app,
        )
        self.assertIn("$('restCompleteNotice').classList.add('hidden')", app)

    def test_manual_skip_does_not_claim_rest_completed(self):
        app = APP.read_text(encoding="utf-8")
        self.assertIn("$('skipRest').addEventListener('click',stopRest)", app)
        self.assertNotIn("$('skipRest').addEventListener('click',showRestComplete)", app)


if __name__ == "__main__":
    unittest.main()
