#!/usr/bin/env python3
"""Live THF Pass -> notification integration boundary.

This module closes the stale-principal gap between a previously verified Pass principal
and notification mutation/delivery. Every operation re-checks the session against a
live SessionAuthority before touching registration state or provider dispatch.

It is provider-neutral and contains no FCM/APNs credentials. It therefore does not by
itself establish PUSH_READY or FINAL/PLAY_READY.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Protocol

from notification_dispatch import NotificationDispatcher
from notification_http_contract import ContractResponse, NotificationHttpContract, SessionPrincipal
from notification_provider_contract import DeliveryRequest, DeliveryResult


@dataclass(frozen=True)
class LiveSession:
    subject: str
    session_id: str
    package_id: str
    expires_at: float
    revoked: bool = False


class SessionAuthority(Protocol):
    def resolve(self, session_id: str) -> LiveSession | None: ...
    def revoke_session(self, session_id: str) -> None: ...


class PassNotificationBridge:
    """Require a current Pass authority decision for every notification operation."""

    def __init__(
        self,
        *,
        authority: SessionAuthority,
        http_contract: NotificationHttpContract,
        dispatcher: NotificationDispatcher,
        clock=time.time,
    ):
        self.authority = authority
        self.http = http_contract
        self.dispatcher = dispatcher
        self.clock = clock

    def authorize(self, principal: SessionPrincipal) -> LiveSession:
        # Preserve local structural/auth checks first; then re-check authoritative state.
        principal.require_authenticated()
        live = self.authority.resolve(principal.session_id)
        if live is None:
            raise PermissionError("THF Pass session is unknown")
        if live.revoked:
            raise PermissionError("THF Pass session is revoked")
        if self.clock() >= live.expires_at:
            raise PermissionError("THF Pass session is expired")
        if live.subject != principal.subject:
            raise PermissionError("THF Pass session subject mismatch")
        if live.package_id != principal.package_id:
            raise PermissionError("THF Pass session audience mismatch")
        return live

    def register(self, *, principal: SessionPrincipal, body, query=None) -> ContractResponse:
        self.authorize(principal)
        return self.http.register(principal=principal, body=body, query=query)

    def rotate(self, *, principal: SessionPrincipal, body, query=None) -> ContractResponse:
        self.authorize(principal)
        return self.http.rotate(principal=principal, body=body, query=query)

    def revoke(self, *, principal: SessionPrincipal, body, query=None) -> ContractResponse:
        self.authorize(principal)
        return self.http.revoke(principal=principal, body=body, query=query)

    def dispatch(self, *, principal: SessionPrincipal, request: DeliveryRequest) -> DeliveryResult:
        live = self.authorize(principal)
        registration = self.http.registry.get(request.token_id, subject=live.subject)
        if registration.package != live.package_id:
            raise PermissionError("notification registration does not match THF Pass session audience")
        return self.dispatcher.dispatch(subject=live.subject, request=request)

    def logout(self, *, principal: SessionPrincipal) -> ContractResponse:
        """Revoke the Pass session first, then remove package-scoped provider registrations.

        Revoking Pass first is deliberately fail-secure: if token cleanup later fails, the
        session still cannot authorize another mutation or dispatch.
        """
        live = self.authorize(principal)
        self.authority.revoke_session(live.session_id)
        count = self.http.registry.revoke_logout(subject=live.subject, package=live.package_id)
        return ContractResponse(200, {"session_revoked": True, "notification_tokens_revoked": count})
