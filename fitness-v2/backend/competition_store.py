"""Server-owned competition enrollment, scoring and leaderboard state.

Only strength-training volume is currently scoreable. The metric is kg-reps
(repetitions multiplied by load in kg), not kilograms or a medical measurement.
All scores remain server-recorded, not physically verified, and are ineligible
for THF/token rewards until a separate physical-provenance gate exists.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import math
import re
import sqlite3

from workout_store import WorkoutConflictError, WorkoutValidationError


COMPETITION_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,119}$")
SUPPORTED_SPORT = "strength_training"
SUPPORTED_METRIC = "strength_volume_kg_reps"
VERIFICATION_LEVEL = "SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED"


class CompetitionStore:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def _migrate(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS competitions (
                competition_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                sport TEXT NOT NULL,
                metric TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                ends_at TEXT NOT NULL,
                max_participants INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS competition_memberships (
                competition_id TEXT NOT NULL REFERENCES competitions(competition_id) ON DELETE CASCADE,
                user_id TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                PRIMARY KEY (competition_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS competition_submissions (
                competition_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                workout_client_record_id TEXT NOT NULL,
                workout_version INTEGER NOT NULL,
                metric_value REAL NOT NULL,
                submitted_at TEXT NOT NULL,
                verification_level TEXT NOT NULL,
                PRIMARY KEY (competition_id, user_id, workout_client_record_id),
                FOREIGN KEY (competition_id, user_id)
                    REFERENCES competition_memberships(competition_id, user_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_competition_leaderboard
                ON competition_submissions(competition_id, metric_value DESC, submitted_at ASC);
            """
        )

    @staticmethod
    def _parse_time(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as exc:
            raise WorkoutValidationError("competition timestamps must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise WorkoutValidationError("competition timestamps must include a timezone")
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _now(value: datetime | None = None) -> datetime:
        current = value or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise WorkoutValidationError("competition clock must include a timezone")
        return current.astimezone(timezone.utc)

    @staticmethod
    def _iso(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @classmethod
    def _status(cls, starts_at: str, ends_at: str, now: datetime) -> str:
        start = cls._parse_time(starts_at)
        end = cls._parse_time(ends_at)
        if now < start:
            return "scheduled"
        if now < end:
            return "active"
        return "completed"

    def create_competition(
        self,
        competition_id: str,
        title: str,
        sport: str,
        metric: str,
        starts_at: str,
        ends_at: str,
        max_participants: int = 0,
        now: datetime | None = None,
    ) -> dict:
        if not isinstance(competition_id, str):
            raise WorkoutValidationError("competition id must be a string")
        if not isinstance(title, str):
            raise WorkoutValidationError("competition title must be a string")
        if not isinstance(sport, str) or not isinstance(metric, str):
            raise WorkoutValidationError("competition sport and metric must be strings")
        if not isinstance(starts_at, str) or not isinstance(ends_at, str):
            raise WorkoutValidationError("competition timestamps must be strings")
        identifier = competition_id.strip().lower()
        name = title.strip()
        if not COMPETITION_ID.fullmatch(identifier):
            raise WorkoutValidationError("invalid competition id")
        if not 1 <= len(name) <= 160:
            raise WorkoutValidationError("competition title must be between 1 and 160 characters")
        if sport != SUPPORTED_SPORT or metric != SUPPORTED_METRIC:
            raise WorkoutValidationError("unsupported competition sport or metric")
        start = self._parse_time(starts_at)
        end = self._parse_time(ends_at)
        if end <= start:
            raise WorkoutValidationError("competition end must be after start")
        if isinstance(max_participants, bool) or not isinstance(max_participants, int):
            raise WorkoutValidationError("max_participants must be an integer")
        if max_participants != 0 and not 2 <= max_participants <= 100000:
            raise WorkoutValidationError("max_participants must be zero or between 2 and 100000")
        created_at = self._iso(self._now(now))
        try:
            with self.db:
                self.db.execute(
                    """INSERT INTO competitions
                       (competition_id, title, sport, metric, starts_at, ends_at, max_participants, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        identifier, name, sport, metric, self._iso(start), self._iso(end),
                        max_participants, created_at,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise WorkoutConflictError("competition id already exists") from exc
        result = self.get_competition(identifier, now=now)
        assert result is not None
        return result

    def get_competition(self, competition_id: str, now: datetime | None = None) -> dict | None:
        row = self.db.execute(
            """SELECT c.*,
                      (SELECT COUNT(*) FROM competition_memberships m
                       WHERE m.competition_id=c.competition_id) AS participant_count
               FROM competitions c WHERE c.competition_id=?""",
            (competition_id,),
        ).fetchone()
        if row is None:
            return None
        current = self._now(now)
        return {
            "id": row["competition_id"],
            "title": row["title"],
            "sport": row["sport"],
            "metric": row["metric"],
            "metricUnit": "kg·reps",
            "startsAt": row["starts_at"],
            "endsAt": row["ends_at"],
            "status": self._status(row["starts_at"], row["ends_at"], current),
            "maxParticipants": row["max_participants"],
            "participantCount": row["participant_count"],
            "verificationLevel": VERIFICATION_LEVEL,
            "rewardEligible": False,
        }

    def list_competitions(self, user_id: str | None = None, now: datetime | None = None) -> list[dict]:
        rows = self.db.execute(
            """SELECT c.*,
                      (SELECT COUNT(*) FROM competition_memberships m
                       WHERE m.competition_id=c.competition_id) AS participant_count
               FROM competitions c ORDER BY c.starts_at ASC, c.competition_id ASC"""
        ).fetchall()
        current = self._now(now)
        items = []
        for row in rows:
            item = self.get_competition(row["competition_id"], now=current)
            if item is None:
                continue
            if user_id is not None:
                joined = self.db.execute(
                    """SELECT 1 FROM competition_memberships
                       WHERE competition_id=? AND user_id=?""",
                    (row["competition_id"], user_id),
                ).fetchone()
                item["joined"] = joined is not None
            items.append(item)
        return items

    def join(self, competition_id: str, user_id: str, now: datetime | None = None) -> dict:
        # Serialize capacity checks across workers, not just threads in one WSGI process.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if not user_id or len(user_id) > 128:
                raise WorkoutValidationError("verified user_id is required")
            competition = self.get_competition(competition_id, now=now)
            if competition is None:
                raise WorkoutValidationError("competition not found")
            if competition["status"] == "completed":
                return {"joined": False, "reason": "COMPETITION_ENDED"}
            existing = self.db.execute(
                """SELECT 1 FROM competition_memberships
                   WHERE competition_id=? AND user_id=?""",
                (competition_id, user_id),
            ).fetchone()
            if existing is not None:
                return {"joined": True, "alreadyJoined": True, "competitionId": competition_id}
            maximum = int(competition["maxParticipants"])
            if maximum:
                count = int(competition["participantCount"])
                if count >= maximum:
                    return {"joined": False, "reason": "COMPETITION_FULL"}
            joined_at = self._iso(self._now(now))
            self.db.execute(
                """INSERT INTO competition_memberships(competition_id, user_id, joined_at)
                   VALUES (?, ?, ?)""",
                (competition_id, user_id, joined_at),
            )
            return {"joined": True, "alreadyJoined": False, "competitionId": competition_id}

    def submit_workout(
        self,
        competition_id: str,
        user_id: str,
        client_record_id: str,
        now: datetime | None = None,
    ) -> dict:
        # Lock before reading the workout and submission ledger so concurrent
        # retries observe one immutable score snapshot instead of racing inserts.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if not 8 <= len(client_record_id) <= 120 or any(character.isspace() for character in client_record_id):
                raise WorkoutValidationError("invalid workout client record id")
            competition = self.get_competition(competition_id, now=now)
            if competition is None:
                raise WorkoutValidationError("competition not found")
            if competition["status"] != "active":
                return {"accepted": False, "reason": "COMPETITION_NOT_ACTIVE"}
            member = self.db.execute(
                """SELECT 1 FROM competition_memberships
                   WHERE competition_id=? AND user_id=?""",
                (competition_id, user_id),
            ).fetchone()
            if member is None:
                return {"accepted": False, "reason": "NOT_ENROLLED"}

            row = self.db.execute(
                """SELECT s.id, s.client_record_version, s.started_at, s.ended_at, s.sport,
                          s.source, s.provenance_package,
                          COALESCE(SUM(CASE WHEN ws.set_type != 'warmup'
                                            THEN ws.reps * ws.load_kg ELSE 0 END), 0) AS metric_value
                   FROM workout_sessions s
                   LEFT JOIN workout_sets ws ON ws.session_id=s.id
                   WHERE s.user_id=? AND s.client_record_id=?
                   GROUP BY s.id""",
                (user_id, client_record_id),
            ).fetchone()
            if row is None:
                return {"accepted": False, "reason": "WORKOUT_NOT_FOUND"}
            if row["sport"] != competition["sport"]:
                return {"accepted": False, "reason": "SPORT_MISMATCH"}
            if row["source"] != "THF_ANDROID" or row["provenance_package"] != "com.topherofit.thf.pulse":
                return {"accepted": False, "reason": "UNSUPPORTED_WORKOUT_SOURCE"}

            start = self._parse_time(row["started_at"])
            end = self._parse_time(row["ended_at"])
            event_start = self._parse_time(competition["startsAt"])
            event_end = self._parse_time(competition["endsAt"])
            current = self._now(now)
            if start < event_start or end > event_end or end > current:
                return {"accepted": False, "reason": "WORKOUT_OUTSIDE_COMPETITION_WINDOW"}
            metric_value = float(row["metric_value"])
            if not math.isfinite(metric_value) or metric_value <= 0:
                return {"accepted": False, "reason": "NO_SCOREABLE_WORKING_VOLUME"}

            existing = self.db.execute(
                """SELECT workout_version, metric_value, verification_level
                   FROM competition_submissions
                   WHERE competition_id=? AND user_id=? AND workout_client_record_id=?""",
                (competition_id, user_id, client_record_id),
            ).fetchone()
            if existing is not None:
                if (
                    int(existing["workout_version"]) == int(row["client_record_version"])
                    and abs(float(existing["metric_value"]) - metric_value) <= 0.0001
                ):
                    return {
                        "accepted": True,
                        "duplicate": True,
                        "reason": "ALREADY_RECORDED",
                        "metric": competition["metric"],
                        "metricValue": float(existing["metric_value"]),
                        "metricUnit": "kg·reps",
                        "verificationLevel": VERIFICATION_LEVEL,
                        "rewardEligible": False,
                    }
                raise WorkoutConflictError("submitted workout changed after competition scoring")

            submitted_at = self._iso(current)
            self.db.execute(
                """INSERT INTO competition_submissions
                   (competition_id, user_id, workout_client_record_id, workout_version,
                    metric_value, submitted_at, verification_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    competition_id, user_id, client_record_id, int(row["client_record_version"]),
                    metric_value, submitted_at, VERIFICATION_LEVEL,
                ),
            )
            return {
                "accepted": True,
                "duplicate": False,
                "reason": "SERVER_RECORDED_SCORE",
                "metric": competition["metric"],
                "metricValue": metric_value,
                "metricUnit": "kg·reps",
                "verificationLevel": VERIFICATION_LEVEL,
                "rewardEligible": False,
            }

    def leaderboard(self, competition_id: str, limit: int = 50, now: datetime | None = None) -> dict:
        competition = self.get_competition(competition_id, now=now)
        if competition is None:
            raise WorkoutValidationError("competition not found")
        if not 1 <= limit <= 100:
            raise WorkoutValidationError("leaderboard limit must be between 1 and 100")
        rows = self.db.execute(
            """SELECT user_id, SUM(metric_value) AS total_metric,
                      COUNT(*) AS submissions, MIN(submitted_at) AS first_submission
               FROM competition_submissions
               WHERE competition_id=?
               GROUP BY user_id
               ORDER BY total_metric DESC, first_submission ASC, user_id ASC
               LIMIT ?""",
            (competition_id, limit),
        ).fetchall()
        entries = []
        for index, row in enumerate(rows, start=1):
            digest = hashlib.sha256(
                f"{competition_id}:{row['user_id']}".encode("utf-8")
            ).hexdigest()[:12]
            entries.append({
                "rank": index,
                "participantId": f"athlete-{digest}",
                "metricValue": float(row["total_metric"]),
                "metricUnit": "kg·reps",
                "submissionCount": int(row["submissions"]),
                "verificationLevel": VERIFICATION_LEVEL,
                "rewardEligible": False,
            })
        return {
            "competition": competition,
            "metric": competition["metric"],
            "entries": entries,
            "rewardEligible": False,
        }
