from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'android/app/build.gradle'
SERVICE = ROOT / 'android/app/src/main/java/com/topherofit/thf/pulse/ActivityTrackingService.kt'
APP = ROOT / 'android/app/src/main/assets/pulse/app.js'

class FitnessFusedLocationContractTest(unittest.TestCase):
    def test_uses_current_fused_location_with_legacy_fallback(self):
        build = BUILD.read_text()
        service = SERVICE.read_text()
        self.assertIn("com.google.android.gms:play-services-location:21.3.0", build)
        self.assertIn('LocationServices.getFusedLocationProviderClient', service)
        self.assertIn('Priority.PRIORITY_HIGH_ACCURACY', service)
        self.assertIn('LocationRequest.Builder', service)
        self.assertIn('.setWaitForAccurateLocation(true)', service)
        self.assertIn('.setMaxUpdateAgeMillis(0L)', service)
        self.assertIn('.setMaxUpdateDelayMillis(0L)', service)
        self.assertIn('registerLegacyLocationProviders', service)
        self.assertIn('removeLocationUpdates(fusedLocationCallback)', service)
        legacy = service[service.index('private fun registerLegacyLocationProviders'):service.index('private fun registerStepSource')]
        self.assertIn('checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)', legacy)
        self.assertIn('checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)', legacy)

    def test_weak_observed_fix_is_visible_but_not_accepted_into_route(self):
        service = SERVICE.read_text()
        observed = service.index('lastObservedLocation = Location(location)')
        gate = service.index('GpsFixGate.accepts')
        accepted = service.index('lastLocation = Location(location)')
        self.assertLess(observed, gate)
        self.assertLess(gate, accepted)
        self.assertIn('gpsFixState', service)
        app = APP.read_text()
        self.assertIn("gpsFixState==='weak'", app)
        self.assertIn("gpsWeak", app)

if __name__ == '__main__':
    unittest.main()
