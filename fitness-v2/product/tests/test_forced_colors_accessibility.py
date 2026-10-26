from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
STYLES_PATH = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "assets"
    / "pulse"
    / "styles.css"
)


class ForcedColorsAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.styles = STYLES_PATH.read_text()
        match = re.search(
            r"@media\s*\(forced-colors:\s*active\)\s*\{(?P<body>.*)\}\s*$",
            cls.styles,
            re.S,
        )
        cls.forced_colors = match.group("body") if match else ""

    def test_interactive_surfaces_keep_system_borders_in_forced_colors(self):
        self.assertIn("forced-color-adjust:auto", self.forced_colors)
        for selector in (
            ".button",
            ".icon-button",
            ".primary-nav button",
            ".activity-mode-button",
            ".program-card",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.forced_colors)
        self.assertIn("border:1px solid ButtonText", self.forced_colors)

    def test_keyboard_focus_uses_system_highlight_in_forced_colors(self):
        self.assertIn(":focus-visible", self.forced_colors)
        self.assertIn("outline:3px solid Highlight", self.forced_colors)
        self.assertIn("outline-offset:3px", self.forced_colors)

    def test_status_text_is_not_distinguished_by_custom_color_alone(self):
        for selector in (".status-chip", ".pill.gold", ".error-message"):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.forced_colors)
        self.assertIn("color:CanvasText", self.forced_colors)
        self.assertIn("border-color:CanvasText", self.forced_colors)


if __name__ == "__main__":
    unittest.main()
