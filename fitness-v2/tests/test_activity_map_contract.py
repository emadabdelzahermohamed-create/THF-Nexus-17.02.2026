from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'android/app/src/main/assets/pulse'

class ActivityMapContractTest(unittest.TestCase):
    def test_uses_vendored_leaflet_and_real_attributed_map_tiles(self):
        html = (ASSETS / 'index.html').read_text()
        css = (ASSETS / 'styles.css').read_text()
        js = (ASSETS / 'app.js').read_text()
        self.assertTrue((ASSETS / 'vendor/leaflet/leaflet.js').is_file())
        self.assertTrue((ASSETS / 'vendor/leaflet/leaflet.css').is_file())
        self.assertTrue((ASSETS / 'vendor/leaflet/LICENSE').is_file())
        self.assertIn('./vendor/leaflet/leaflet.js', html)
        self.assertIn('./vendor/leaflet/leaflet.css', html)
        self.assertIn('https://tile.openstreetmap.org/{z}/{x}/{y}.png', js)
        self.assertIn('OpenStreetMap contributors', js)
        self.assertIn('id="activityMapCanvas"', html)
        self.assertIn('#activityMapCanvas', css)

    def test_live_route_has_recenter_accuracy_and_google_maps_handoff(self):
        html = (ASSETS / 'index.html').read_text()
        js = (ASSETS / 'app.js').read_text()
        self.assertIn('id="activityMapRecenter"', html)
        self.assertIn('id="activityGoogleMaps"', html)
        self.assertIn('accuracyMetres', js)
        self.assertIn('fitActivityMapToRoute', js)
        self.assertIn('https://www.google.com/maps/search/?api=1&query=', js)
        self.assertIn('map.panTo(lastLatLng', js)
        main = (ROOT / 'android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt').read_text()
        self.assertIn('uri.host in setOf("www.google.com", "maps.google.com")', main)

    def test_offline_fallback_route_is_retained(self):
        html = (ASSETS / 'index.html').read_text()
        js = (ASSETS / 'app.js').read_text()
        self.assertIn('id="activityMapFallback"', html)
        self.assertIn("if(!map){const lats=points.map", js)

if __name__ == '__main__':
    unittest.main()
