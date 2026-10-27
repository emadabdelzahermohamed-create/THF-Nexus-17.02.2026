from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"


class InstructionAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ASSET_ROOT / "index.html").read_text(encoding="utf-8")
        cls.javascript = (ASSET_ROOT / "app.js").read_text(encoding="utf-8")

    def test_active_workout_steps_are_named_by_the_technique_heading(self):
        self.assertIn('id="activeTechniqueTitle"', self.html)
        self.assertIn(
            '<ol id="activeSteps" aria-labelledby="activeTechniqueTitle"></ol>',
            self.html,
        )

    def test_detail_instruction_lists_are_named_by_their_headings(self):
        self.assertIn('<h3 id="detailTechniqueTitle">', self.javascript)
        self.assertIn(
            "list(item.steps[state.lang],true,'detailTechniqueTitle')",
            self.javascript,
        )
        self.assertIn('<h3 id="detailMistakesTitle">', self.javascript)
        self.assertIn(
            "list(item.commonMistakes[state.lang],false,'detailMistakesTitle')",
            self.javascript,
        )
        self.assertIn('aria-labelledby="${escapeHtml(labelId)}"', self.javascript)

    def test_active_breathing_and_safety_guidance_have_visible_headings(self):
        self.assertIn(
            '<div class="breathing-cue" role="group" aria-labelledby="activeBreathingTitle">',
            self.html,
        )
        self.assertIn(
            '<h3 id="activeBreathingTitle" data-i18n="breathing">التنفس</h3>',
            self.html,
        )
        self.assertIn(
            '<article class="surface safety-card" aria-labelledby="activeSafetyTitle">',
            self.html,
        )
        self.assertIn(
            '<h2 id="activeSafetyTitle" data-i18n="safety">السلامة أولًا</h2>',
            self.html,
        )


if __name__ == "__main__":
    unittest.main()
