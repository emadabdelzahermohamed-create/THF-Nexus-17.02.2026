from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
JAVA_ROOT = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"
REPOSITORY = JAVA_ROOT / "HealthConnectRepository.kt"
POLICY = JAVA_ROOT / "HealthExerciseSessionReconciliationPolicy.kt"


class HealthActivitySessionReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = REPOSITORY.read_text(encoding="utf-8")
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_health_snapshot_reconciles_sessions_before_reward_aggregation(self):
        reconcile = self.repository.index(
            "HealthExerciseSessionReconciliationPolicy.reconcile(sessionCandidates)"
        )
        aggregate = self.repository.index(
            "val verifiedEntries = reconciledEntries.filter"
        )
        self.assertLess(reconcile, aggregate)
        self.assertIn("sessionReconciliation.duplicateCount", self.repository)

    def test_duplicate_and_conflicting_sport_records_keep_explicit_provenance(self):
        self.assertIn('withProvenanceFailure("DUPLICATE_ACTIVITY_SESSION")', self.repository)
        self.assertIn(
            'withProvenanceFailure("CONFLICTING_ACTIVITY_TYPE_AMBIGUOUS")',
            self.repository,
        )
        self.assertIn("sessionReconciliation.invalid", self.repository)

    def test_policy_limits_reconciliation_to_walking_running_and_cycling(self):
        for marker in (
            "EXERCISE_TYPE_WALKING",
            "EXERCISE_TYPE_RUNNING",
            "EXERCISE_TYPE_RUNNING_TREADMILL",
            "EXERCISE_TYPE_BIKING",
            "EXERCISE_TYPE_BIKING_STATIONARY",
        ):
            self.assertIn(marker, self.policy)
        self.assertIn("if (!candidate.verifiedForRewards)", self.policy)

    def test_unverified_health_sources_cannot_poison_verified_activity_sessions(self):
        self.assertIn("accepted += candidate", self.policy)
        self.assertIn("validVerified += candidate", self.policy)
        self.assertIn("CONFLICTING_ACTIVITY_TYPE_AMBIGUOUS", self.repository)


if __name__ == "__main__":
    unittest.main()
