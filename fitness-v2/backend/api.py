"""Small production-shaped WSGI adapter for the Fitness V2 workout core.

TLS is terminated by the deployment ingress.  Requests remain fail-closed when
the WSGI environment is not HTTPS, when a token is absent/invalid/revoked, or
when an idempotency key is reused for a different payload.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
from threading import RLock
from typing import Callable, Iterable
from urllib.parse import parse_qs

from auth import AuthenticationError, HmacAccessTokenVerifier, decode_key_ring
from competition_store import CompetitionStore
from workout_store import (
    WorkoutConflictError,
    WorkoutSession,
    WorkoutSet,
    WorkoutStore,
    WorkoutValidationError,
)


MAX_BODY_BYTES = 512 * 1024
COMPETITION_ROUTE_PATH = re.compile(r"^/api/v2/competitions/([^/]+)(?:/(join|submissions|leaderboard))?$")
COMPETITION_ADMIN_PATH = "/api/v2/admin/competitions"


class IdempotencyConflict(ValueError):
    pass


class FitnessApi:
    def __init__(
        self,
        store: WorkoutStore,
        verifier: HmacAccessTokenVerifier,
        *,
        require_https: bool = True,
        competition_admin_key: str | None = None,
    ):
        self.store = store
        self.verifier = verifier
        self.require_https = require_https
        self._store_lock = RLock()
        self._migrate()
        self.competitions = CompetitionStore(store.db)
        self.competition_admin_key = competition_admin_key if competition_admin_key is not None else os.environ.get("THF_COMPETITION_ADMIN_KEY", "")

    def _migrate(self) -> None:
        self.store.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS api_idempotency (
                user_id TEXT NOT NULL,
                route TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                request_sha256 TEXT NOT NULL,
                response_json TEXT NOT NULL,
                PRIMARY KEY(user_id, route, idempotency_key)
            );
            CREATE TABLE IF NOT EXISTS revoked_sessions (
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                revoked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, session_id)
            );
            """
        )

    def is_session_revoked(self, user_id: str, session_id: str) -> bool:
        with self._store_lock:
            row = self.store.db.execute(
                "SELECT 1 FROM revoked_sessions WHERE user_id=? AND session_id=?",
                (user_id, session_id),
            ).fetchone()
        return row is not None

    @staticmethod
    def _response(start_response: Callable, status: str, payload: dict | list) -> Iterable[bytes]:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        start_response(
            status,
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-store"),
                ("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"),
                ("Strict-Transport-Security", "max-age=31536000; includeSubDomains"),
                ("X-Content-Type-Options", "nosniff"),
                ("X-Frame-Options", "DENY"),
                ("Referrer-Policy", "no-referrer"),
            ],
        )
        return [body]

    @staticmethod
    def _read_json(environ: dict) -> tuple[bytes, dict]:
        if environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower() != "application/json":
            raise WorkoutValidationError("Content-Type must be application/json")
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError as exc:
            raise WorkoutValidationError("invalid Content-Length") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise WorkoutValidationError("request body size is invalid")
        raw = environ["wsgi.input"].read(length)
        if len(raw) != length:
            raise WorkoutValidationError("incomplete request body")
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise WorkoutValidationError("invalid JSON") from exc
        if not isinstance(payload, dict):
            raise WorkoutValidationError("JSON body must be an object")
        return raw, payload

    @staticmethod
    def _session(payload: dict) -> WorkoutSession:
        allowed = {
            "clientRecordId", "clientRecordVersion", "startedAt", "endedAt", "sport",
            "exerciseSessionType", "source", "provenancePackage", "sets",
        }
        if set(payload) - allowed:
            raise WorkoutValidationError("unknown workout fields")
        try:
            sets = tuple(
                WorkoutSet(
                    exercise_id=item["exerciseId"],
                    ordinal=int(item["ordinal"]),
                    set_type=item["setType"],
                    reps=int(item["reps"]),
                    load_kg=float(item["loadKg"]),
                    rest_seconds=int(item["restSeconds"]),
                    rpe=None if item.get("rpe") is None else float(item["rpe"]),
                    rir=None if item.get("rir") is None else float(item["rir"]),
                )
                for item in payload["sets"]
            )
            return WorkoutSession(
                client_record_id=payload["clientRecordId"],
                client_record_version=int(payload["clientRecordVersion"]),
                started_at=payload["startedAt"],
                ended_at=payload["endedAt"],
                sport=payload["sport"],
                exercise_session_type=int(payload["exerciseSessionType"]),
                source=payload["source"],
                provenance_package=payload.get("provenancePackage"),
                sets=sets,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WorkoutValidationError("invalid workout shape") from exc

    def _cached_or_store(
        self,
        user_id: str,
        route: str,
        key: str,
        request_digest: str,
        response_factory: Callable[[], dict],
    ) -> dict:
        if not 8 <= len(key) <= 120 or any(character.isspace() for character in key):
            raise WorkoutValidationError("invalid Idempotency-Key")
        with self._store_lock:
            existing = self.store.db.execute(
                "SELECT request_sha256, response_json FROM api_idempotency WHERE user_id=? AND route=? AND idempotency_key=?",
                (user_id, route, key),
            ).fetchone()
            if existing:
                if existing["request_sha256"] != request_digest:
                    raise IdempotencyConflict("idempotency key already used for a different payload")
                return json.loads(existing["response_json"])
            response = response_factory()
            encoded = json.dumps(response, separators=(",", ":"), sort_keys=True)
            with self.store.db:
                self.store.db.execute(
                    "INSERT INTO api_idempotency(user_id,route,idempotency_key,request_sha256,response_json) VALUES(?,?,?,?,?)",
                    (user_id, route, key, request_digest, encoded),
                )
            return response

    def __call__(self, environ: dict, start_response: Callable) -> Iterable[bytes]:
        try:
            if self.require_https and environ.get("wsgi.url_scheme") != "https":
                return self._response(start_response, "426 Upgrade Required", {"error": "HTTPS_REQUIRED"})
            path = environ.get("PATH_INFO", "")
            method = environ.get("REQUEST_METHOD", "GET").upper()
            if path == "/healthz" and method == "GET":
                return self._response(start_response, "200 OK", {"status": "ok"})
            principal = self.verifier.verify_authorization(environ.get("HTTP_AUTHORIZATION"))

            if path == "/api/v2/workouts/sync" and method == "POST":
                raw, payload = self._read_json(environ)
                session = self._session(payload)
                key = environ.get("HTTP_IDEMPOTENCY_KEY", "")
                digest = hashlib.sha256(raw).hexdigest()

                def sync() -> dict:
                    result = self.store.sync(principal.user_id, session)
                    return {
                        "result": result,
                        "clientRecordId": session.client_record_id,
                        "serverRevision": session.client_record_version,
                    }

                response = self._cached_or_store(principal.user_id, path, key, digest, sync)
                return self._response(start_response, "200 OK", response)
            if path == "/api/v2/workouts" and method == "GET":
                query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=False)
                try:
                    limit = int(query.get("limit", ["50"])[0])
                except ValueError as exc:
                    raise WorkoutValidationError("invalid history limit") from exc
                if not 1 <= limit <= 200:
                    raise WorkoutValidationError("history limit must be between 1 and 200")
                with self._store_lock:
                    items = self.store.history(principal.user_id, limit)
                return self._response(start_response, "200 OK", {"items": items})
            if path == "/api/v2/progress/summary" and method == "GET":
                with self._store_lock:
                    summary = self.store.progress_summary(principal.user_id)
                return self._response(start_response, "200 OK", summary)
            if path == "/api/v2/competitions" and method == "GET":
                with self._store_lock:
                    items = self.competitions.list_competitions(user_id=principal.user_id)
                return self._response(start_response, "200 OK", {"items": items})
            if path == COMPETITION_ADMIN_PATH and method == "POST":
                if not self.competition_admin_key:
                    return self._response(start_response, "503 Service Unavailable", {"error": "COMPETITION_ADMIN_DISABLED"})
                supplied_key = environ.get("HTTP_X_THF_COMPETITION_ADMIN_KEY", "")
                if not hmac.compare_digest(supplied_key, self.competition_admin_key):
                    return self._response(start_response, "403 Forbidden", {"error": "ADMIN_FORBIDDEN"})
                _raw, payload = self._read_json(environ)
                required = {"id", "title", "sport", "metric", "startsAt", "endsAt"}
                allowed = required | {"maxParticipants"}
                if not required.issubset(payload) or set(payload) - allowed:
                    raise WorkoutValidationError("invalid competition definition shape")
                string_fields = ("id", "title", "sport", "metric", "startsAt", "endsAt")
                if any(not isinstance(payload[field], str) for field in string_fields):
                    raise WorkoutValidationError("competition definition fields must be strings")
                with self._store_lock:
                    competition_item = self.competitions.create_competition(
                        competition_id=payload["id"],
                        title=payload["title"],
                        sport=payload["sport"],
                        metric=payload["metric"],
                        starts_at=payload["startsAt"],
                        ends_at=payload["endsAt"],
                        max_participants=payload.get("maxParticipants", 0),
                    )
                return self._response(start_response, "201 Created", competition_item)
            competition = COMPETITION_ROUTE_PATH.match(path)
            if competition:
                competition_id, action = competition.groups()
                if action is None and method == "GET":
                    with self._store_lock:
                        item = self.competitions.get_competition(competition_id)
                    if item is None:
                        return self._response(start_response, "404 Not Found", {"error": "COMPETITION_NOT_FOUND"})
                    return self._response(start_response, "200 OK", item)
                if action == "join" and method == "POST":
                    with self._store_lock:
                        result = self.competitions.join(competition_id, principal.user_id)
                    status = "200 OK" if result.get("joined") else "409 Conflict"
                    return self._response(start_response, status, result)
                if action == "submissions" and method == "POST":
                    _raw, payload = self._read_json(environ)
                    if set(payload) != {"workoutClientRecordId"}:
                        raise WorkoutValidationError("competition submission accepts only workoutClientRecordId")
                    with self._store_lock:
                        result = self.competitions.submit_workout(
                            competition_id,
                            principal.user_id,
                            str(payload["workoutClientRecordId"]),
                        )
                    status = "201 Created" if result.get("accepted") else "409 Conflict"
                    result["competitionId"] = competition_id
                    return self._response(start_response, status, result)
                if action == "leaderboard" and method == "GET":
                    query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=False)
                    try:
                        limit = int(query.get("limit", ["50"])[0])
                    except ValueError as exc:
                        raise WorkoutValidationError("invalid leaderboard limit") from exc
                    with self._store_lock:
                        exists = self.competitions.get_competition(competition_id)
                        if exists is None:
                            return self._response(start_response, "404 Not Found", {"error": "COMPETITION_NOT_FOUND"})
                        result = self.competitions.leaderboard(competition_id, limit=limit)
                    return self._response(start_response, "200 OK", result)
            return self._response(start_response, "404 Not Found", {"error": "NOT_FOUND"})
        except AuthenticationError:
            return self._response(start_response, "401 Unauthorized", {"error": "UNAUTHORIZED"})
        except IdempotencyConflict as error:
            return self._response(start_response, "409 Conflict", {"error": "IDEMPOTENCY_CONFLICT", "detail": str(error)})
        except WorkoutConflictError as error:
            return self._response(start_response, "409 Conflict", {"error": "RECORD_VERSION_CONFLICT", "detail": str(error)})
        except (WorkoutValidationError, ValueError) as error:
            return self._response(start_response, "422 Unprocessable Entity", {"error": "INVALID_REQUEST", "detail": str(error)})
        except Exception:
            return self._response(start_response, "500 Internal Server Error", {"error": "INTERNAL_ERROR"})


def create_app_from_environment() -> FitnessApi:
    """Create the production adapter without insecure configuration defaults."""
    database_path = os.environ.get("THF_WORKOUT_DB")
    issuer = os.environ.get("THF_AUTH_ISSUER")
    audience = os.environ.get("THF_AUTH_AUDIENCE")
    keys_json = os.environ.get("THF_AUTH_KEYS_JSON")
    if not database_path or not issuer or not audience or not keys_json:
        raise RuntimeError("THF_WORKOUT_DB, THF_AUTH_ISSUER, THF_AUTH_AUDIENCE and THF_AUTH_KEYS_JSON are required")
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    store = WorkoutStore(sqlite3.connect(database_path, check_same_thread=False))
    api: FitnessApi
    verifier = HmacAccessTokenVerifier(
        decode_key_ring(keys_json),
        issuer,
        audience,
        is_session_revoked=lambda user_id, session_id: api.is_session_revoked(user_id, session_id),
    )
    api = FitnessApi(store, verifier, require_https=True)
    return api
