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

    def test_back_and_health_navigation_only_stop_ui_polling_not_native_session(self):
        self.assertIn("$('activityBackBtn').addEventListener('click',()=>{stopActivityPolling();showScreen('todayScreen');});", self.source)
        self.assertIn("$('activityHealthBtn').addEventListener('click',()=>{stopActivityPolling();showScreen('healthScreen');});", self.source)


if __name__ == "__main__":
    unittest.main()
