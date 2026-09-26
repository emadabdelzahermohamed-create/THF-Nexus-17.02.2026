import tempfile
import unittest
from pathlib import Path

from ReleaseOps.FitnessStandalone.backend_release_contract import inventory


GOOD_SOURCE = """
router.post('/api/auth/login', login)
router.post('/api/auth/logout', logout)
router.get('/api/session', session)
router.post('/api/workout/sync', sync)
const userId = session.userId
const expectedSet = body.expectedSet
throw new Error('exercise_out_of_order')
throw new Error('stale_set_sequence')
return { acceptedSet, leaderboard: trustedScore, competition: ranked }
"""


class FitnessBackendReleaseContractTests(unittest.TestCase):
    def test_release_critical_contracts_report_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "backend" / "index.ts"
            path.parent.mkdir()
            path.write_text(GOOD_SOURCE, encoding="utf-8")
            report = inventory(root, "a" * 64, "2026-09-26T17:45:00Z")
        self.assertEqual(report["result"], "PROGRESS")
        self.assertTrue(report["checks"]["set_sequence_contract_complete"])
        self.assertIn("health_ingestion_contract_present", report["open_checks"])

    def test_missing_user_scope_and_sequence_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "backend" / "index.ts"
            path.parent.mkdir()
            path.write_text("router.post('/api/login', login)\n", encoding="utf-8")
            report = inventory(root, "b" * 64, "2026-09-26T17:45:00Z")
        self.assertEqual(report["result"], "BLOCKED")
        self.assertFalse(report["checks"]["authenticated_user_scope_present"])
        self.assertFalse(report["checks"]["set_sequence_contract_complete"])

    def test_source_content_is_not_copied_to_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "backend" / "index.ts"
            path.parent.mkdir()
            path.write_text(GOOD_SOURCE + "\nconst secret='do-not-export';\n", encoding="utf-8")
            report = inventory(root, "c" * 64, "2026-09-26T17:45:00Z")
        self.assertNotIn("do-not-export", str(report))

    def test_source_root_below_build_directory_is_not_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "build" / "fitness"
            path = root / "backend" / "index.ts"
            path.parent.mkdir(parents=True)
            path.write_text(GOOD_SOURCE, encoding="utf-8")
            report = inventory(root, "d" * 64, "2026-09-26T17:45:00Z")
        self.assertEqual(report["result"], "PROGRESS")
        self.assertEqual(report["source"]["file_count"], 1)
        self.assertEqual(report["source"]["backend_file_count"], 1)


if __name__ == "__main__":
    unittest.main()
