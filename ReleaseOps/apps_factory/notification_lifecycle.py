#!/usr/bin/env python3
"""Provider-neutral THF notification token lifecycle candidate.

This module deliberately does not implement provider delivery and therefore cannot
establish PUSH_READY. It implements the server-side registration/rotation/revocation
semantics needed before a provider adapter is attached.

Raw provider tokens are never written to the registry database. A SecureTokenVault
implementation owns token custody. The registry stores only a SHA-256 fingerprint,
subject, locked THF package identity, provider name, generation and lifecycle state.
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


class SecureTokenVault(Protocol):
    """Opaque token custody boundary. Production implementations must encrypt at rest."""

    def put(self, token_id: str, raw_token: str) -> None: ...
    def get(self, token_id: str) -> str: ...
    def delete(self, token_id: str) -> None: ...


@dataclass(frozen=True)
class Registration:
    token_id: str
    subject: str
    package: str
    provider: str
    fingerprint: str
    generation: int
    active: bool


def _fingerprint(raw_token: str) -> str:
    if not raw_token or len(raw_token.strip()) < 8:
        raise ValueError("provider token is missing or implausibly short")
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _token_id(*, subject: str, package: str, provider: str, fingerprint: str) -> str:
    return hashlib.sha256(f"{subject}\0{package}\0{provider}\0{fingerprint}".encode()).hexdigest()


class NotificationTokenRegistry:
    def __init__(self, db: sqlite3.Connection, vault: SecureTokenVault):
        self.db = db
        self.vault = vault
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_tokens (
              token_id TEXT PRIMARY KEY,
              subject TEXT NOT NULL,
              package TEXT NOT NULL,
              provider TEXT NOT NULL,
              fingerprint TEXT NOT NULL,
              generation INTEGER NOT NULL,
              active INTEGER NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              UNIQUE(subject, package, provider, fingerprint)
            )
            """
        )
        self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_notification_tokens_subject ON notification_tokens(subject, package, active)"
        )
        self.db.commit()

    @staticmethod
    def _validate_identity(subject: str, package: str, provider: str) -> None:
        if not subject or not subject.strip():
            raise PermissionError("authenticated subject required")
        if package not in ALLOWED_PACKAGES:
            raise PermissionError("package is not in the locked THF allowlist")
        if provider not in ALLOWED_PROVIDERS:
            raise ValueError("unsupported provider")

    def register(self, *, subject: str, package: str, provider: str, raw_token: str) -> Registration:
        self._validate_identity(subject, package, provider)
        fp = _fingerprint(raw_token)
        now = int(time.time())
        token_id = _token_id(subject=subject, package=package, provider=provider, fingerprint=fp)
        row = self.db.execute(
            "SELECT generation, active FROM notification_tokens WHERE token_id=?", (token_id,)
        ).fetchone()
        generation = int(row[0]) if row else 1
        self.vault.put(token_id, raw_token)
        try:
            with self.db:
                self.db.execute(
                    """
                    INSERT INTO notification_tokens(token_id,subject,package,provider,fingerprint,generation,active,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,1,?,?)
                    ON CONFLICT(token_id) DO UPDATE SET active=1, updated_at=excluded.updated_at
                    """,
                    (token_id, subject, package, provider, fp, generation, now, now),
                )
        except Exception:
            self.vault.delete(token_id)
            raise
        return self.get(token_id, subject=subject)

    def rotate(
        self,
        *,
        subject: str,
        package: str,
        provider: str,
        old_token_id: str,
        new_raw_token: str,
    ) -> Registration:
        self._validate_identity(subject, package, provider)
        old = self.get(old_token_id, subject=subject)
        if not old.active or old.package != package or old.provider != provider:
            raise PermissionError("rotation source is inactive or outside authenticated scope")
        new_fp = _fingerprint(new_raw_token)
        new_token_id = _token_id(subject=subject, package=package, provider=provider, fingerprint=new_fp)
        if new_token_id == old_token_id:
            raise ValueError("new provider token must differ from rotation source")
        next_generation = old.generation + 1
        now = int(time.time())
        self.vault.put(new_token_id, new_raw_token)
        try:
            with self.db:
                self.db.execute(
                    "UPDATE notification_tokens SET active=0, updated_at=? WHERE token_id=? AND subject=? AND active=1",
                    (now, old_token_id, subject),
                )
                if self.db.execute("SELECT changes()").fetchone()[0] != 1:
                    raise PermissionError("rotation source changed before commit")
                self.db.execute(
                    """
                    INSERT INTO notification_tokens(token_id,subject,package,provider,fingerprint,generation,active,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,1,?,?)
                    ON CONFLICT(token_id) DO UPDATE SET generation=excluded.generation, active=1, updated_at=excluded.updated_at
                    """,
                    (new_token_id, subject, package, provider, new_fp, next_generation, now, now),
                )
        except Exception:
            self.vault.delete(new_token_id)
            raise
        self.vault.delete(old_token_id)
        return self.get(new_token_id, subject=subject)

    def revoke(self, *, token_id: str, subject: str) -> None:
        reg = self.get(token_id, subject=subject)
        if reg.active:
            self.db.execute(
                "UPDATE notification_tokens SET active=0, updated_at=? WHERE token_id=?",
                (int(time.time()), token_id),
            )
            self.db.commit()
            self.vault.delete(token_id)

    def revoke_logout(self, *, subject: str, package: str) -> int:
        if package not in ALLOWED_PACKAGES:
            raise PermissionError("package is not in the locked THF allowlist")
        rows = self.db.execute(
            "SELECT token_id FROM notification_tokens WHERE subject=? AND package=? AND active=1",
            (subject, package),
        ).fetchall()
        for (token_id,) in rows:
            self.revoke(token_id=token_id, subject=subject)
        return len(rows)

    def get(self, token_id: str, *, subject: str) -> Registration:
        row = self.db.execute(
            """
            SELECT token_id,subject,package,provider,fingerprint,generation,active
            FROM notification_tokens WHERE token_id=? AND subject=?
            """,
            (token_id, subject),
        ).fetchone()
        if not row:
            raise PermissionError("notification token is outside authenticated subject scope")
        return Registration(
            token_id=row[0], subject=row[1], package=row[2], provider=row[3], fingerprint=row[4],
            generation=int(row[5]), active=bool(row[6])
        )
