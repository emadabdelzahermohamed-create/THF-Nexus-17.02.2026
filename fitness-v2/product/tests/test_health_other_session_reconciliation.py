from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
JAVA_ROOT = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"
REPOSITORY = JAVA_ROOT / "HealthConnectRepository.kt"
SESSION_POLICY = JAVA_ROOT / "HealthExerciseSessionReconciliationPolicy.kt"


class HealthOtherSessionReconciliationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = REPOSITORY.read_text(encoding="utf-8")
        cls.session_policy = SESSION_POLICY.read_text(encoding="utf-8")

    def test_repository_passes_raw_health_connect_exercise_type_to_reconciliation(self):
        self.assertIn("exerciseType = session.exerciseType", self.repository)

    def test_non_cardio_sessions_are_reconciled_without_collapsing_distinct_types(self):
        self.assertIn("else -> HealthActivitySessionKind.OTHER", self.session_policy)
        self.assertIn(".map { it.exerciseType }.distinct().size > 1", self.session_policy)


if __name__ == "__main__":
    unittest.main()
