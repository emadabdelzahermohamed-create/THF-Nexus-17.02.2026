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
    / "voice-guidance.js"
)


class VoiceGuidanceRuntimeTest(unittest.TestCase):
    def run_node(self, body: str):
        script = f"""
const {{ createVoiceGuidance }} = require({json.dumps(str(MODULE))});
{body}
"""
        return subprocess.run(
            ["node", "-e", script],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_preference_persists_and_blocks_automatic_cues_only(self):
        result = self.run_node(
            """
const values = new Map();
const calls = [];
const guide = createVoiceGuidance({
  storage: { getItem: key => values.has(key) ? values.get(key) : null,
             setItem: (key, value) => values.set(key, String(value)) },
  speakNative: (text, locale) => calls.push({text, locale}),
});
const exercise = {
  name: 'Push-up', setup: 'Hands under shoulders',
  steps: ['Lower with control', 'Press evenly'],
  breathing: 'Exhale while pressing', safety: 'Stop for sharp pain',
};
if (!guide.isEnabled()) throw new Error('voice should default on');
guide.setEnabled(false);
if (values.get('pulse.v2.voiceGuidance') !== '0') throw new Error('disabled preference not saved');
if (guide.speak(exercise, 'en')) throw new Error('automatic cue ignored disabled preference');
if (!guide.speak(exercise, 'en', {force: true})) throw new Error('manual cue should remain available');
if (calls.length !== 1) throw new Error(`expected one manual cue, got ${calls.length}`);
console.log(JSON.stringify(calls[0]));
"""
        )
        self.assertEqual(0, result.returncode, result.stderr)
        call = json.loads(result.stdout)
        self.assertEqual("en-US", call["locale"])
        self.assertIn("Push-up", call["text"])
        self.assertIn("Stop for sharp pain", call["text"])

    def test_arabic_cue_uses_arabic_locale_and_complete_coaching_text(self):
        result = self.run_node(
            """
const calls = [];
const guide = createVoiceGuidance({
  storage: { getItem: () => '1', setItem: () => {} },
  speakNative: (text, locale) => calls.push({text, locale}),
});
guide.speak({
  name: 'القرفصاء', setup: 'ثبّت القدمين',
  steps: ['انزل بتحكم', 'اصعد بثبات'],
  breathing: 'ازفر أثناء الصعود', safety: 'توقف عند الألم الحاد',
}, 'ar');
console.log(JSON.stringify(calls[0]));
"""
        )
        self.assertEqual(0, result.returncode, result.stderr)
        call = json.loads(result.stdout)
        self.assertEqual("ar-EG", call["locale"])
        for phrase in (
            "القرفصاء", "ثبّت القدمين", "انزل بتحكم",
            "ازفر أثناء الصعود", "توقف عند الألم الحاد",
        ):
            self.assertIn(phrase, call["text"])


if __name__ == "__main__":
    unittest.main()
