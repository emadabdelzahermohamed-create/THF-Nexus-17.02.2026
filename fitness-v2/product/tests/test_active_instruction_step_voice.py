from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
VOICE_PATH = PULSE / "voice-guidance.js"


class ActiveInstructionStepVoiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.voice = VOICE_PATH.read_text(encoding="utf-8")

    def test_voice_api_exposes_single_step_speech_without_changing_full_guidance(self):
        self.assertIn("function speakStep(step, index, language = 'en', {force = false} = {})", self.voice)
        self.assertIn("return {isEnabled, setEnabled, speak, speakStep};", self.voice)
        self.assertIn("function speak(exercise, language, {force = false} = {})", self.voice)
        self.assertIn("segments.forEach((segment, index) => speakSegment(segment, locale, index > 0))", self.voice)

    def test_manual_voice_button_uses_selected_step_and_real_step_number(self):
        start = self.app.index("$('speakCue').addEventListener('click'")
        end = self.app.index("    });", start) + len("    });")
        handler = self.app[start:end]
        self.assertIn("const steps = Array.isArray(item?.steps?.[state.lang])", handler)
        self.assertIn("boundedInstructionIndex(activeInstructionIndex, steps.length)", handler)
        self.assertIn("voiceGuidance.speakStep(steps[index], index, state.lang, {force: true})", handler)
        self.assertNotIn("speakExercise(activeExercise()", handler)

    def test_current_step_voice_handles_missing_steps_without_throwing(self):
        start = self.app.index("$('speakCue').addEventListener('click'")
        end = self.app.index("    });", start) + len("    });")
        handler = self.app[start:end]
        self.assertIn("if (!steps.length) { toast(t('instructionStepsUnavailable')); return; }", handler)

    def test_step_voice_localizes_number_and_does_not_append_to_stale_queue(self):
        self.assertIn("${arabic ? 'الخطوة' : 'Step'} ${stepNumber}. ${step.trim()}", self.voice)
        self.assertIn("speakSegment(`${arabic ? 'الخطوة' : 'Step'} ${stepNumber}. ${step.trim()}`, locale, false)", self.voice)
        self.assertIn("const locale = arabic ? 'ar-EG' : 'en-US';", self.voice)


if __name__ == "__main__":
    unittest.main()
