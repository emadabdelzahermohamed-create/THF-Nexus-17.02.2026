#!/usr/bin/env python3
"""Provider adapter contract for THF notifications.

This defines the minimum behavior a real provider adapter must expose before it may
be attached to the lifecycle registry. It intentionally contains no credentials,
network sender, or production provider implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlsplit, parse_qsl


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
    def send(self, *, provider_token: str, request: DeliveryRequest) -> DeliveryResult: ...


def validate_delivery_request(request: DeliveryRequest) -> None:
    if not request.token_id.strip():
        raise ValueError("token_id required")
    if not request.title_key.strip() or not request.body_key.strip():
        raise ValueError("localized resource keys required")
    if not request.locale.strip():
        raise ValueError("locale required")
    if request.deeplink:
        parsed=urlsplit(request.deeplink)
        if parsed.scheme not in {"thf","https"}:
            raise PermissionError("notification deeplink must use thf or https scheme")
        sensitive={"token","access_token","authorization","secret","credential","provider_token"}
        keys={k.lower() for k,_ in parse_qsl(parsed.query,keep_blank_values=True)}
        fragment=parsed.fragment.lower()
        if keys & sensitive or any(f"{x}=" in fragment for x in sensitive):
            raise PermissionError("credentials are forbidden in notification deeplinks")


def validate_delivery_result(result: DeliveryResult) -> None:
    if result.accepted and (result.retryable or result.permanent_token_failure):
        raise ValueError("accepted delivery cannot also be retryable or permanently failed")
    if result.retryable and result.permanent_token_failure:
        raise ValueError("delivery failure cannot be both retryable and permanent")
    if result.accepted and not result.provider_message_id:
        raise ValueError("accepted delivery requires provider_message_id")


def assert_adapter_conformance(adapter: NotificationProviderAdapter) -> None:
    name=getattr(adapter,"provider_name","")
    if name not in {"fcm","apns","test"}:
        raise ValueError("unsupported provider adapter")
    if not callable(getattr(adapter,"validate_configuration",None)) or not callable(getattr(adapter,"send",None)):
        raise TypeError("provider adapter is incomplete")
    configured=adapter.validate_configuration()
    if not isinstance(configured,bool):
        raise TypeError("validate_configuration must return bool")
