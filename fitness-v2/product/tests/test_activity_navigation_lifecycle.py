from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "app.js"


class ActivityNavigationLifecycleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_reentering_activity_resumes_live_session_before_native_start(self):
        self.assertIn("const live=readActivitySnapshot();", self.source)
        self.assertIn("if(live?.active){state.activitySnapshot=live;renderActivity(live);startActivityPolling();return;}", self.source)
        guard = self.source.index("if(live?.active){state.activitySnapshot=live;renderActivity(live);startActivityPolling();return;}")
        native_start = self.source.index("N.beginActivitySession(mode,profileWeightKg())", guard)
        self.assertLess(guard, native_start)

    def test_back_and_health_navigation_preserve_native_session(self):
        self.assertIn(
            "$('activityBackBtn').addEventListener('click',()=>{pauseIfLeavingActivity();stopActivityPolling();showScreen('todayScreen');});",
            self.source,
        )
        self.assertIn(
            "$('activityHealthBtn').addEventListener('click',()=>{pauseIfLeavingActivity();stopActivityPolling();showScreen('healthScreen');});",
            self.source,
        )
        pause_start = self.source.index("const pauseIfLeavingActivity=()=>")
        pause_end = self.source.index(";$('activityStopBtn')", pause_start)
        pause_guard = self.source[pause_start:pause_end]
        self.assertIn("$('activityAutoPauseLeave').checked", pause_guard)
        self.assertIn("N.pauseActivitySession()", pause_guard)
        self.assertNotIn("N.endActivitySession", pause_guard)
        handlers_start = self.source.index("$('activityBackBtn').addEventListener('click'")
        handlers_end = self.source.index("window.addEventListener('thf:activity-started'", handlers_start)
        handlers = self.source[handlers_start:handlers_end]
        self.assertNotIn("N.endActivitySession", handlers)
        self.assertNotIn("persistFinishedActivity", handlers)


if __name__ == "__main__":
    unittest.main()
