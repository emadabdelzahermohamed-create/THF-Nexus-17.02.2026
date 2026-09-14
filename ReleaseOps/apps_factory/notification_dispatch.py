#!/usr/bin/env python3
"""Fail-closed coordinator between THF notification registry and provider adapters.

This is server-side contract code only. It does not provide FCM/APNs credentials or
network transport and therefore cannot establish PUSH_READY by itself.
"""
from __future__ import annotations

from notification_lifecycle import NotificationTokenRegistry
from notification_provider_contract import (
    DeliveryRequest,
    DeliveryResult,
    NotificationProviderAdapter,
    assert_adapter_conformance,
    validate_delivery_request,
    validate_delivery_result,
)


class NotificationDispatcher:
    def __init__(self, registry: NotificationTokenRegistry, adapters: dict[str, NotificationProviderAdapter]):
        self.registry = registry
        self.adapters = dict(adapters)
        for provider, adapter in self.adapters.items():
            assert_adapter_conformance(adapter)
            if adapter.provider_name != provider:
                raise ValueError("adapter map key must match provider_name")

    def dispatch(self, *, subject: str, session_id: str, request: DeliveryRequest) -> DeliveryResult:
        validate_delivery_request(request)
        reg = self.registry.get(request.token_id, subject=subject, session_id=session_id)
        if not reg.active:
            raise PermissionError("notification registration is inactive")

        adapter = self.adapters.get(reg.provider)
        if adapter is None:
            raise RuntimeError("no provider adapter registered")
        if not adapter.validate_configuration():
            raise RuntimeError("provider adapter is not configured")

        raw_token = self.registry.vault.get(reg.token_id)
        if not isinstance(raw_token, str) or len(raw_token.strip()) < 8:
            raise RuntimeError("provider token unavailable from secure vault")

        result = adapter.send(provider_token=raw_token, request=request)
        if not isinstance(result, DeliveryResult):
            raise TypeError("provider adapter returned invalid result type")
        validate_delivery_result(result)

        if result.permanent_token_failure:
            self.registry.revoke(token_id=reg.token_id, subject=subject, session_id=session_id)
        return result
