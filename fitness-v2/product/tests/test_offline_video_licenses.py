from pathlib import Path
import hashlib
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'android/app/src/main/assets/pulse'
LEDGER = ASSETS / 'data/video-licenses.json'
MANIFEST = ASSETS / 'data/motion-manifest.js'
INDEX = ASSETS / 'index.html'
APP = ASSETS / 'app.js'
EXPECTED = {
    'romanian-deadlift',
    'standing-calf-raises',
    'leg-press',
    'hammer-curls',
    'tricep-dumbbell-kickback',
}

class OfflineVideoLicensesTest(unittest.TestCase):
    def test_first_video_batch_has_exact_cc_by_sa_attribution_and_real_files(self):
        data = json.loads(LEDGER.read_text())
        by_exercise = {item['exerciseId']: item for item in data['videos']}
        self.assertEqual(EXPECTED, set(by_exercise))
        for exercise_id, item in by_exercise.items():
            self.assertEqual('CC-BY-SA-4.0', item['license'])
            self.assertEqual('https://creativecommons.org/licenses/by-sa/4.0/', item['licenseUrl'])
            self.assertEqual('wger', item['source'])
            self.assertTrue(item['author'].strip())
            self.assertTrue(item['sourceUrl'].startswith('https://wger.de/media/exercise-video/'))
            asset = ASSETS / item['asset']
            self.assertTrue(asset.is_file(), exercise_id)
            self.assertLess(asset.stat().st_size, 12 * 1024 * 1024, exercise_id)
            self.assertEqual(item['sha256'], hashlib.sha256(asset.read_bytes()).hexdigest())

    def test_motion_manifest_maps_only_the_exact_reviewed_batch_and_exposes_credit(self):
        script = MANIFEST.read_text()
        for exercise_id in EXPECTED:
            self.assertIn(f'"{exercise_id}"', script)
            self.assertIn(f'"licenseId": "wger-{exercise_id}"', script)
        html = INDEX.read_text()
        app = APP.read_text()
        self.assertIn('id="activeDemoCredit"', html)
        self.assertIn("$('activeDemoCredit')", app)
        self.assertIn('licenseUrl', app)
        self.assertIn('sourceUrl', app)

if __name__ == '__main__':
    unittest.main()
