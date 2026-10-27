import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
CSS_PATH = PULSE / "styles.css"
CATALOG_PATH = PULSE / "data" / "exercises.js"


class DetailDemoAutoplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.css = CSS_PATH.read_text(encoding="utf-8")
        source = CATALOG_PATH.read_text(encoding="utf-8")
        payload = source.split("=", 1)[1].strip().removesuffix(";")
        cls.exercises = json.loads(payload)

    def test_all_detail_demos_have_a_complete_two_frame_loop(self):
        self.assertEqual(112, len(self.exercises))
        self.assertTrue(all(len(item["demo"]["assets"]) == 2 for item in self.exercises))
        self.assertIn("function referenceMotionPlayer(item, context = 'detail')", self.app)
        self.assertIn("item.demo.assets.slice(0, 2)", self.app)
        self.assertIn("const safeAssets = assets.length === 2", self.app)
        self.assertIn('class="exercise-reference-motion ${className}"', self.app)
        self.assertIn("exercise-reference-motion-detail", self.app)
        self.assertIn("thf-reference-start 1.8s steps(1,end) infinite", self.css)
        self.assertIn("thf-reference-finish 1.8s steps(1,end) infinite", self.css)
        self.assertIn("@keyframes thf-reference-start", self.css)
        self.assertIn("@keyframes thf-reference-finish", self.css)

    def test_manual_and_system_reduced_motion_show_static_start_and_finish(self):
        self.assertIn(".motion-reduced .exercise-reference-motion img:first-of-type", self.css)
        self.assertIn(".motion-reduced .exercise-reference-motion img:last-of-type", self.css)
        self.assertIn("@media(prefers-reduced-motion:reduce){.exercise-reference-motion", self.css)
        self.assertIn("animation:none!important", self.css)

    def test_bilingual_demo_description_remains_attached_to_the_reference_sequence(self):
        self.assertIn("const alt = escapeHtml(local(item.demo?.alt) || local(item.name));", self.app)
        self.assertIn('role="img" aria-label="${alt}"', self.app)
        self.assertIn('alt="" aria-hidden="true"', self.app)
        self.assertIn("local(item.demo?.alt)", self.app)
