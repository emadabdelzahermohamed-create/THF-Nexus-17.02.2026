from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "android/app/src/main/assets/pulse/app.js"
HTML = ROOT / "android/app/src/main/assets/pulse/index.html"


class RestTimerAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")
        cls.html = HTML.read_text(encoding="utf-8")

    def function_slice(self, start, end):
        first = self.app.index(start)
        last = self.app.index(end, first + len(start))
        return self.app[first:last]

    def test_completion_copy_is_bilingual(self):
        self.assertIn("restComplete:'انتهت فترة الراحة. يمكنك متابعة التمرين.'", self.app)
        self.assertIn("restComplete:'Rest is over. You can continue your workout.'", self.app)

    def test_completion_uses_a_dedicated_polite_live_region(self):
        self.assertIn(
            'id="restAnnouncement" class="sr-only" role="status" aria-live="polite" aria-atomic="true"',
            self.html,
        )
        self.assertGreater(self.html.index('id="restAnnouncement"'), self.html.index('id="toast"'))
        self.assertLess(self.html.index("</main>"), self.html.index('id="restAnnouncement"'))
        self.assertIn("const node=$('restAnnouncement');", self.app)
        self.assertIn("node.textContent=t('restComplete');", self.app)

    def test_natural_countdown_completion_announces_once(self):
        render = self.function_slice("function renderRest(){", "function announceRestComplete(){")
        self.assertIn("if(seconds<=0)stopRest({announce:true});", render)
        stop = self.function_slice("function stopRest(", "function resumeRest(){")
        self.assertIn("if(announce)announceRestComplete();", stop)

    def test_skip_does_not_claim_rest_finished_naturally(self):
        self.assertIn("$('skipRest').addEventListener('click',()=>stopRest());", self.app)

    def test_expired_deadline_after_restore_announces_completion(self):
        resume = self.function_slice("function resumeRest(){", "function addSet(){")
        self.assertIn("expiredWhileAway", resume)
        self.assertIn("if(expiredWhileAway)announceRestComplete();", resume)
        self.assertIn("restTimer.remaining(deadlineMs)<=0", resume)

    def test_existing_timer_stays_deadline_based(self):
        timer = (ROOT / "android/app/src/main/assets/pulse/rest-timer.js").read_text(encoding="utf-8")
        self.assertIn("return now() +", timer)
        self.assertIn("Math.ceil((deadlineMs - now()) / 1000)", timer)


if __name__ == "__main__":
    unittest.main()
