#!/usr/bin/env python3
"""Provider adapter contract for THF notifications.

This defines the minimum behavior a real provider adapter must expose before it may
be attached to the lifecycle registry. It intentionally contains no credentials,
network sender, or production provider implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DeliveryRequest:
    token_id: str
    title_key: str
    body_key: str
    locale: str
    deeplink: str | None
    data_saver: bool


@dataclass(frozen=True)
class DeliveryResult:
    accepted: bool
    provider_message_id: str | None = None
    permanent_token_failure: bool = False
    retryable: bool = False


class NotificationProviderAdapter(Protocol):
    provider_name: str

    def validate_configuration(self) -> bool: ...
    def send(self, request: DeliveryRequest) -> DeliveryResult: ...


def validate_delivery_request(request: DeliveryRequest) -> None:
    if not request.token_id.strip():
        raise ValueError("token_id required")
    if not request.title_key.strip() or not request.body_key.strip():
        raise ValueError("localized resource keys required")
    if not request.locale.strip():
        raise ValueError("locale required")
    if request.deeplink:
        lowered=request.deeplink.lower()
        if any(x in lowered for x in ("token=", "access_token=", "authorization=", "secret=", "credential=")):
            raise PermissionError("credentials are forbidden in notification deeplinks")


def assert_adapter_conformance(adapter: NotificationProviderAdapter) -> None:
    name=getattr(adapter,"provider_name","")
    if name not in {"fcm","apns","test"}:
        raise ValueError("unsupported provider adapter")
    if not callable(getattr(adapter,"validate_configuration",None)) or not callable(getattr(adapter,"send",None)):
        raise TypeError("provider adapter is incomplete")
    # Configuration must be explicit. A false result is acceptable before deployment;
    # callers must not attempt live delivery when it is false.
    configured=adapter.validate_configuration()
    if not isinstance(configured,bool):
        raise TypeError("validate_configuration must return bool")
