#!/usr/bin/env python3
"""Fail-closed THF Pass receiver/federation candidate.

This module is intentionally a server-side/control-plane contract, not proof of a
reachable production backend. It consumes a verifier boundary that must perform real
cryptographic verification outside this module, then enforces replay, issuer,
audience, scope, route, private-app RBAC and session invariants before creating a
federated session.

It never creates offline economy/social/ranked truth and does not establish
NETWORK_RELEASE_READY, PHYSICAL_DEVICE_PASS, PUSH_READY or FINAL/PLAY_READY.
"""
from __future__ import annotations

from dataclasses import dataclass
import secrets
import sqlite3
import time
from typing import Mapping, Protocol
from urllib.parse import urlparse


TRUSTED_ISSUER = "https://pass.topherofit.com"
CLAIMS_VERSION = 1
MAX_HANDOFF_TTL_SECONDS = 120
MAX_CLOCK_SKEW_SECONDS = 30

PACKAGE_SLUGS: Mapping[str, str] = {
    "com.topherofit.thf.core": "core",
    "com.topherofit.thf.pulse": "pulse",
    "com.topherofit.thf.forge": "forge",
    "com.topherofit.thf.echo": "echo",
    "com.topherofit.thf.codex": "codex",
    "com.topherofit.thf.spark": "spark",
    "com.topherofit.thf.rush": "rush",
    "com.topherofit.thf.vault": "vault",
    "com.topherofit.thf.signal": "signal",
    "com.topherofit.thf.command": "command",
}

BASE_SCOPES = frozenset({"openid", "profile", "locale", "notifications"})
APP_SCOPES: Mapping[str, frozenset[str]] = {
    package: BASE_SCOPES | frozenset({f"app:{slug}"}) for package, slug in PACKAGE_SLUGS.items()
}
FORBIDDEN_OFFLINE_TRUTH_SCOPES = frozenset({
    "economy:write", "wallet:write", "social:write", "ranked:write", "tournament:write"
})

# Private/internal applications are not authorized by client-side visibility. The
# deployed cryptographic verifier must return these role claims only after checking
# server-authoritative identity/RBAC state. Admin implies publisher for Signal only;
# Command always requires the explicit admin role.
ALLOWED_ROLE_CLAIMS = frozenset({"user", "publisher", "admin"})
PRIVATE_APP_REQUIRED_ROLES: Mapping[str, frozenset[str]] = {
    "com.topherofit.thf.signal": frozenset({"publisher", "admin"}),
    "com.topherofit.thf.command": frozenset({"admin"}),
}


@dataclass(frozen=True)
class VerifiedHandoff:
    issuer: str
    subject: str
    source_package: str
    target_package: str
    nonce: str
    state: str
    issued_at: float
    expires_at: float
    scopes: tuple[str, ...]
    return_route: str
    online_authority: bool
    claims_version: int = CLAIMS_VERSION
    roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class FederatedSession:
    subject: str
    session_id: str
    package_id: str
    source_package: str
    scopes: tuple[str, ...]
    created_at: float
    expires_at: float
    revoked: bool = False
    roles: tuple[str, ...] = ()


class HandoffVerifier(Protocol):
    """Cryptographic/transport verifier supplied by the deployed THF Pass boundary."""

    def verify(self, raw_payload: str) -> VerifiedHandoff: ...


class HandoffReplayStore:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS used_handoffs ("
            "issuer TEXT NOT NULL, nonce TEXT NOT NULL, subject TEXT NOT NULL, "
            "target_package TEXT NOT NULL, expires_at REAL NOT NULL, "
            "PRIMARY KEY (issuer, nonce))"
        )
        self.db.commit()

    def consume(self, handoff: VerifiedHandoff, *, now: float) -> None:
        self.db.execute("DELETE FROM used_handoffs WHERE expires_at < ?", (now,))
        try:
            self.db.execute(
                "INSERT INTO used_handoffs(issuer,nonce,subject,target_package,expires_at) VALUES(?,?,?,?,?)",
                (handoff.issuer, handoff.nonce, handoff.subject, handoff.target_package, handoff.expires_at),
            )
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise PermissionError("THF Pass handoff nonce replayed") from exc


class FederatedSessionStore:
    def __init__(self, connection: sqlite3.Connection):
        self.db = connection
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS federated_sessions ("
            "session_id TEXT PRIMARY KEY, subject TEXT NOT NULL, package_id TEXT NOT NULL, "
            "source_package TEXT NOT NULL, scopes TEXT NOT NULL, created_at REAL NOT NULL, "
            "expires_at REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, "
            "roles TEXT NOT NULL DEFAULT '')"
        )
        # Safe forward migration for V1 databases. Existing sessions receive no role
        # claims and therefore cannot enter private applications after this upgrade.
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(federated_sessions)")}
        if "roles" not in columns:
            self.db.execute("ALTER TABLE federated_sessions ADD COLUMN roles TEXT NOT NULL DEFAULT ''")
        self.db.commit()

    def create(self, handoff: VerifiedHandoff, *, now: float, ttl_seconds: int = 3600) -> FederatedSession:
        session_id = secrets.token_urlsafe(32)
        expires_at = now + ttl_seconds
        scopes = tuple(sorted(set(handoff.scopes)))
        roles = tuple(sorted(set(handoff.roles)))
        self.db.execute(
            "INSERT INTO federated_sessions(session_id,subject,package_id,source_package,scopes,created_at,expires_at,revoked,roles) "
            "VALUES(?,?,?,?,?,?,?,0,?)",
            (session_id, handoff.subject, handoff.target_package, handoff.source_package,
             " ".join(scopes), now, expires_at, " ".join(roles)),
        )
        self.db.commit()
        return FederatedSession(
            handoff.subject, session_id, handoff.target_package, handoff.source_package,
            scopes, now, expires_at, False, roles,
        )

    def resolve(self, session_id: str) -> FederatedSession | None:
        row = self.db.execute(
            "SELECT subject,session_id,package_id,source_package,scopes,created_at,expires_at,revoked,roles "
            "FROM federated_sessions WHERE session_id=?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return FederatedSession(
            row[0], row[1], row[2], row[3], tuple(row[4].split()), row[5], row[6], bool(row[7]),
            tuple(row[8].split()) if row[8] else (),
        )

    def revoke_session(self, session_id: str) -> None:
        self.db.execute("UPDATE federated_sessions SET revoked=1 WHERE session_id=?", (session_id,))
        self.db.commit()


class PassHandoffReceiver:
    def __init__(
        self,
        *,
        verifier: HandoffVerifier,
        replay_store: HandoffReplayStore,
        session_store: FederatedSessionStore,
        clock=time.time,
    ):
        self.verifier = verifier
        self.replays = replay_store
        self.sessions = session_store
        self.clock = clock

    def receive(self, *, raw_payload: str, installed_package: str, expected_state: str) -> FederatedSession:
        if not raw_payload or not expected_state:
            raise PermissionError("THF Pass handoff payload/state required")
        handoff = self.verifier.verify(raw_payload)
        now = float(self.clock())
        self._validate(handoff, installed_package=installed_package, expected_state=expected_state, now=now)
        # Consume only after every semantic check succeeds; replay is then fail-closed.
        self.replays.consume(handoff, now=now)
        return self.sessions.create(handoff, now=now)

    def _validate(self, handoff: VerifiedHandoff, *, installed_package: str, expected_state: str, now: float) -> None:
        if handoff.claims_version != CLAIMS_VERSION:
            raise PermissionError("unsupported THF Pass claims version")
        if handoff.issuer != TRUSTED_ISSUER:
            raise PermissionError("untrusted THF Pass issuer")
        if handoff.target_package != installed_package:
            raise PermissionError("THF Pass handoff audience mismatch")
        if installed_package not in PACKAGE_SLUGS or handoff.source_package not in PACKAGE_SLUGS:
            raise PermissionError("unknown THF application package")
        if handoff.source_package == handoff.target_package:
            raise PermissionError("cross-app handoff source and target must differ")
        if not handoff.subject or not handoff.nonce or not handoff.state:
            raise PermissionError("THF Pass identity/nonce/state missing")
        if not secrets.compare_digest(handoff.state, expected_state):
            raise PermissionError("THF Pass handoff state mismatch")
        if handoff.issued_at > now + MAX_CLOCK_SKEW_SECONDS:
            raise PermissionError("THF Pass handoff issued in the future")
        if now >= handoff.expires_at:
            raise PermissionError("THF Pass handoff expired")
        ttl = handoff.expires_at - handoff.issued_at
        if ttl <= 0 or ttl > MAX_HANDOFF_TTL_SECONDS:
            raise PermissionError("THF Pass handoff TTL invalid")

        requested = set(handoff.scopes)
        if not requested or not requested.issubset(APP_SCOPES[installed_package]):
            raise PermissionError("THF Pass handoff scope escalation")
        if not handoff.online_authority and requested.intersection(FORBIDDEN_OFFLINE_TRUTH_SCOPES):
            raise PermissionError("offline handoff cannot establish economy/social/ranked truth")

        roles = set(handoff.roles)
        if any(not role or role not in ALLOWED_ROLE_CLAIMS for role in roles):
            raise PermissionError("THF Pass handoff contains unknown role claim")
        private_roles = PRIVATE_APP_REQUIRED_ROLES.get(installed_package)
        if private_roles is not None:
            if not handoff.online_authority:
                raise PermissionError("private THF application requires online RBAC authority")
            if roles.isdisjoint(private_roles):
                raise PermissionError("private THF application role denied")

        parsed = urlparse(handoff.return_route)
        expected_slug = PACKAGE_SLUGS[installed_package]
        if parsed.scheme != "thf" or parsed.netloc != expected_slug or not parsed.path.startswith("/"):
            raise PermissionError("THF Pass return route is not bound to target application")

    def authorize_session(
        self,
        *,
        session_id: str,
        subject: str,
        package_id: str,
        required_role: str | None = None,
    ) -> FederatedSession:
        session = self.sessions.resolve(session_id)
        now = float(self.clock())
        if session is None:
            raise PermissionError("THF Pass federated session unknown")
        if session.revoked:
            raise PermissionError("THF Pass federated session revoked")
        if now >= session.expires_at:
            raise PermissionError("THF Pass federated session expired")
        if session.subject != subject or session.package_id != package_id:
            raise PermissionError("THF Pass federated session binding mismatch")
        private_roles = PRIVATE_APP_REQUIRED_ROLES.get(package_id)
        if private_roles is not None and set(session.roles).isdisjoint(private_roles):
            raise PermissionError("private THF application session role denied")
        if required_role is not None:
            if required_role not in ALLOWED_ROLE_CLAIMS:
                raise PermissionError("unknown required THF role")
            effective_roles = set(session.roles)
            if required_role == "publisher" and "admin" in effective_roles:
                effective_roles.add("publisher")
            if required_role not in effective_roles:
                raise PermissionError("THF federated session role denied")
        return session
