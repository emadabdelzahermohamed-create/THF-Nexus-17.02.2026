"""Fail-closed verification for short-lived THF Fitness V2 access tokens.

The API validates tokens issued by the existing THF account service; it never
accepts a user identifier from an Android or Web workout payload.  The module
uses only the Python standard library so the verification gate can run in the
minimal CI and recovery environments used by this repository.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Callable, Mapping


class AuthenticationError(ValueError):
    """A bearer credential could not be authenticated."""


@dataclass(frozen=True)
class Principal:
    user_id: str
    session_id: str


def _decode_segment(value: str) -> bytes:
    if not value or any(character.isspace() for character in value):
        raise AuthenticationError("malformed access token")
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (binascii.Error, ValueError, TypeError) as exc:
        raise AuthenticationError("malformed access token") from exc


class HmacAccessTokenVerifier:
    """Verify issuer-bound HS256 access tokens from a rotated key ring.

    This is a verifier, not a token issuer.  Production keys are supplied at
    runtime and selected by ``kid``; there is deliberately no development or
    hard-coded fallback secret.
    """

    def __init__(
        self,
        keys: Mapping[str, bytes],
        issuer: str,
        audience: str,
        *,
        max_lifetime_seconds: int = 3600,
        clock_skew_seconds: int = 30,
        now: Callable[[], float] = time.time,
        is_session_revoked: Callable[[str, str], bool] | None = None,
    ):
        if not keys or any(
            not isinstance(kid, str)
            or not kid
            or not isinstance(secret, (bytes, bytearray))
            or len(secret) < 32
            for kid, secret in keys.items()
        ):
            raise ValueError("a non-empty key ring with >=32-byte secrets is required")
        if not issuer or not audience:
            raise ValueError("issuer and audience are required")
        self.keys = {kid: bytes(secret) for kid, secret in keys.items()}
        self.issuer = issuer
        self.audience = audience
        self.max_lifetime_seconds = max_lifetime_seconds
        self.clock_skew_seconds = clock_skew_seconds
        self.now = now
        self.is_session_revoked = is_session_revoked or (lambda _user, _session: False)

    def verify_authorization(self, authorization: str | None) -> Principal:
        if not authorization or len(authorization) > 8192 or not authorization.startswith("Bearer "):
            raise AuthenticationError("bearer access token required")
        token = authorization[7:].strip()
        parts = token.split(".")
        if len(parts) != 3:
            raise AuthenticationError("malformed access token")
        header_segment, payload_segment, signature_segment = parts
        try:
            header = json.loads(_decode_segment(header_segment))
            claims = json.loads(_decode_segment(payload_segment))
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise AuthenticationError("malformed access token") from exc
        if not isinstance(header, dict) or not isinstance(claims, dict):
            raise AuthenticationError("malformed access token")
        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise AuthenticationError("unsupported access token algorithm")
        kid = header.get("kid")
        secret = self.keys.get(kid) if isinstance(kid, str) else None
        if secret is None:
            raise AuthenticationError("unknown access token key")
        signed = f"{header_segment}.{payload_segment}".encode("ascii")
        expected = hmac.new(secret, signed, hashlib.sha256).digest()
        actual = _decode_segment(signature_segment)
        if not hmac.compare_digest(expected, actual):
            raise AuthenticationError("invalid access token signature")

        now = int(self.now())
        try:
            issued_at = int(claims["iat"])
            expires_at = int(claims["exp"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("invalid access token timestamps") from exc
        if claims.get("iss") != self.issuer or claims.get("aud") != self.audience:
            raise AuthenticationError("invalid access token scope")
        if issued_at > now + self.clock_skew_seconds or expires_at <= now - self.clock_skew_seconds:
            raise AuthenticationError("expired or not-yet-valid access token")
        if expires_at <= issued_at or expires_at - issued_at > self.max_lifetime_seconds:
            raise AuthenticationError("invalid access token lifetime")
        not_before = claims.get("nbf")
        if not_before is not None:
            try:
                not_before = int(not_before)
            except (TypeError, ValueError) as exc:
                raise AuthenticationError("invalid access token timestamps") from exc
            if not_before > now + self.clock_skew_seconds:
                raise AuthenticationError("access token is not active")
        user_id = claims.get("sub")
        session_id = claims.get("sid")
        if (
            not isinstance(user_id, str)
            or not 1 <= len(user_id) <= 128
            or any(character.isspace() or ord(character) < 0x20 for character in user_id)
        ):
            raise AuthenticationError("invalid access token subject")
        if (
            not isinstance(session_id, str)
            or not 8 <= len(session_id) <= 128
            or any(character.isspace() or ord(character) < 0x20 for character in session_id)
        ):
            raise AuthenticationError("invalid access token session")
        if self.is_session_revoked(user_id, session_id):
            raise AuthenticationError("access token session revoked")
        return Principal(user_id=user_id, session_id=session_id)


def decode_key_ring(value: str) -> dict[str, bytes]:
    """Decode ``{kid: base64url-secret}`` without accepting plain-text keys."""
    try:
        document = json.loads(value)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("THF_AUTH_KEYS_JSON must be valid JSON") from exc
    if not isinstance(document, dict):
        raise ValueError("THF_AUTH_KEYS_JSON must be an object")
    decoded: dict[str, bytes] = {}
    for kid, encoded in document.items():
        if not isinstance(kid, str) or not isinstance(encoded, str):
            raise ValueError("key ids and values must be strings")
        try:
            decoded[kid] = _decode_segment(encoded)
        except AuthenticationError as exc:
            raise ValueError("THF_AUTH_KEYS_JSON contains an invalid encoded key") from exc
    return decoded
