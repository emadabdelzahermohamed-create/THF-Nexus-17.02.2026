import base64
from io import BytesIO
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api import FitnessApi
from auth import HmacAccessTokenVerifier
from workout_store import WorkoutStore


NOW = 1_791_000_000
KEY = b"k" * 32


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def token(user="user-1", session="session-0001", expires=NOW + 300, kid="primary", key=KEY, **extra_claims):
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT", "kid": kid}, separators=(",", ":")).encode())
    claims = {
        "iss": "https://accounts.topherofit.com",
        "aud": "fitness-v2",
        "sub": user,
        "sid": session,
        "iat": NOW - 10,
        "exp": expires,
    }
    claims.update(extra_claims)
    payload = b64(json.dumps(claims, separators=(",", ":")).encode())
    signature = b64(hmac.new(key, f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def workout(client="thf-workout-http-0001", version=1, load=50):
    return {
        "clientRecordId": client,
        "clientRecordVersion": version,
        "startedAt": "2026-10-02T04:00:00Z",
        "endedAt": "2026-10-02T04:30:00Z",
        "sport": "strength_training",
        "exerciseSessionType": 80,
        "source": "THF_ANDROID",
        "provenancePackage": "com.topherofit.thf.pulse",
        "sets": [{
            "exerciseId": "back-squat", "ordinal": 1, "setType": "working",
            "reps": 5, "loadKg": load, "restSeconds": 120, "rpe": 8, "rir": 2,
        }],
    }


class FitnessApiTest(unittest.TestCase):
    def setUp(self):
        store = WorkoutStore(sqlite3.connect(":memory:"))
        self.api = None
        verifier = HmacAccessTokenVerifier(
            {"primary": KEY},
            "https://accounts.topherofit.com",
            "fitness-v2",
            now=lambda: NOW,
            is_session_revoked=lambda user, session: self.api.is_session_revoked(user, session),
        )
        self.api = FitnessApi(store, verifier)

    def request(self, path, method="GET", body=None, bearer=None, idempotency=None, scheme="https"):
        raw = b"" if body is None else json.dumps(body, separators=(",", ":")).encode()
        environ = {
            "PATH_INFO": path,
            "REQUEST_METHOD": method,
            "QUERY_STRING": "",
            "wsgi.url_scheme": scheme,
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": str(len(raw)),
            "CONTENT_TYPE": "application/json" if body is not None else "",
        }
        if bearer:
            environ["HTTP_AUTHORIZATION"] = f"Bearer {bearer}"
        if idempotency:
            environ["HTTP_IDEMPOTENCY_KEY"] = idempotency
        captured = {}
        result = self.api(environ, lambda status, headers: captured.update(status=status, headers=dict(headers)))
        return captured["status"], json.loads(b"".join(result)), captured["headers"]

    def test_requires_https_and_authenticated_unexpired_session(self):
        self.assertEqual("426 Upgrade Required", self.request("/api/v2/workouts", bearer=token(), scheme="http")[0])
        unauthorized = self.request("/api/v2/workouts")
        self.assertEqual("401 Unauthorized", unauthorized[0])
        self.assertEqual({"error": "UNAUTHORIZED"}, unauthorized[1])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(expires=NOW - 100))[0])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(key=b"x" * 32))[0])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(kid="unknown"))[0])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(nbf="invalid"))[0])
        self.assertEqual("DENY", unauthorized[2]["X-Frame-Options"])
        self.assertIn("max-age=31536000", unauthorized[2]["Strict-Transport-Security"])
        self.api.store.db.execute(
            "INSERT INTO revoked_sessions(user_id,session_id) VALUES(?,?)", ("user-1", "session-0001"),
        )
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token())[0])

    def test_idempotency_is_stable_and_conflicts_fail_closed(self):
        first = self.request(
            "/api/v2/workouts/sync", "POST", workout(), token(), "request-0001",
        )
        second = self.request(
            "/api/v2/workouts/sync", "POST", workout(), token(), "request-0001",
        )
        conflict = self.request(
            "/api/v2/workouts/sync", "POST", workout(load=60), token(), "request-0001",
        )
        self.assertEqual("200 OK", first[0])
        self.assertEqual(first[:2], second[:2])
        self.assertEqual("inserted", first[1]["result"])
        self.assertEqual("409 Conflict", conflict[0])

        record_conflict = self.request(
            "/api/v2/workouts/sync", "POST", workout(load=60), token(), "request-0002",
        )
        self.assertEqual("409 Conflict", record_conflict[0])
        self.assertEqual("RECORD_VERSION_CONFLICT", record_conflict[1]["error"])

    def test_account_history_and_progress_are_isolated(self):
        self.request("/api/v2/workouts/sync", "POST", workout(), token("user-1"), "request-0001")
        history = self.request("/api/v2/workouts", bearer=token("user-1"))
        other = self.request("/api/v2/workouts", bearer=token("user-2", "session-0002"))
        progress = self.request("/api/v2/progress/summary", bearer=token("user-1"))
        self.assertEqual(1, len(history[1]["items"]))
        self.assertEqual("thf-workout-http-0001", history[1]["items"][0]["clientRecordId"])
        self.assertEqual(1, len(history[1]["items"][0]["sets"]))
        self.assertEqual(120, history[1]["items"][0]["sets"][0]["restSeconds"])
        self.assertEqual([], other[1]["items"])
        self.assertEqual(250, progress[1]["volumeKg"])
        self.assertEqual(50, progress[1]["personalRecords"][0]["maxLoadKg"])

    def test_client_identity_fields_and_unknown_contract_fields_are_rejected(self):
        body = workout()
        body["userId"] = "victim"
        status, response, _headers = self.request(
            "/api/v2/workouts/sync", "POST", body, token("attacker"), "request-0002",
        )
        self.assertEqual("422 Unprocessable Entity", status)
        self.assertEqual("INVALID_REQUEST", response["error"])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(user="bad user"))[0])
        self.assertEqual("401 Unauthorized", self.request("/api/v2/workouts", bearer=token(session="bad session"))[0])

    def test_history_limit_and_competition_contract_fail_closed(self):
        # QUERY_STRING is supplied separately by the WSGI server; exercise it directly.
        raw = b""
        captured = {}
        environ = {
            "PATH_INFO": "/api/v2/workouts",
            "REQUEST_METHOD": "GET",
            "QUERY_STRING": "limit=201",
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(raw),
            "CONTENT_LENGTH": "0",
            "CONTENT_TYPE": "",
            "HTTP_AUTHORIZATION": f"Bearer {token()}",
        }
        response = self.api(environ, lambda status, headers: captured.update(status=status, headers=dict(headers)))
        self.assertEqual("422 Unprocessable Entity", captured["status"])
        self.assertEqual("INVALID_REQUEST", json.loads(b"".join(response))["error"])
        invalid = self.request(
            "/api/v2/competitions/autumn/submissions",
            "POST",
            {"workoutClientRecordId": "missing", "claimedMetric": 0, "userId": "victim"},
            token(),
        )
        self.assertEqual("422 Unprocessable Entity", invalid[0])


if __name__ == "__main__":
    unittest.main()
