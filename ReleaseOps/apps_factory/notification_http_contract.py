#!/usr/bin/env python3
"""Framework-neutral HTTP contract candidate for THF notification registration.

Security boundary:
- authentication is performed by THF Pass before this contract is called;
- this module accepts only an already-verified SessionPrincipal;
- provider tokens are accepted only in request bodies, never query strings;
- package identities are constrained by NotificationTokenRegistry;
- no provider delivery is implemented here, so PUSH_READY remains false.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from notification_lifecycle import NotificationTokenRegistry


@dataclass(frozen=True)
class SessionPrincipal:
    subject: str
    session_id: str
    authenticated: bool

    def require_authenticated(self) -> str:
        if not self.authenticated or not self.subject.strip() or not self.session_id.strip():
            raise PermissionError("verified THF Pass session required")
        return self.subject


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
        reg = self.registry.register(
            subject=subject,
            package=self._required(body, "package"),
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
        reg = self.registry.rotate(
            subject=subject,
            package=self._required(body, "package"),
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
        self.registry.revoke(token_id=self._required(body, "token_id"), subject=subject)
        return ContractResponse(204, {})

    def logout(self, *, principal: SessionPrincipal, body: Mapping[str, Any], query: Mapping[str, str] | None = None) -> ContractResponse:
        self._reject_query_credentials(query)
        subject = principal.require_authenticated()
        count = self.registry.revoke_logout(subject=subject, package=self._required(body, "package"))
        return ContractResponse(200, {"revoked": count})
