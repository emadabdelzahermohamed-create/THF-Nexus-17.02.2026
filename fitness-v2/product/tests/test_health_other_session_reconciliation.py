from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
JAVA_ROOT = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"
REPOSITORY = JAVA_ROOT / "HealthConnectRepository.kt"
SESSION_POLICY = JAVA_ROOT / "HealthExerciseSessionReconciliationPolicy.kt"
EVIDENCE_POLICY = JAVA_ROOT / "HealthRecordEvidencePolicy.kt"
PRESENTATION_POLICY = JAVA_ROOT / "HealthRecordProvenancePresentationPolicy.kt"


class HealthOtherSessionReconciliationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = REPOSITORY.read_text(encoding="utf-8")
        cls.session_policy = SESSION_POLICY.read_text(encoding="utf-8")
        cls.evidence_policy = EVIDENCE_POLICY.read_text(encoding="utf-8")
        cls.presentation_policy = PRESENTATION_POLICY.read_text(encoding="utf-8")

    def test_repository_passes_raw_health_connect_exercise_type_to_reconciliation(self):
        self.assertIn("exerciseType = session.exerciseType", self.repository)

    def test_non_unknown_other_sessions_are_reconciled_without_collapsing_distinct_types(self):
        self.assertIn("ExerciseSessionRecord.EXERCISE_TYPE_UNKNOWN -> null", self.session_policy)
        self.assertIn("else -> HealthActivitySessionKind.OTHER", self.session_policy)
        self.assertIn(".map { it.exerciseType }.distinct().size > 1", self.session_policy)

    def test_unknown_exercise_type_fails_closed_at_evidence_and_presentation_boundaries(self):
        self.assertIn('return supported("UNKNOWN_EXERCISE_TYPE")', self.evidence_policy)
        self.assertIn(
            "if (exerciseType == ExerciseSessionRecord.EXERCISE_TYPE_UNKNOWN) return false",
            self.presentation_policy,
        )


if __name__ == "__main__":
    unittest.main()
