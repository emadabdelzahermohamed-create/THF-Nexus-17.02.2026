import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[3]
MODULE = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "assets"
    / "pulse"
    / "rest-timer.js"
)
APP = MODULE.with_name("app.js")
INDEX = MODULE.with_name("index.html")


class RestTimerRuntimeTest(unittest.TestCase):
    def run_node(self, body: str):
        script = f"""
const {{ createRestTimer }} = require({json.dumps(str(MODULE))});
{body}
"""
        return subprocess.run(
            ["node", "-e", script],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_remaining_time_is_derived_from_deadline_after_throttled_gap(self):
        result = self.run_node(
            """
let clock = 1_000_000;
const timer = createRestTimer({now: () => clock});
const endsAt = timer.deadline(90);
clock += 65_400;
console.log(JSON.stringify({endsAt, remaining: timer.remaining(endsAt)}));
"""
        )
        self.assertEqual(0, result.returncode, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(1_090_000, value["endsAt"])
        self.assertEqual(25, value["remaining"])

    def test_expired_or_invalid_deadline_never_returns_negative_time(self):
        result = self.run_node(
            """
const timer = createRestTimer({now: () => 50_000});
console.log(JSON.stringify([
  timer.remaining(49_999),
  timer.remaining(0),
  timer.remaining('not-a-time'),
]));
"""
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([0, 0, 0], json.loads(result.stdout))

    def test_workout_persists_and_restores_deadline_based_rest(self):
        app = APP.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")

        self.assertLess(index.index("./rest-timer.js"), index.index("./app.js"))
        self.assertIn("window.THFRestTimer.createRestTimer()", app)
        self.assertIn("state.active.restEndsAtMs=restTimer.deadline(seconds)", app)
        self.assertIn("restTimer.remaining(state.active?.restEndsAtMs)", app)
        self.assertIn("resumeRest()", app)
        self.assertNotIn("state.restRemaining--", app)


if __name__ == "__main__":
    unittest.main()
