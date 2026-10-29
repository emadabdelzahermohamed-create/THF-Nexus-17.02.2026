from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "android/app/src/main/assets/pulse/app.js"


class RestTimerUndoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")

    def function_slice(self, start, end):
        first = self.app.index(start)
        last = self.app.index(end, first + len(start))
        return self.app[first:last]

    def test_rest_timer_records_the_set_that_started_it(self):
        self.assertIn(
            "startRest(set.restSeconds || activeExercise().prescription.restSeconds || 60,index)",
            self.app,
        )
        self.assertIn(
            "state.active.restForSetIndex=Number.isInteger(setIndex)?setIndex:null;",
            self.app,
        )

    def test_undoing_the_owning_set_cancels_rest(self):
        complete = self.function_slice("function completeSet(index) {", "function startRest(")
        self.assertIn("!set.complete && (state.active.restForSetIndex===index", complete)
        self.assertIn(") stopRest();", complete)

    def test_unrelated_set_does_not_cancel_a_known_owner(self):
        complete = self.function_slice("function completeSet(index) {", "function startRest(")
        self.assertIn("state.active.restForSetIndex===index", complete)
        self.assertIn("!Number.isInteger(state.active.restForSetIndex) && state.active.restEndsAtMs", complete)

    def test_stop_clears_deadline_and_set_owner(self):
        stop = self.function_slice("function stopRest(", "function resumeRest(){")
        self.assertIn("delete state.active.restEndsAtMs", stop)
        self.assertIn("delete state.active.restForSetIndex", stop)

    def test_expired_restore_clears_stale_set_owner(self):
        resume = self.function_slice("function resumeRest(){", "function addSet(){")
        self.assertIn("delete state.active.restForSetIndex", resume)
        self.assertIn("if(expiredWhileAway)announceRestComplete();", resume)


if __name__ == "__main__":
    unittest.main()
