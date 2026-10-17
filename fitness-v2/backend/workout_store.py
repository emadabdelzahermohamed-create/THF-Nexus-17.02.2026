"""Server-authoritative workout sync core for THF Fitness V2.

The HTTP/auth adapter deliberately lives outside this module. Every call must already
carry a verified account identifier; the store never accepts user identity from a
workout payload.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
import sqlite3
from typing import Iterable


class WorkoutValidationError(ValueError):
    pass


class WorkoutConflictError(ValueError):
    """The same stable record/version was reused for different workout facts."""


@dataclass(frozen=True)
class WorkoutSet:
    exercise_id: str
    ordinal: int
    set_type: str
    reps: int
    load_kg: float = 0.0
    rest_seconds: int = 0
    rpe: float | None = None
    rir: float | None = None


@dataclass(frozen=True)
class WorkoutSession:
    client_record_id: str
    client_record_version: int
    started_at: str
    ended_at: str
    sport: str
    exercise_session_type: int
    source: str
    provenance_package: str | None = None
    sets: tuple[WorkoutSet, ...] = field(default_factory=tuple)


class WorkoutStore:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def _migrate(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                client_record_id TEXT NOT NULL,
                client_record_version INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT NOT NULL,
                sport TEXT NOT NULL,
                exercise_session_type INTEGER NOT NULL,
                source TEXT NOT NULL,
                provenance_package TEXT,
                received_at TEXT NOT NULL,
                UNIQUE(user_id, client_record_id)
            );
            CREATE TABLE IF NOT EXISTS workout_sets (
                session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
                exercise_id TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                set_type TEXT NOT NULL,
                reps INTEGER NOT NULL,
                load_kg REAL NOT NULL,
                rest_seconds INTEGER NOT NULL,
                rpe REAL,
                rir REAL,
                PRIMARY KEY(session_id, exercise_id, ordinal)
            );
            CREATE INDEX IF NOT EXISTS idx_workout_history
                ON workout_sessions(user_id, started_at DESC);
            """
        )

    @staticmethod
    def _parse_time(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise WorkoutValidationError("timestamps must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise WorkoutValidationError("timestamps must include a timezone")
        return parsed.astimezone(timezone.utc)

    @classmethod
    def validate(cls, user_id: str, session: WorkoutSession) -> None:
        if not user_id or len(user_id) > 128:
            raise WorkoutValidationError("verified user_id is required")
        if not 8 <= len(session.client_record_id) <= 120 or any(character.isspace() for character in session.client_record_id):
            raise WorkoutValidationError("invalid client_record_id")
        if session.client_record_version < 1:
            raise WorkoutValidationError("client_record_version must be positive")
        if session.source not in {"THF_ANDROID", "THF_WEB", "HEALTH_CONNECT"}:
            raise WorkoutValidationError("unsupported provenance source")
        if not isinstance(session.sport, str) or not 1 <= len(session.sport) <= 80:
            raise WorkoutValidationError("invalid sport")
        if session.exercise_session_type < 0:
            raise WorkoutValidationError("invalid exercise_session_type")
        if session.provenance_package is not None and not 1 <= len(session.provenance_package) <= 200:
            raise WorkoutValidationError("invalid provenance_package")
        if session.source == "THF_ANDROID" and session.provenance_package != "com.topherofit.thf.pulse":
            raise WorkoutValidationError("Android provenance package does not match THF Fitness")
        started_at = cls._parse_time(session.started_at)
        ended_at = cls._parse_time(session.ended_at)
        if ended_at <= started_at:
            raise WorkoutValidationError("ended_at must be after started_at")
        if (ended_at - started_at).total_seconds() > 48 * 60 * 60:
            raise WorkoutValidationError("workout duration exceeds 48 hours")
        if len(session.sets) > 1000:
            raise WorkoutValidationError("too many workout sets")
        seen: set[tuple[str, int]] = set()
        for item in session.sets:
            key = (item.exercise_id, item.ordinal)
            if key in seen:
                raise WorkoutValidationError("duplicate exercise set ordinal")
            seen.add(key)
            if (
                not 1 <= len(item.exercise_id) <= 120
                or item.ordinal < 1
                or item.reps < 0
                or item.reps > 10000
                or not math.isfinite(item.load_kg)
                or item.load_kg < 0
                or item.load_kg > 100000
                or item.rest_seconds < 0
                or item.rest_seconds > 86400
            ):
                raise WorkoutValidationError("invalid set values")
            if item.set_type not in {"warmup", "working", "drop", "failure"}:
                raise WorkoutValidationError("invalid set type")
            if item.rpe is not None and (not math.isfinite(item.rpe) or not 0 <= item.rpe <= 10):
                raise WorkoutValidationError("RPE must be between 0 and 10")
            if item.rir is not None and (not math.isfinite(item.rir) or not 0 <= item.rir <= 10):
                raise WorkoutValidationError("RIR must be between 0 and 10")

    def sync(self, user_id: str, session: WorkoutSession) -> str:
        """Insert or version-upsert a session; return inserted/updated/duplicate/stale."""
        self.validate(user_id, session)
        existing = self.db.execute(
            """SELECT id, client_record_version, started_at, ended_at, sport,
                      exercise_session_type, source, provenance_package
                 FROM workout_sessions WHERE user_id=? AND client_record_id=?""",
            (user_id, session.client_record_id),
        ).fetchone()
        if existing and existing["client_record_version"] == session.client_record_version:
            if not self._matches_existing(existing, session):
                raise WorkoutConflictError(
                    "client_record_id/version already exists with different workout facts"
                )
            return "duplicate"
        if existing and existing["client_record_version"] > session.client_record_version:
            return "stale"

        received_at = datetime.now(timezone.utc).isoformat()
        with self.db:
            if existing:
                session_id = existing["id"]
                self.db.execute(
                    """UPDATE workout_sessions SET client_record_version=?, started_at=?, ended_at=?, sport=?,
                       exercise_session_type=?, source=?, provenance_package=?, received_at=? WHERE id=?""",
                    (
                        session.client_record_version, session.started_at, session.ended_at, session.sport,
                        session.exercise_session_type, session.source, session.provenance_package, received_at, session_id,
                    ),
                )
                self.db.execute("DELETE FROM workout_sets WHERE session_id=?", (session_id,))
                outcome = "updated"
            else:
                cursor = self.db.execute(
                    """INSERT INTO workout_sessions
                       (user_id, client_record_id, client_record_version, started_at, ended_at, sport,
                        exercise_session_type, source, provenance_package, received_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, session.client_record_id, session.client_record_version, session.started_at,
                        session.ended_at, session.sport, session.exercise_session_type, session.source,
                        session.provenance_package, received_at,
                    ),
                )
                session_id = cursor.lastrowid
                outcome = "inserted"
            self.db.executemany(
                """INSERT INTO workout_sets
                   (session_id, exercise_id, ordinal, set_type, reps, load_kg, rest_seconds, rpe, rir)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (session_id, item.exercise_id, item.ordinal, item.set_type, item.reps, item.load_kg,
                     item.rest_seconds, item.rpe, item.rir)
                    for item in session.sets
                ],
            )
        return outcome

    def _matches_existing(self, existing: sqlite3.Row, session: WorkoutSession) -> bool:
        if (
            existing["started_at"] != session.started_at
            or existing["ended_at"] != session.ended_at
            or existing["sport"] != session.sport
            or existing["exercise_session_type"] != session.exercise_session_type
            or existing["source"] != session.source
            or existing["provenance_package"] != session.provenance_package
        ):
            return False
        stored = self.db.execute(
            """SELECT exercise_id, ordinal, set_type, reps, load_kg, rest_seconds, rpe, rir
                 FROM workout_sets WHERE session_id=? ORDER BY exercise_id, ordinal""",
            (existing["id"],),
        ).fetchall()
        expected = sorted(
            (
                item.exercise_id,
                item.ordinal,
                item.set_type,
                item.reps,
                item.load_kg,
                item.rest_seconds,
                item.rpe,
                item.rir,
            )
            for item in session.sets
        )
        actual = [
            (
                item["exercise_id"],
                item["ordinal"],
                item["set_type"],
                item["reps"],
                item["load_kg"],
                item["rest_seconds"],
                item["rpe"],
                item["rir"],
            )
            for item in stored
        ]
        return actual == expected

    def history(self, user_id: str, limit: int = 50) -> list[dict]:
        sessions = self.db.execute(
            """SELECT id, client_record_id, client_record_version, started_at, ended_at,
                      sport, exercise_session_type, source, provenance_package, received_at
               FROM workout_sessions WHERE user_id=? ORDER BY started_at DESC LIMIT ?""",
            (user_id, min(max(limit, 1), 200)),
        ).fetchall()
        if not sessions:
            return []
        placeholders = ",".join("?" for _ in sessions)
        set_rows = self.db.execute(
            f"""SELECT session_id, exercise_id, ordinal, set_type, reps, load_kg,
                       rest_seconds, rpe, rir FROM workout_sets
                 WHERE session_id IN ({placeholders}) ORDER BY session_id, exercise_id, ordinal""",
            tuple(row["id"] for row in sessions),
        ).fetchall()
        grouped: dict[int, list[dict]] = {row["id"]: [] for row in sessions}
        for item in set_rows:
            grouped[item["session_id"]].append(
                {
                    "exerciseId": item["exercise_id"],
                    "ordinal": item["ordinal"],
                    "setType": item["set_type"],
                    "reps": item["reps"],
                    "loadKg": item["load_kg"],
                    "restSeconds": item["rest_seconds"],
                    "rpe": item["rpe"],
                    "rir": item["rir"],
                }
            )
        result = []
        for row in sessions:
            sets = grouped[row["id"]]
            result.append(
                {
                    "clientRecordId": row["client_record_id"],
                    "clientRecordVersion": row["client_record_version"],
                    "startedAt": row["started_at"],
                    "endedAt": row["ended_at"],
                    "sport": row["sport"],
                    "exerciseSessionType": row["exercise_session_type"],
                    "source": row["source"],
                    "provenancePackage": row["provenance_package"],
                    "receivedAt": row["received_at"],
                    "volumeKg": sum(item["reps"] * item["loadKg"] for item in sets if item["setType"] != "warmup"),
                    "sets": sets,
                }
            )
        return result

    def progress_summary(self, user_id: str) -> dict:
        totals = self.db.execute(
            """SELECT COUNT(DISTINCT s.id) AS workouts,
                      COALESCE(SUM(CASE WHEN ws.set_type != 'warmup' THEN ws.reps * ws.load_kg ELSE 0 END), 0) AS volume_kg
               FROM workout_sessions s LEFT JOIN workout_sets ws ON ws.session_id=s.id WHERE s.user_id=?""",
            (user_id,),
        ).fetchone()
        prs = self.db.execute(
            """SELECT ws.exercise_id, MAX(ws.load_kg) AS max_load_kg
               FROM workout_sets ws JOIN workout_sessions s ON s.id=ws.session_id
               WHERE s.user_id=? AND ws.set_type!='warmup' GROUP BY ws.exercise_id ORDER BY ws.exercise_id""",
            (user_id,),
        ).fetchall()
        return {
            "workouts": totals["workouts"],
            "volumeKg": totals["volume_kg"],
            "personalRecords": [
                {"exerciseId": row["exercise_id"], "maxLoadKg": row["max_load_kg"]}
                for row in prs
            ],
        }

    def verify_competition_claim(self, user_id: str, client_record_id: str, claimed_volume_kg: float) -> dict:
        if not 8 <= len(client_record_id) <= 120 or not math.isfinite(claimed_volume_kg) or claimed_volume_kg < 0:
            raise WorkoutValidationError("invalid competition claim")
        row = self.db.execute(
            """SELECT COALESCE(SUM(CASE WHEN ws.set_type != 'warmup' THEN ws.reps * ws.load_kg ELSE 0 END), 0) AS volume_kg
               FROM workout_sessions s LEFT JOIN workout_sets ws ON ws.session_id=s.id
               WHERE s.user_id=? AND s.client_record_id=? GROUP BY s.id""",
            (user_id, client_record_id),
        ).fetchone()
        if row is None:
            return {"accepted": False, "reason": "WORKOUT_NOT_FOUND"}
        authoritative = float(row["volume_kg"])
        if abs(authoritative - float(claimed_volume_kg)) > 0.01:
            return {"accepted": False, "reason": "CLAIM_MISMATCH", "authoritativeVolumeKg": authoritative}
        return {
            "accepted": True,
            "reason": "SERVER_RECORD_MATCH",
            "authoritativeVolumeKg": authoritative,
            "verificationLevel": "SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED",
        }
