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


class KeyboardFocusTest(unittest.TestCase):
    def test_dynamic_training_actions_have_a_visible_focus_indicator(self):
        styles = STYLES_PATH.read_text()
        rules = re.findall(r"([^{}]+)\{([^{}]+)\}", styles)
        focus_rules = [
            (selectors, declarations)
            for selectors, declarations in rules
            if ":focus-visible" in selectors
            and "outline:3px solid var(--blue)" in declarations
            and "outline-offset:3px" in declarations
        ]

        required = {
            ".program-card:focus-visible",
            ".session-exercises button:focus-visible",
            ".activity-mode-button:focus-visible",
            ".set-complete:focus-visible",
            ".text-button:focus-visible",
        }
        covered = {
            selector.strip()
            for selectors, _ in focus_rules
            for selector in selectors.split(",")
        }
        self.assertEqual(set(), required - covered)


if __name__ == "__main__":
    unittest.main()
