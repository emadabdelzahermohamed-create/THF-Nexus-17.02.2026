import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
MOTION_MANIFEST_PATH = PULSE / "data" / "motion-manifest.json"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"


class DemoCoverageTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MOTION_MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_catalog_coverage_counts_are_exhaustive_and_typed(self):
        ids = {item["id"] for item in self.catalog}
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(7, len(self.manifest))
        self.assertTrue(set(self.manifest).issubset(ids))
        kinds = [entry["kind"] for entry in self.manifest.values()]
        self.assertEqual(5, kinds.count("offline_video"))
        self.assertEqual(2, kinds.count("verified_frame_sequence"))
        self.assertEqual(105, len(self.catalog) - len(self.manifest))
        for item in self.catalog:
            self.assertEqual(2, len(item["demo"]["assets"]), item["id"])
            self.assertTrue(all(asset.startswith("media/free-exercise-db/") for asset in item["demo"]["assets"]))
        for entry in self.manifest.values():
            self.assertTrue(entry["asset"].startswith("media/motion/"))
            self.assertEqual(64, len(entry["sha256"]))

    def test_cards_and_details_render_the_manifest_derived_demo_type(self):
        self.assertIn("function motionCoverageLabel(item, compact = false)", self.app)
        self.assertIn("const entry = motionAsset(item);", self.app)
        self.assertIn("if (entry?.kind === 'offline_video')", self.app)
        self.assertIn("if (entry?.kind === 'verified_frame_sequence')", self.app)
        self.assertIn("return referenceCoverageLabel(item, compact);", self.app)
        self.assertGreaterEqual(self.app.count("motionCoverageLabel(item"), 3)
        self.assertIn("demo-coverage-badge", self.app)

    def test_coverage_summary_is_dynamic_bilingual_and_visible_in_training_header(self):
        self.assertIn('id="motionCoverageSummary"', self.html)
        self.assertIn("function renderMotionCoverageSummary()", self.app)
        self.assertIn("counts.offlineVideo", self.app)
        self.assertIn("counts.verifiedClips", self.app)
        self.assertIn("counts.referenceFrames", self.app)
        self.assertIn("Motion coverage:", self.app)
        self.assertIn("تغطية الحركة:", self.app)
        self.assertIn("renderMotionCoverageSummary();", self.app)

    def test_fallback_label_does_not_claim_reference_motion_is_pending(self):
        self.assertNotIn("Reference images — motion pending", self.app)
        self.assertIn("Auto-animated reference frames", self.app)
        self.assertIn("صور مرجعية تتحرك تلقائيًا", self.app)


if __name__ == "__main__":
    unittest.main()
