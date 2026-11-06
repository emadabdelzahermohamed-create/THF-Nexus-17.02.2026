from datetime import datetime, timedelta, timezone
from io import BytesIO
import base64
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api import FitnessApi
from competition_store import CompetitionStore
from auth import HmacAccessTokenVerifier
from workout_store import WorkoutSession, WorkoutSet, WorkoutStore


KEY = b"k" * 32
TOKEN_NOW = 1_791_000_000


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def token(user="user-1", session="session-0001"):
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT", "kid": "primary"}, separators=(",", ":")).encode())
    claims = {
        "iss": "https://accounts.topherofit.com",
        "aud": "fitness-v2",
        "sub": user,
        "sid": session,
        "iat": TOKEN_NOW - 10,
        "exp": TOKEN_NOW + 300,
    }
    payload = b64(json.dumps(claims, separators=(",", ":")).encode())
    signature = b64(hmac.new(KEY, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


class CompetitionApiTest(unittest.TestCase):
    def setUp(self):
        self.store = WorkoutStore(sqlite3.connect(":memory:"))
        self.addCleanup(self.store.db.close)
        self.api = None
        verifier = HmacAccessTokenVerifier(
            {"primary": KEY},
            "https://accounts.topherofit.com",
            "fitness-v2",
            now=lambda: TOKEN_NOW,
            is_session_revoked=lambda user, session: self.api.is_session_revoked(user, session),
        )
        self.api = FitnessApi(self.store, verifier, competition_admin_key="competition-admin-secret")

    def request(self, path, method="GET", body=None, bearer=None, admin_key=None, query=""):
        raw = b"" if body is None else json.dumps(body, separators=(",", ":")).encode()
        environ = {
            "PATH_INFO": path,
            "REQUEST_METHOD": method,
            "QUERY_STRING": query,
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)),
            "CONTENT_TYPE": "application/json" if body is not None else "",
        }
        if bearer:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {bearer}"
        if admin_key:
            environ["HTTP_X_THF_COMPETITION_ADMIN_KEY"] = admin_key
        captured = {}
        result = self.api(environ, lambda status, headers: captured.update(status=status, headers=dict(headers)))
        return captured["status"], json.loads(b"".join(result))

    def event_window(self):
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=2)
        end = now + timedelta(hours=2)
        return start.isoformat(), end.isoformat()

    def create_event(self, competition_id="strength-open", max_participants=20):
        start, end = self.event_window()
        status, body = self.request(
            "/api/v2/admin/competitions",
            method="POST",
            bearer=token("admin-user"),
            admin_key="competition-admin-secret",
            body={
                "id": competition_id,
                "title": "Strength Open",
                "sport": "strength_training",
                "metric": "strength_volume_kg_reps",
                "startsAt": start,
                "endsAt": end,
                "maxParticipants": max_participants,
            },
        )
        self.assertEqual("201 Created", status, body)
        return start, end

    def sync_workout(self, user="user-1", record_id="thf-strength-0001", load=50, version=1, start=None, end=None, source="THF_ANDROID", provenance_package="com.topherofit.thf.pulse"):
        now = datetime.now(timezone.utc)
        started_at = start or (now - timedelta(minutes=30)).isoformat()
        ended_at = end or (now - timedelta(minutes=20)).isoformat()
        self.store.sync(
            user,
            WorkoutSession(
                client_record_id=record_id,
                client_record_version=version,
                started_at=started_at,
                ended_at=ended_at,
                sport="strength_training",
                exercise_session_type=80,
                source=source,
                provenance_package=provenance_package,
                sets=(WorkoutSet("back-squat", 1, "working", 5, float(load), 120, 8, 2),),
            ),
        )

    def test_admin_key_gates_creation_and_public_list_is_account_scoped(self):
        start, end = self.event_window()
        body = {
            "id": "strength-open",
            "title": "Strength Open",
            "sport": "strength_training",
            "metric": "strength_volume_kg_reps",
            "startsAt": start,
            "endsAt": end,
        }
        denied = self.request(
            "/api/v2/admin/competitions",
            method="POST",
            bearer=token("admin-user"),
            admin_key="wrong-key",
            body=body,
        )
        self.assertEqual("403 Forbidden", denied[0])
        created = self.request(
            "/api/v2/admin/competitions",
            method="POST",
            bearer=token("admin-user"),
            admin_key="competition-admin-secret",
            body=body,
        )
        self.assertEqual("201 Created", created[0])
        self.assertEqual("strength_volume_kg_reps", created[1]["metric"])
        self.assertFalse(created[1]["rewardEligible"])
        listed = self.request("/api/v2/competitions", bearer=token("user-1"))
        self.assertEqual("200 OK", listed[0])
        self.assertEqual("strength-open", listed[1]["items"][0]["id"])
        self.assertFalse(listed[1]["items"][0]["joined"])

    def test_openapi_documents_all_competition_routes_and_unverified_boundary(self):
        specification = json.loads(
            (Path(__file__).resolve().parents[1] / "openapi.json").read_text(encoding="utf-8")
        )
        paths = specification["paths"]
        self.assertIn("/api/v2/admin/competitions", paths)
        self.assertIn("/api/v2/competitions", paths)
        self.assertIn("/api/v2/competitions/{competitionId}", paths)
        self.assertIn("/api/v2/competitions/{competitionId}/join", paths)
        self.assertIn("/api/v2/competitions/{competitionId}/submissions", paths)
        self.assertIn("/api/v2/competitions/{competitionId}/leaderboard", paths)
        submission = specification["components"]["schemas"]["CompetitionSubmissionRequest"]
        self.assertEqual(["workoutClientRecordId"], submission["required"])
        result = specification["components"]["schemas"]["CompetitionSubmissionResult"]
        self.assertIn("SERVER_RECORDED_SCORE", result["properties"]["reason"]["enum"])
        self.assertEqual(
            "SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED",
            result["properties"]["verificationLevel"]["const"],
        )
        self.assertFalse(result["properties"]["rewardEligible"]["const"])
        self.assertEqual(
            "X-THF-Competition-Admin-Key",
            paths["/api/v2/admin/competitions"]["post"]["parameters"][0]["name"],
        )

    def test_admin_rejects_non_integer_capacity(self):
        start, end = self.event_window()
        for index, invalid_capacity in enumerate((True, 2.5, "20")):
            status, body = self.request(
                "/api/v2/admin/competitions",
                method="POST",
                bearer=token("admin-user"),
                admin_key="competition-admin-secret",
                body={
                    "id": f"invalid-cap-{index}",
                    "title": "Invalid Capacity",
                    "sport": "strength_training",
                    "metric": "strength_volume_kg_reps",
                    "startsAt": start,
                    "endsAt": end,
                    "maxParticipants": invalid_capacity,
                },
            )
            self.assertEqual("422 Unprocessable Entity", status, body)

    def test_capacity_is_atomic_across_database_connections(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "competition-capacity.sqlite3"
            first_db = sqlite3.connect(database, timeout=5, check_same_thread=False)
            second_db = sqlite3.connect(database, timeout=5, check_same_thread=False)
            try:
                first = CompetitionStore(first_db)
                second = CompetitionStore(second_db)
                now = datetime.now(timezone.utc)
                first.create_competition(
                    "capacity-race",
                    "Capacity Race",
                    "strength_training",
                    "strength_volume_kg_reps",
                    (now - timedelta(hours=1)).isoformat(),
                    (now + timedelta(hours=1)).isoformat(),
                    max_participants=2,
                )
                first.join("capacity-race", "seed-user")
                barrier = threading.Barrier(2)
                results = []
                errors = []

                def attempt(store, user_id):
                    try:
                        barrier.wait()
                        results.append(store.join("capacity-race", user_id))
                    except Exception as error:
                        errors.append(error)

                threads = [
                    threading.Thread(target=attempt, args=(first, "racer-one")),
                    threading.Thread(target=attempt, args=(second, "racer-two")),
                ]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=10)
                self.assertFalse(any(thread.is_alive() for thread in threads))
                self.assertEqual([], errors)
                self.assertEqual(1, sum(1 for result in results if result.get("joined")))
                self.assertEqual(1, sum(1 for result in results if result.get("reason") == "COMPETITION_FULL"))
                count = first_db.execute(
                    "SELECT COUNT(*) FROM competition_memberships WHERE competition_id=?",
                    ("capacity-race",),
                ).fetchone()[0]
                self.assertEqual(2, count)
            finally:
                first_db.close()
                second_db.close()

    def test_duplicate_submission_is_atomic_across_database_connections(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "competition-submission.sqlite3"
            first_db = sqlite3.connect(database, timeout=5, check_same_thread=False)
            second_db = sqlite3.connect(database, timeout=5, check_same_thread=False)
            try:
                workout_store = WorkoutStore(first_db)
                first = CompetitionStore(first_db)
                second = CompetitionStore(second_db)
                now = datetime.now(timezone.utc)
                first.create_competition(
                    "submission-race",
                    "Submission Race",
                    "strength_training",
                    "strength_volume_kg_reps",
                    (now - timedelta(hours=1)).isoformat(),
                    (now + timedelta(hours=1)).isoformat(),
                )
                first.join("submission-race", "user-1")
                workout_store.sync(
                    "user-1",
                    WorkoutSession(
                        client_record_id="thf-strength-race-01",
                        client_record_version=1,
                        started_at=(now - timedelta(minutes=30)).isoformat(),
                        ended_at=(now - timedelta(minutes=20)).isoformat(),
                        sport="strength_training",
                        exercise_session_type=80,
                        source="THF_ANDROID",
                        provenance_package="com.topherofit.thf.pulse",
                        sets=(WorkoutSet("back-squat", 1, "working", 5, 50.0, 120, 8, 2),),
                    ),
                )
                barrier = threading.Barrier(2)
                results = []
                errors = []

                def attempt(store):
                    try:
                        barrier.wait()
                        results.append(store.submit_workout(
                            "submission-race", "user-1", "thf-strength-race-01"
                        ))
                    except Exception as error:
                        errors.append(error)

                threads = [
                    threading.Thread(target=attempt, args=(first,)),
                    threading.Thread(target=attempt, args=(second,)),
                ]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=10)
                self.assertFalse(any(thread.is_alive() for thread in threads))
                self.assertEqual([], errors)
                self.assertEqual(2, len(results))
                self.assertTrue(all(result.get("accepted") for result in results))
                self.assertEqual([False, True], sorted(result["duplicate"] for result in results))
                count = first_db.execute(
                    "SELECT COUNT(*) FROM competition_submissions WHERE competition_id=?",
                    ("submission-race",),
                ).fetchone()[0]
                self.assertEqual(1, count)
            finally:
                first_db.close()
                second_db.close()

    def test_score_is_server_derived_and_leaderboard_is_pseudonymous(self):
        self.create_event()
        self.sync_workout()
        joined = self.request(
            "/api/v2/competitions/strength-open/join",
            method="POST",
            bearer=token("user-1"),
        )
        self.assertEqual("200 OK", joined[0])
        submitted = self.request(
            "/api/v2/competitions/strength-open/submissions",
            method="POST",
            bearer=token("user-1"),
            body={"workoutClientRecordId": "thf-strength-0001"},
        )
        self.assertEqual("201 Created", submitted[0])
        self.assertEqual(250.0, submitted[1]["metricValue"])
        self.assertEqual("kg·reps", submitted[1]["metricUnit"])
        self.assertEqual("SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED", submitted[1]["verificationLevel"])
        self.assertFalse(submitted[1]["rewardEligible"])

        leaderboard = self.request(
            "/api/v2/competitions/strength-open/leaderboard",
            bearer=token("user-2"),
        )
        self.assertEqual("200 OK", leaderboard[0])
        self.assertEqual(1, leaderboard[1]["entries"][0]["rank"])
        self.assertEqual(250.0, leaderboard[1]["entries"][0]["metricValue"])
        self.assertTrue(leaderboard[1]["entries"][0]["participantId"].startswith("athlete-"))
        self.assertNotIn("userId", leaderboard[1]["entries"][0])
        self.assertNotIn("user-1", json.dumps(leaderboard[1]))

    def test_claimed_client_metric_is_rejected_and_membership_is_required(self):
        self.create_event()
        self.sync_workout()
        not_joined = self.request(
            "/api/v2/competitions/strength-open/submissions",
            method="POST",
            bearer=token("user-1"),
            body={"workoutClientRecordId": "thf-strength-0001"},
        )
        self.assertEqual("409 Conflict", not_joined[0])
        self.assertEqual("NOT_ENROLLED", not_joined[1]["reason"])
        self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-1"))
        claimed = self.request(
            "/api/v2/competitions/strength-open/submissions",
            method="POST",
            bearer=token("user-1"),
            body={"workoutClientRecordId": "thf-strength-0001", "claimedMetric": 999999},
        )
        self.assertEqual("422 Unprocessable Entity", claimed[0])

    def test_duplicate_submission_is_idempotent_but_mutated_workout_conflicts(self):
        self.create_event()
        self.sync_workout()
        self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-1"))
        path = "/api/v2/competitions/strength-open/submissions"
        first = self.request(path, method="POST", bearer=token("user-1"), body={"workoutClientRecordId": "thf-strength-0001"})
        duplicate = self.request(path, method="POST", bearer=token("user-1"), body={"workoutClientRecordId": "thf-strength-0001"})
        self.assertEqual("201 Created", first[0])
        self.assertEqual("201 Created", duplicate[0])
        self.assertTrue(duplicate[1]["duplicate"])
        self.sync_workout(load=60, version=2)
        changed = self.request(path, method="POST", bearer=token("user-1"), body={"workoutClientRecordId": "thf-strength-0001"})
        self.assertEqual("409 Conflict", changed[0])
        self.assertEqual("RECORD_VERSION_CONFLICT", changed[1]["error"])

    def test_admin_endpoint_fails_closed_without_configured_key(self):
        verifier = self.api.verifier
        disabled = FitnessApi(self.store, verifier, competition_admin_key="")
        original = self.api
        self.api = disabled
        try:
            status, body = self.request(
                "/api/v2/admin/competitions",
                method="POST",
                bearer=token("admin-user"),
                admin_key="any-value",
                body={
                    "id": "disabled-event",
                    "title": "Disabled",
                    "sport": "strength_training",
                    "metric": "strength_volume_kg_reps",
                    "startsAt": "2026-11-01T00:00:00Z",
                    "endsAt": "2026-11-08T00:00:00Z",
                },
            )
            self.assertEqual("503 Service Unavailable", status)
            self.assertEqual("COMPETITION_ADMIN_DISABLED", body["error"])
        finally:
            self.api = original


    def test_participant_cap_and_unsupported_activity_competitions_fail_closed(self):
        self.create_event(max_participants=2)
        first = self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-1"))
        second = self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-2"))
        third = self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-3"))
        self.assertEqual("200 OK", first[0])
        self.assertEqual("200 OK", second[0])
        self.assertEqual("409 Conflict", third[0])
        self.assertEqual("COMPETITION_FULL", third[1]["reason"])

        start, end = self.event_window()
        unsupported = self.request(
            "/api/v2/admin/competitions",
            method="POST",
            bearer=token("admin-user"),
            admin_key="competition-admin-secret",
            body={
                "id": "running-open",
                "title": "Running Open",
                "sport": "running",
                "metric": "distance_m",
                "startsAt": start,
                "endsAt": end,
            },
        )
        self.assertEqual("422 Unprocessable Entity", unsupported[0])

    def test_event_window_and_android_source_are_enforced(self):
        now = datetime.now(timezone.utc)
        start, end = self.event_window()
        self.create_event()
        self.sync_workout(
            record_id="thf-old-workout-0001",
            start=(now - timedelta(hours=4)).isoformat(),
            end=(now - timedelta(hours=3)).isoformat(),
        )
        self.sync_workout(
            record_id="thf-web-workout-0001",
            source="THF_WEB",
            provenance_package=None,
        )
        self.request("/api/v2/competitions/strength-open/join", method="POST", bearer=token("user-1"))
        outside = self.request(
            "/api/v2/competitions/strength-open/submissions",
            method="POST",
            bearer=token("user-1"),
            body={"workoutClientRecordId": "thf-old-workout-0001"},
        )
        unsupported = self.request(
            "/api/v2/competitions/strength-open/submissions",
            method="POST",
            bearer=token("user-1"),
            body={"workoutClientRecordId": "thf-web-workout-0001"},
        )
        self.assertEqual("409 Conflict", outside[0])
        self.assertEqual("WORKOUT_OUTSIDE_COMPETITION_WINDOW", outside[1]["reason"])
        self.assertEqual("409 Conflict", unsupported[0])
        self.assertEqual("UNSUPPORTED_WORKOUT_SOURCE", unsupported[1]["reason"])


    def test_missing_leaderboard_is_not_found_and_limit_is_validated(self):
        missing = self.request(
            "/api/v2/competitions/does-not-exist/leaderboard",
            bearer=token("user-1"),
        )
        self.assertEqual("404 Not Found", missing[0])
        self.create_event()
        invalid_limit = self.request(
            "/api/v2/competitions/strength-open/leaderboard",
            bearer=token("user-1"),
            query="limit=0",
        )
        self.assertEqual("422 Unprocessable Entity", invalid_limit[0])


if __name__ == "__main__":
    unittest.main()
