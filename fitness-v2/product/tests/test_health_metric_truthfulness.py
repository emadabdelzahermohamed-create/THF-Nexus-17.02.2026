from pathlib import Path
import json
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]
APP_JS = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "app.js"


class HealthMetricTruthfulnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_JS.read_text(encoding="utf-8")

    def test_missing_permission_is_not_rendered_as_zero(self):
        match = re.search(
            r"function healthMetricDisplayValue\(value, divisor = 1, decimals = 0\) \{.*?\n  \}",
            self.app,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Health metric formatter must remain explicit and testable")
        script = """
const locale = () => "en-US";
""" + match.group(0) + """
console.log(JSON.stringify([
  healthMetricDisplayValue(null),
  healthMetricDisplayValue(undefined),
  healthMetricDisplayValue(0),
  healthMetricDisplayValue(1234),
  healthMetricDisplayValue(1250, 1000, 1),
  healthMetricDisplayValue(-1),
  healthMetricDisplayValue("not-a-number")
]));
"""
        result = subprocess.run(
            ["node", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(result.stdout),
            ["—", "—", "0", "1,234", "1.3", "—", "—"],
        )

    def test_every_health_summary_metric_uses_truthful_formatter(self):
        match = re.search(
            r"function renderHealthSnapshot\(data\)\{.*?\n  \}",
            self.app,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        renderer = match.group(0)
        for expression in (
            "healthMetricDisplayValue(data.steps)",
            "healthMetricDisplayValue(data.exerciseSessions)",
            "healthMetricDisplayValue(data.distanceMeters,1000,1)",
            "healthMetricDisplayValue(data.activeCaloriesKcal)",
        ):
            self.assertIn(expression, renderer)
        self.assertNotRegex(renderer, r"Number\(data\.(?:steps|exerciseSessions|distanceMeters|activeCaloriesKcal)\s*\|\|\s*0\)")

if __name__ == "__main__":
    unittest.main()
