from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP_JS = (ROOT / "android/app/src/main/assets/pulse/app.js").read_text(encoding="utf-8")
INDEX_HTML = (ROOT / "android/app/src/main/assets/pulse/index.html").read_text(encoding="utf-8")


class GpsStatusTruthfulnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.render_activity = APP_JS.split("function renderActivity(snapshot=readActivitySnapshot())", 1)[1].split(
            "function renderActivityHistory()", 1
        )[0]

    def test_ready_fused_or_network_fix_is_not_mislabeled_as_gps(self):
        self.assertIn("displayLocationState=snapshot?.paused?'paused':gpsFixState", self.render_activity)
        self.assertIn("t('locationReady')", self.render_activity)
        self.assertNotIn("GPS · ", self.render_activity)

    def test_paused_session_has_a_distinct_status_and_is_not_shown_as_ready(self):
        self.assertIn("displayLocationState==='paused'?t('locationPaused')", self.render_activity)
        self.assertIn("displayLocationState==='ready'", self.render_activity)

    def test_location_status_and_accuracy_copy_are_bilingual(self):
        self.assertIn("locationReady:'الموقع جاهز'", APP_JS)
        self.assertIn("locationPaused:'التتبع متوقف مؤقتًا'", APP_JS)
        self.assertIn("locationReady:'Location ready'", APP_JS)
        self.assertIn("locationPaused:'Tracking paused'", APP_JS)
        self.assertIn("gpsAccuracy:'دقة الموقع'", APP_JS)
        self.assertIn("gpsAccuracy:'Location accuracy'", APP_JS)
        self.assertIn("gpsSteps:'الموقع + الخطوات'", APP_JS)
        self.assertIn("gpsSpeed:'Location + speed'", APP_JS)

    def test_activity_header_uses_localized_location_label(self):
        self.assertIn('id="activityLocationPill"', INDEX_HTML)
        self.assertIn('data-i18n="locationLabel"', INDEX_HTML)
        self.assertNotIn('<span class="pill gold">GPS</span>', INDEX_HTML)


if __name__ == "__main__":
    unittest.main()
