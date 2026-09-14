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
        token_id = hashlib.sha256(f"{subject}\0{package}\0{provider}\0{fp}".encode()).hexdigest()
        row = self.db.execute(
            "SELECT generation, active FROM notification_tokens WHERE token_id=?", (token_id,)
        ).fetchone()
        generation = int(row[0]) if row else 1
        self.vault.put(token_id, raw_token)
        self.db.execute(
            """
            INSERT INTO notification_tokens(token_id,subject,package,provider,fingerprint,generation,active,created_at,updated_at)
            VALUES(?,?,?,?,?,?,1,?,?)
            ON CONFLICT(token_id) DO UPDATE SET active=1, updated_at=excluded.updated_at
            """,
            (token_id, subject, package, provider, fp, generation, now, now),
        )
        self.db.commit()
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
        self.revoke(token_id=old_token_id, subject=subject)
        new = self.register(subject=subject, package=package, provider=provider, raw_token=new_raw_token)
        next_generation = old.generation + 1
        self.db.execute(
            "UPDATE notification_tokens SET generation=? WHERE token_id=?", (next_generation, new.token_id)
        )
        self.db.commit()
        return self.get(new.token_id, subject=subject)

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
