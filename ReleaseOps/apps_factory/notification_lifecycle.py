#!/usr/bin/env python3
"""Provider-neutral THF notification token lifecycle candidate.

This module deliberately does not implement provider delivery and therefore cannot
establish PUSH_READY. It implements the server-side registration/rotation/revocation
semantics needed before a provider adapter is attached.

Raw provider tokens are never written to the registry database. A SecureTokenVault
implementation owns token custody. Registrations are bound to the authenticated THF
Pass subject + session + locked package so one device/session cannot mutate another.
Legacy rows without a session binding are migrated fail-closed and cannot be used by
an authenticated session.

Vault deletion is durability-tracked. If a provider secret cannot be deleted after a
registration is made inactive, only the opaque token_id is journaled for retry; raw
provider credentials and fingerprints are never copied into the cleanup journal.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import sqlite3
import time
from typing import Protocol

ALLOWED_PACKAGES = {
    "com.topherofit.thf.pulse",
    "com.topherofit.thf.forge",
    "com.topherofit.thf.echo",
    "com.topherofit.thf.codex",
    "com.topherofit.thf.spark",
    "com.topherofit.thf.rush",
    "com.topherofit.thf.vault",
    "com.topherofit.thf.signal",
    "com.topherofit.thf.command",
}
ALLOWED_PROVIDERS = {"fcm", "apns", "test"}
LEGACY_UNBOUND_SESSION = "__legacy_unbound__"


class SecureTokenVault(Protocol):
    """Opaque token custody boundary. Production implementations must encrypt at rest."""

    def put(self, token_id: str, raw_token: str) -> None: ...
    def get(self, token_id: str) -> str: ...
    def delete(self, token_id: str) -> None: ...


@dataclass(frozen=True)
class Registration:
    token_id: str
    subject: str
    session_id: str
    package: str
    provider: str
    fingerprint: str
    generation: int
    active: bool


def _fingerprint(raw_token: str) -> str:
    if not raw_token or len(raw_token.strip()) < 8:
        raise ValueError("provider token is missing or implausibly short")
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _token_id(*, subject: str, session_id: str, package: str, provider: str, fingerprint: str) -> str:
    return hashlib.sha256(
        f"{subject}\0{session_id}\0{package}\0{provider}\0{fingerprint}".encode()
    ).hexdigest()


class NotificationTokenRegistry:
    _CREATE_TABLE_SQL = """
        CREATE TABLE notification_tokens (
          token_id TEXT PRIMARY KEY,
          subject TEXT NOT NULL,
          session_id TEXT NOT NULL,
          package TEXT NOT NULL,
          provider TEXT NOT NULL,
          fingerprint TEXT NOT NULL,
          generation INTEGER NOT NULL,
          active INTEGER NOT NULL,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL,
          UNIQUE(subject, session_id, package, provider, fingerprint)
        )
    """
    _CREATE_CLEANUP_SQL = """
        CREATE TABLE IF NOT EXISTS notification_token_cleanup (
          token_id TEXT PRIMARY KEY,
          queued_at INTEGER NOT NULL,
          last_attempt_at INTEGER,
          attempts INTEGER NOT NULL DEFAULT 0,
          last_error TEXT
        )
    """

    def __init__(self, db: sqlite3.Connection, vault: SecureTokenVault):
        self.db = db
        self.vault = vault
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        exists = self.db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='notification_tokens'"
        ).fetchone()
        if not exists:
            self.db.execute(self._CREATE_TABLE_SQL)
            self.db.commit()
        else:
            columns = {row[1] for row in self.db.execute("PRAGMA table_info(notification_tokens)")}
            if "session_id" not in columns:
                with self.db:
                    self.db.execute("ALTER TABLE notification_tokens RENAME TO notification_tokens_legacy")
                    self.db.execute(self._CREATE_TABLE_SQL)
                    self.db.execute(
                        """
                        INSERT INTO notification_tokens(
                          token_id,subject,session_id,package,provider,fingerprint,
                          generation,active,created_at,updated_at
                        )
                        SELECT token_id,subject,?,package,provider,fingerprint,
                               generation,active,created_at,updated_at
                        FROM notification_tokens_legacy
                        """,
                        (LEGACY_UNBOUND_SESSION,),
                    )
                    self.db.execute("DROP TABLE notification_tokens_legacy")
        self.db.execute(self._CREATE_CLEANUP_SQL)
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_notification_tokens_subject_session "
            "ON notification_tokens(subject, session_id, package, active)"
        )
        self.db.commit()

    @staticmethod
    def _validate_identity(subject: str, session_id: str, package: str, provider: str) -> None:
        if not subject or not subject.strip():
            raise PermissionError("authenticated subject required")
        if not session_id or not session_id.strip() or session_id == LEGACY_UNBOUND_SESSION:
            raise PermissionError("authenticated THF Pass session required")
        if package not in ALLOWED_PACKAGES:
            raise PermissionError("package is not in the locked THF allowlist")
        if provider not in ALLOWED_PROVIDERS:
            raise ValueError("unsupported provider")

    def _queue_cleanup(self, token_id: str, error: Exception | str) -> None:
        now = int(time.time())
        message = str(error)
        if len(message) > 240:
            message = message[:240]
        self.db.execute(
            """
            INSERT INTO notification_token_cleanup(token_id,queued_at,last_attempt_at,attempts,last_error)
            VALUES(?,?,?,1,?)
            ON CONFLICT(token_id) DO UPDATE SET
              last_attempt_at=excluded.last_attempt_at,
              attempts=notification_token_cleanup.attempts+1,
              last_error=excluded.last_error
            """,
            (token_id, now, now, message),
        )
        self.db.commit()

    def _delete_vault_or_queue(self, token_id: str) -> bool:
        try:
            self.vault.delete(token_id)
        except Exception as exc:
            self._queue_cleanup(token_id, exc)
            return False
        self.db.execute("DELETE FROM notification_token_cleanup WHERE token_id=?", (token_id,))
        self.db.commit()
        return True

    def pending_vault_cleanup_count(self) -> int:
        return int(self.db.execute("SELECT COUNT(*) FROM notification_token_cleanup").fetchone()[0])

    def drain_vault_cleanup(self, *, limit: int = 100) -> tuple[int, int]:
        """Retry deletion of orphaned inactive secrets without deleting active tokens."""
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValueError("cleanup limit must be between 1 and 1000")
        token_ids = [
            row[0]
            for row in self.db.execute(
                "SELECT token_id FROM notification_token_cleanup ORDER BY queued_at, token_id LIMIT ?",
                (limit,),
            ).fetchall()
        ]
        cleared = failed = 0
        for token_id in token_ids:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                active = self.db.execute(
                    "SELECT active FROM notification_tokens WHERE token_id=?", (token_id,)
                ).fetchone()
                if active is not None and bool(active[0]):
                    self.db.execute("DELETE FROM notification_token_cleanup WHERE token_id=?", (token_id,))
                    self.db.commit()
                    cleared += 1
                    continue
                try:
                    self.vault.delete(token_id)
                except Exception as exc:
                    now = int(time.time())
                    self.db.execute(
                        """
                        UPDATE notification_token_cleanup
                        SET last_attempt_at=?, attempts=attempts+1, last_error=?
                        WHERE token_id=?
                        """,
                        (now, str(exc)[:240], token_id),
                    )
                    self.db.commit()
                    failed += 1
                    continue
                self.db.execute("DELETE FROM notification_token_cleanup WHERE token_id=?", (token_id,))
                self.db.commit()
                cleared += 1
            except Exception:
                self.db.rollback()
                raise
        return cleared, failed

    def register(
        self, *, subject: str, session_id: str, package: str, provider: str, raw_token: str
    ) -> Registration:
        self._validate_identity(subject, session_id, package, provider)
        fp = _fingerprint(raw_token)
        now = int(time.time())
        token_id = _token_id(
            subject=subject, session_id=session_id, package=package, provider=provider, fingerprint=fp
        )
        row = self.db.execute(
            "SELECT generation, active FROM notification_tokens WHERE token_id=?", (token_id,)
        ).fetchone()
        generation = int(row[0]) if row else 1

        self.db.execute("BEGIN IMMEDIATE")
        vault_written = False
        try:
            self.db.execute("DELETE FROM notification_token_cleanup WHERE token_id=?", (token_id,))
            self.vault.put(token_id, raw_token)
            vault_written = True
            self.db.execute(
                """
                INSERT INTO notification_tokens(
                  token_id,subject,session_id,package,provider,fingerprint,generation,active,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,1,?,?)
                ON CONFLICT(token_id) DO UPDATE SET active=1, updated_at=excluded.updated_at
                """,
                (token_id, subject, session_id, package, provider, fp, generation, now, now),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            if vault_written:
                self._delete_vault_or_queue(token_id)
            raise
        return self.get(token_id, subject=subject, session_id=session_id)

    def rotate(
        self,
        *,
        subject: str,
        session_id: str,
        package: str,
        provider: str,
        old_token_id: str,
        new_raw_token: str,
    ) -> Registration:
        self._validate_identity(subject, session_id, package, provider)
        old = self.get(old_token_id, subject=subject, session_id=session_id)
        if not old.active or old.package != package or old.provider != provider:
            raise PermissionError("rotation source is inactive or outside authenticated scope")
        new_fp = _fingerprint(new_raw_token)
        new_token_id = _token_id(
            subject=subject, session_id=session_id, package=package, provider=provider, fingerprint=new_fp
        )
        if new_token_id == old_token_id:
            raise ValueError("new provider token must differ from rotation source")
        existing_new = self.db.execute(
            "SELECT active FROM notification_tokens WHERE token_id=?", (new_token_id,)
        ).fetchone()
        if existing_new is not None and bool(existing_new[0]):
            raise ValueError("rotation destination is already active")

        next_generation = old.generation + 1
        now = int(time.time())
        self.db.execute("BEGIN IMMEDIATE")
        vault_written = False
        try:
            self.db.execute("DELETE FROM notification_token_cleanup WHERE token_id=?", (new_token_id,))
            self.vault.put(new_token_id, new_raw_token)
            vault_written = True
            self.db.execute(
                "UPDATE notification_tokens SET active=0, updated_at=? "
                "WHERE token_id=? AND subject=? AND session_id=? AND active=1",
                (now, old_token_id, subject, session_id),
            )
            if self.db.execute("SELECT changes()").fetchone()[0] != 1:
                raise PermissionError("rotation source changed before commit")
            self.db.execute(
                """
                INSERT INTO notification_tokens(
                  token_id,subject,session_id,package,provider,fingerprint,generation,active,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,1,?,?)
                ON CONFLICT(token_id) DO UPDATE SET generation=excluded.generation, active=1, updated_at=excluded.updated_at
                """,
                (new_token_id, subject, session_id, package, provider, new_fp, next_generation, now, now),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            if vault_written:
                self._delete_vault_or_queue(new_token_id)
            raise

        self._delete_vault_or_queue(old_token_id)
        return self.get(new_token_id, subject=subject, session_id=session_id)

    def revoke(self, *, token_id: str, subject: str, session_id: str) -> None:
        reg = self.get(token_id, subject=subject, session_id=session_id)
        if reg.active:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                self.db.execute(
                    "UPDATE notification_tokens SET active=0, updated_at=? "
                    "WHERE token_id=? AND subject=? AND session_id=? AND active=1",
                    (int(time.time()), token_id, subject, session_id),
                )
                if self.db.execute("SELECT changes()").fetchone()[0] != 1:
                    raise PermissionError("notification registration changed before revoke commit")
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            self._delete_vault_or_queue(token_id)

    def revoke_logout(self, *, subject: str, session_id: str, package: str) -> int:
        if package not in ALLOWED_PACKAGES:
            raise PermissionError("package is not in the locked THF allowlist")
        if not session_id or not session_id.strip() or session_id == LEGACY_UNBOUND_SESSION:
            raise PermissionError("authenticated THF Pass session required")
        rows = self.db.execute(
            "SELECT token_id FROM notification_tokens "
            "WHERE subject=? AND session_id=? AND package=? AND active=1",
            (subject, session_id, package),
        ).fetchall()
        for (token_id,) in rows:
            self.revoke(token_id=token_id, subject=subject, session_id=session_id)
        return len(rows)

    def get(self, token_id: str, *, subject: str, session_id: str) -> Registration:
        row = self.db.execute(
            """
            SELECT token_id,subject,session_id,package,provider,fingerprint,generation,active
            FROM notification_tokens WHERE token_id=? AND subject=? AND session_id=?
            """,
            (token_id, subject, session_id),
        ).fetchone()
        if not row:
            raise PermissionError("notification token is outside authenticated session scope")
        return Registration(
            token_id=row[0], subject=row[1], session_id=row[2], package=row[3], provider=row[4],
            fingerprint=row[5], generation=int(row[6]), active=bool(row[7])
        )
