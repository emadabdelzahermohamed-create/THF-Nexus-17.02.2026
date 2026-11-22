from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
JAVA_ROOT = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"
REPOSITORY = JAVA_ROOT / "HealthConnectRepository.kt"
POLICY = JAVA_ROOT / "HealthRecordDeduplicationPolicy.kt"


class HealthRecordVersionConflictTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = REPOSITORY.read_text(encoding="utf-8")
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_repository_fingerprints_reward_relevant_record_and_provenance_fields(self):
        self.assertIn("payloadFingerprint = entry.rewardPayloadFingerprint()", self.repository)
        for marker in (
            "current.count.toString()",
            "current.distance.inMeters.metricFingerprint()",
            "current.energy.inKilocalories.metricFingerprint()",
            "current.exerciseType.toString()",
            "evidence.recordingMethod.toString()",
            "evidence.deviceType?.toString()",
            "evidence.verifiedForRewards.toString()",
        ):
            self.assertIn(marker, self.repository)

    def test_conflicting_latest_versions_are_preserved_but_excluded_from_rewards(self):
        self.assertIn("deduplication.conflicting.map", self.repository)
        self.assertIn('withProvenanceFailure("CONFLICTING_RECORD_VERSION_PAYLOAD")', self.repository)
        self.assertIn("conflictingVersionEntries", self.repository)

    def test_policy_requires_comparable_identical_fingerprints_for_tied_latest_versions(self):
        self.assertIn("latestRecords.size > 1", self.policy)
        self.assertIn("fingerprints.all { it != null }", self.policy)
        self.assertIn("fingerprints.distinct().size == 1", self.policy)
        self.assertIn("conflicting += latestRecords", self.policy)

    def test_older_revision_is_not_resurrected_when_latest_revision_conflicts(self):
        self.assertIn("duplicateCount += group.size - latestRecords.size", self.policy)
        self.assertIn("selectedByKey += latestRecords.first()", self.policy)
        self.assertIn("conflicting += latestRecords", self.policy)


if __name__ == "__main__":
    unittest.main()
