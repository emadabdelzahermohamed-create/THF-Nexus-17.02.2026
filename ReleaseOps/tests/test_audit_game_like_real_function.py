import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / 'validators' / 'audit_game_like_real_function.py'
spec = importlib.util.spec_from_file_location('game_like_audit', MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GameLikeRealFunctionTests(unittest.TestCase):
    def _root(self, body: str):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        src = root / 'android' / 'app' / 'src' / 'main' / 'java' / 'thf'
        src.mkdir(parents=True)
        (src / 'Game.kt').write_text(body)
        self.addCleanup(td.cleanup)
        return root

    def test_learning_contract_passes_with_real_interaction_progress_and_motion(self):
        root = self._root('''
            import android.view.MotionEvent
            class QuizGame {
              var score = 0
              fun onTouchEvent(event: MotionEvent): Boolean { score += 1; return true }
              fun update() { val question = "math"; val answer = "choice" }
            }
        ''')
        r = mod.audit(root, 'learning')
        self.assertEqual(r['source_contract'], 'PASS')

    def test_fitness_contract_passes_with_timer_input_and_reps(self):
        root = self._root('''
            import android.os.CountDownTimer
            class WorkoutGame {
              var reps = 0
              fun setOnClickListener() { reps += 1 }
              fun exerciseTimer() { val timer: CountDownTimer? = null; val squat = true }
            }
        ''')
        r = mod.audit(root, 'fitness')
        self.assertEqual(r['source_contract'], 'PASS')

    def test_fitness_contract_accepts_sensor_motion_and_plural_reps(self):
        root = self._root('''
            import android.view.MotionEvent
            import android.view.Choreographer
            import android.hardware.SensorManager
            class MotionSession {
              var reps = 0
              fun onTouchEvent(event: MotionEvent): Boolean { reps = 0; return true }
              fun doFrame(frameTimeNanos: Long) { Choreographer.getInstance().postFrameCallback { } }
              fun sample(sensorManager: SensorManager) { reps += 1 }
            }
        ''')
        r = mod.audit(root, 'fitness')
        self.assertEqual(r['source_contract'], 'PASS')
        self.assertNotIn('fitness_domain', r['missing_required_signals'])

    def test_ui_only_shell_fails(self):
        root = self._root('class Main { val title = "Welcome" }')
        r = mod.audit(root, 'learning')
        self.assertEqual(r['source_contract'], 'FAIL')
        self.assertIn('interactive_input', r['missing_required_signals'])
        self.assertIn('state_or_progression', r['missing_required_signals'])

    def test_wrong_domain_fails(self):
        root = self._root('''
            import android.view.MotionEvent
            class FitnessOnly {
              var score = 0
              fun onTouchEvent(e: MotionEvent) = true
              fun update() { val workout = "squat" }
            }
        ''')
        r = mod.audit(root, 'learning')
        self.assertEqual(r['source_contract'], 'FAIL')
        self.assertIn('learning_domain', r['missing_required_signals'])


if __name__ == '__main__':
    unittest.main()
