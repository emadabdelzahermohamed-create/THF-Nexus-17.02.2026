#!/usr/bin/env python3
"""Framework-neutral HTTP contract candidate for THF notification registration.

Security boundary:
- authentication is performed by THF Pass before this contract is called;
- this module accepts only an already-verified SessionPrincipal;
- the Pass principal must still be live (not revoked and not expired);
- the Pass principal is bound to one locked application package/audience;
- notification registrations are bound to the exact Pass session;
- provider tokens are accepted only in request bodies, never query strings;
- package identities are constrained by NotificationTokenRegistry;
- no provider delivery is implemented here, so PUSH_READY remains false.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Mapping

from notification_lifecycle import NotificationTokenRegistry


@dataclass(frozen=True)
class SessionPrincipal:
    subject: str
    session_id: str
    package_id: str
    authenticated: bool
    session_expires_at: float | None = None
    revoked: bool = False

    def require_authenticated(self) -> str:
        if not self.authenticated or not self.subject.strip() or not self.session_id.strip() or not self.package_id.strip():
            raise PermissionError("verified package-bound THF Pass session required")
        if self.revoked:
            raise PermissionError("revoked THF Pass session")
        if self.session_expires_at is not None and time.time() >= self.session_expires_at:
            raise PermissionError("expired THF Pass session")
        return self.subject

    def require_package(self, requested_package: str) -> str:
        self.require_authenticated()
        if requested_package != self.package_id:
            raise PermissionError("requested package does not match THF Pass session audience")
        return requested_package


@dataclass(frozen=True)
class ContractResponse:
    status: int
    body: dict[str, Any]


class NotificationHttpContract:
    """Small deterministic contract intended to sit behind HTTPS/WSS ingress."""

    def __init__(self, registry: NotificationTokenRegistry):
        self.registry = registry

    @staticmethod
    def _reject_query_credentials(query: Mapping[str, str] | None) -> None:
        for key in (query or {}):
            normalized = key.lower().replace("-", "_")
            if any(part in normalized for part in ("token", "authorization", "credential", "secret")):
                raise PermissionError("credentials/provider tokens are forbidden in query strings")

    @staticmethod
    def _required(body: Mapping[str, Any], key: str) -> str:
        value = body.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing required field: {key}")
        return value.strip()

    def register(self, *, principal: SessionPrincipal, body: Mapping[str, Any], query: Mapping[str, str] | None = None) -> ContractResponse:
        self._reject_query_credentials(query)
        subject = principal.require_authenticated()
        package = principal.require_package(self._required(body, "package"))
        reg = self.registry.register(
            subject=subject,
            session_id=principal.session_id,
            package=package,
            provider=self._required(body, "provider"),
            raw_token=self._required(body, "provider_token"),
        )
        return ContractResponse(201, {
            "token_id": reg.token_id,
            "package": reg.package,
            "provider": reg.provider,
            "generation": reg.generation,
            "active": reg.active,
        })

    def rotate(self, *, principal: SessionPrincipal, body: Mapping[str, Any], query: Mapping[str, str] | None = None) -> ContractResponse:
        self._reject_query_credentials(query)
        subject = principal.require_authenticated()
        package = principal.require_package(self._required(body, "package"))
        reg = self.registry.rotate(
            subject=subject,
            session_id=principal.session_id,
            package=package,
            provider=self._required(body, "provider"),
            old_token_id=self._required(body, "old_token_id"),
            new_raw_token=self._required(body, "provider_token"),
        )
        return ContractResponse(200, {
            "token_id": reg.token_id,
            "generation": reg.generation,
            "active": reg.active,
        })

    def revoke(self, *, principal: SessionPrincipal, body: Mapping[str, Any], query: Mapping[str, str] | None = None) -> ContractResponse:
        self._reject_query_credentials(query)
        subject = principal.require_authenticated()
        token_id = self._required(body, "token_id")
        existing = self.registry.get(token_id, subject=subject, session_id=principal.session_id)
        principal.require_package(existing.package)
        self.registry.revoke(token_id=token_id, subject=subject, session_id=principal.session_id)
        return ContractResponse(204, {})

    def logout(self, *, principal: SessionPrincipal, body: Mapping[str, Any], query: Mapping[str, str] | None = None) -> ContractResponse:
        self._reject_query_credentials(query)
        subject = principal.require_authenticated()
        package = principal.require_package(self._required(body, "package"))
        count = self.registry.revoke_logout(
            subject=subject, session_id=principal.session_id, package=package
        )
        return ContractResponse(200, {"revoked": count})
