import sqlite3
import unittest
import math

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workout_store import (
    WorkoutConflictError,
    WorkoutSession,
    WorkoutSet,
    WorkoutStore,
    WorkoutValidationError,
)


def session(version=1, load=50.0, client_id="thf-workout-test-0001"):
    return WorkoutSession(
        client_record_id=client_id,
        client_record_version=version,
        started_at="2026-10-02T04:00:00Z",
        ended_at="2026-10-02T04:30:00Z",
        sport="strength_training",
        exercise_session_type=80,
        source="THF_ANDROID",
        provenance_package="com.topherofit.thf.pulse",
        sets=(
            WorkoutSet("back-squat", 1, "warmup", 10, 20, 60, 4, 6),
            WorkoutSet("back-squat", 2, "working", 5, load, 120, 8, 2),
        ),
    )


class WorkoutStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = WorkoutStore(sqlite3.connect(":memory:"))

    def test_idempotent_sync_and_versioned_update(self):
        self.assertEqual("inserted", self.store.sync("user-1", session()))
        self.assertEqual("duplicate", self.store.sync("user-1", session()))
        with self.assertRaises(WorkoutConflictError):
            self.store.sync("user-1", session(load=51))
        self.assertEqual("updated", self.store.sync("user-1", session(version=2, load=60)))
        self.assertEqual("stale", self.store.sync("user-1", session(version=1, load=10)))
        summary = self.store.progress_summary("user-1")
        self.assertEqual(1, summary["workouts"])
        self.assertEqual(300, summary["volumeKg"])
        self.assertEqual(60, summary["personalRecords"][0]["maxLoadKg"])

        history = self.store.history("user-1")
        self.assertEqual(1, len(history))
        self.assertEqual("thf-workout-test-0001", history[0]["clientRecordId"])
        self.assertEqual(2, history[0]["clientRecordVersion"])
        self.assertEqual(300, history[0]["volumeKg"])
        self.assertEqual(2, len(history[0]["sets"]))
        self.assertEqual(120, history[0]["sets"][1]["restSeconds"])
        self.assertEqual(8, history[0]["sets"][1]["rpe"])
        self.assertEqual(2, history[0]["sets"][1]["rir"])

    def test_records_and_claims_are_user_scoped_and_server_authoritative(self):
        self.store.sync("user-1", session())
        self.assertEqual([], self.store.history("user-2"))
        accepted = self.store.verify_competition_claim("user-1", "thf-workout-test-0001", 250)
        self.assertTrue(accepted["accepted"])
        self.assertEqual("SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED", accepted["verificationLevel"])
        rejected = self.store.verify_competition_claim("user-1", "thf-workout-test-0001", 999)
        self.assertFalse(rejected["accepted"])
        self.assertEqual("CLAIM_MISMATCH", rejected["reason"])

    def test_rejects_untrusted_provenance_and_invalid_effort(self):
        invalid_source = session().__class__(**{**session().__dict__, "source": "CLIENT_CLAIM"})
        with self.assertRaises(WorkoutValidationError):
            self.store.sync("user-1", invalid_source)
        bad_set = WorkoutSet("squat", 1, "working", 5, 50, 60, 11, 0)
        invalid_rpe = session().__class__(**{**session().__dict__, "sets": (bad_set,)})
        with self.assertRaises(WorkoutValidationError):
            self.store.sync("user-1", invalid_rpe)
        invalid_package = session().__class__(**{**session().__dict__, "provenance_package": "com.example.impostor"})
        with self.assertRaises(WorkoutValidationError):
            self.store.sync("user-1", invalid_package)
        nan_set = WorkoutSet("squat", 1, "working", 5, math.nan, 60, 8, 2)
        invalid_nan = session().__class__(**{**session().__dict__, "sets": (nan_set,)})
        with self.assertRaises(WorkoutValidationError):
            self.store.sync("user-1", invalid_nan)


if __name__ == "__main__":
    unittest.main()
