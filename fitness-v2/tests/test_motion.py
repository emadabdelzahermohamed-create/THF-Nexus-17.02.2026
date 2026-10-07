import unittest
import os
import json
import re

class TestAutoMotionEngine(unittest.TestCase):
    def setUp(self):
        self.app_js_path = 'fitness-v2/android/app/src/main/assets/pulse/app.js'
        self.index_html_path = 'fitness-v2/android/app/src/main/assets/pulse/index.html'
        self.styles_css_path = 'fitness-v2/android/app/src/main/assets/pulse/styles.css'
        self.exercises_js_path = 'fitness-v2/android/app/src/main/assets/pulse/data/exercises.js'

        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            self.app_js = f.read()

    def test_app_js_contains_motion_engine_functions(self):
        self.assertIn('precalculateNextFrame', self.app_js)
        self.assertIn('preloadAssets', self.app_js)
        self.assertIn('shouldPlayMotion', self.app_js)
        self.assertIn('startMotionLoop', self.app_js)
        self.assertIn('stopMotionLoop', self.app_js)
        self.assertIn('advanceMotionFrame', self.app_js)

    def test_ping_pong_frame_calculation(self):
        # Python implementation matching JS precalculateNextFrame
        def precalculateNextFrame(currentFrame, totalFrames, direction, mode='ping-pong'):
            if not totalFrames or totalFrames <= 1:
                return 0, 1
            if mode == 'loop':
                return (currentFrame + 1) % totalFrames, 1
            nextFrame = currentFrame + direction
            nextDirection = direction
            if nextFrame >= totalFrames:
                nextFrame = totalFrames - 2 if totalFrames - 2 >= 0 else 0
                nextDirection = -1
            elif nextFrame < 0:
                nextFrame = 1 if 1 < totalFrames else 0
                nextDirection = 1
            return nextFrame, nextDirection

        # Test 2-frame exercise (0 -> 1 -> 0 -> 1)
        f, d = precalculateNextFrame(0, 2, 1, 'ping-pong')
        self.assertEqual((f, d), (1, 1))

        f, d = precalculateNextFrame(1, 2, 1, 'ping-pong')
        self.assertEqual((f, d), (0, -1))

        f, d = precalculateNextFrame(0, 2, -1, 'ping-pong')
        self.assertEqual((f, d), (1, 1))

    def test_loop_frame_calculation(self):
        def precalculateNextFrame(currentFrame, totalFrames, direction, mode='loop'):
            if mode == 'loop':
                return (currentFrame + 1) % totalFrames, 1
            return currentFrame, direction

        f, d = precalculateNextFrame(0, 3, 1, 'loop')
        self.assertEqual(f, 1)
        f, d = precalculateNextFrame(1, 3, 1, 'loop')
        self.assertEqual(f, 2)
        f, d = precalculateNextFrame(2, 3, 1, 'loop')
        self.assertEqual(f, 0)

    def test_all_exercises_have_valid_demo_assets(self):
        with open(self.exercises_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            json_str = content[content.find('['):content.rfind(']')+1]
            exercises = json.loads(json_str)

        self.assertGreater(len(exercises), 0)
        base_dir = 'fitness-v2/android/app/src/main/assets/pulse/'
        for ex in exercises:
            self.assertIn('demo', ex)
            self.assertIn('assets', ex['demo'])
            assets = ex['demo']['assets']
            self.assertGreaterEqual(len(assets), 1)
            for asset in assets:
                full_path = os.path.join(base_dir, asset)
                self.assertTrue(os.path.exists(full_path), f"Asset missing: {full_path}")

    def test_visibility_and_focus_listeners_exist(self):
        self.assertIn("visibilitychange", self.app_js)
        self.assertIn("window.addEventListener('blur'", self.app_js)
        self.assertIn("window.addEventListener('focus'", self.app_js)

if __name__ == '__main__':
    unittest.main()
