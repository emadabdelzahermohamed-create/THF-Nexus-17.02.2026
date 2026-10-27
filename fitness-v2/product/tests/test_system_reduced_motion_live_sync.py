import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "app.js"


def extract_function(source, name):
    marker = f"function {name}("
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"Unclosed function: {name}")


class SystemReducedMotionLiveSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_system_preference_change_is_bound_with_legacy_webview_fallback(self):
        helper = extract_function(self.source, "bindSystemReducedMotionPreference")
        self.assertIn("mediaQuery.addEventListener('change', sync)", helper)
        self.assertIn("mediaQuery.addListener(sync)", helper)
        self.assertIn("if (hasSavedPreference()) return;", helper)
        self.assertIn("applyPreference(Boolean(event.matches), false)", helper)

    def test_system_preference_binding_is_connected_to_the_existing_motion_runtime(self):
        self.assertIn("window.matchMedia?.('(prefers-reduced-motion: reduce)')", self.source)
        self.assertIn("() => store.getItem('pulse.v2.reduceMotion') !== null", self.source)
        self.assertIn("applyMotionPreference", self.source)
        start = self.source.index("function applyMotionPreference(")
        end = self.source.index("\\n  function bindSystemReducedMotionPreference", start)
        apply_body = self.source[start:end]
        self.assertIn("classList.toggle('motion-reduced',enabled)", apply_body)
        self.assertIn("syncExerciseDemoVideos()", apply_body)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for the isolated runtime contract")
    def test_runtime_updates_follow_system_only_until_user_saves_a_choice(self):
        helper = extract_function(self.source, "bindSystemReducedMotionPreference")
        script = helper + r"""
const assert = require('assert');
const calls = [];
let saved = null;
let modernListener = null;
const modern = { addEventListener(type, listener) {
  assert.strictEqual(type, 'change');
  modernListener = listener;
} };
bindSystemReducedMotionPreference(modern, () => saved !== null, (enabled, persist) => calls.push([enabled, persist]));
modernListener({ matches: true });
assert.deepStrictEqual(calls, [[true, false]]);
saved = '0';
modernListener({ matches: false });
assert.deepStrictEqual(calls, [[true, false]]);
let legacyListener = null;
const legacy = { addListener(listener) { legacyListener = listener; } };
bindSystemReducedMotionPreference(legacy, () => false, (enabled, persist) => calls.push([enabled, persist]));
legacyListener({ matches: false });
assert.deepStrictEqual(calls, [[true, false], [false, false]]);
bindSystemReducedMotionPreference(null, () => false, () => { throw new Error('must not run'); });
console.log('system reduced-motion runtime contract PASS');
"""
        result = subprocess.run(["node", "-e", script], text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("runtime contract PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
