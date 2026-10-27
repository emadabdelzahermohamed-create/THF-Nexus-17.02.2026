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
        self.assertIn("item.demo.assets.map((asset,index) =>", self.app)
        self.assertIn('class="detail-frame"', self.app)
        self.assertIn("item.demo.alt[state.lang]", self.app)
        self.assertIn("animation:detail-demo-crossfade 1.8s steps(1,end) infinite", self.css)
        self.assertIn("animation-delay:-.9s", self.css)
        self.assertIn("@keyframes detail-demo-crossfade{0%,49.999%{opacity:1}50%,100%{opacity:0}}", self.css)

    def test_manual_and_system_reduced_motion_show_static_start_and_finish(self):
        self.assertIn(':root[style*="--motion: 0"] .detail-demo', self.css)
        self.assertIn(':root[style*="--motion:0"] .detail-demo', self.css)
        self.assertIn("@media(prefers-reduced-motion:reduce){.detail-demo", self.css)
        self.assertIn(".detail-demo .detail-frame{position:relative;inset:auto;aspect-ratio:4/3;opacity:1;animation:none}", self.css)

    def test_frame_labels_remain_attached_to_their_own_images(self):
        self.assertIn("escapeHtml(t(index ? 'finish' : 'start'))", self.app)
        self.assertIn(".detail-frame span{position:absolute;bottom:7px;inset-inline-start:7px", self.css)
