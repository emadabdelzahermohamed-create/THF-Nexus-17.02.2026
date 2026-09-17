from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


class OAuthProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    client_id_env: str
    client_secret_env: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scopes: tuple[str, ...]
    supports_pkce: bool = True


PROVIDERS: dict[str, Provider] = {
    "google": Provider(
        "google", "Google", "THF_GOOGLE_CLIENT_ID", "THF_GOOGLE_CLIENT_SECRET",
        "https://accounts.google.com/o/oauth2/v2/auth",
        "https://oauth2.googleapis.com/token",
        "https://openidconnect.googleapis.com/v1/userinfo",
        ("openid", "email", "profile"), True,
    ),
    "discord": Provider(
        "discord", "Discord", "THF_DISCORD_CLIENT_ID", "THF_DISCORD_CLIENT_SECRET",
        "https://discord.com/oauth2/authorize",
        "https://discord.com/api/oauth2/token",
        "https://discord.com/api/users/@me",
        ("identify", "email"), True,
    ),
    "facebook": Provider(
        "facebook", "Facebook", "THF_FACEBOOK_CLIENT_ID", "THF_FACEBOOK_CLIENT_SECRET",
        "https://www.facebook.com/dialog/oauth",
        "https://graph.facebook.com/oauth/access_token",
        "https://graph.facebook.com/me?fields=id,name,email",
        ("email", "public_profile"), False,
    ),
}


def _client_id(p: Provider) -> str:
    return os.getenv(p.client_id_env, "").strip()


def _client_secret(p: Provider) -> str:
    return os.getenv(p.client_secret_env, "").strip()


def enabled_providers() -> list[dict]:
    return [
        {"id": p.id, "label": p.label}
        for p in PROVIDERS.values()
        if _client_id(p) and _client_secret(p)
    ]


def provider_enabled(provider: str) -> bool:
    p = PROVIDERS.get(provider)
    return bool(p and _client_id(p) and _client_secret(p))


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def authorization_url(provider: str, *, state: str, redirect_uri: str, verifier: str) -> str:
    p = PROVIDERS.get(provider)
    if not p or not provider_enabled(provider):
        raise OAuthProviderError("provider_not_configured")
    params = {
        "client_id": _client_id(p),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(p.scopes),
        "state": state,
    }
    if p.id == "google":
        params["prompt"] = "select_account"
        params["access_type"] = "online"
    if p.supports_pkce:
        params["code_challenge"] = pkce_challenge(verifier)
        params["code_challenge_method"] = "S256"
    return p.authorize_url + "?" + urllib.parse.urlencode(params)


def _json_request(url: str, *, data: dict | None = None, headers: dict | None = None) -> dict:
    payload = None
    req_headers = {"Accept": "application/json", "User-Agent": "THF-Terra/1.0"}
    if headers:
        req_headers.update(headers)
    if data is not None:
        payload = urllib.parse.urlencode(data).encode("utf-8")
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=payload, headers=req_headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(256_000)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise OAuthProviderError("provider_network_error") from exc
    try:
        result = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise OAuthProviderError("provider_invalid_response") from exc
    if not isinstance(result, dict):
        raise OAuthProviderError("provider_invalid_response")
    return result


def _exchange_sync(provider: str, code: str, redirect_uri: str, verifier: str) -> dict:
    p = PROVIDERS.get(provider)
    if not p or not provider_enabled(provider):
        raise OAuthProviderError("provider_not_configured")
    token_data = {
        "client_id": _client_id(p),
        "client_secret": _client_secret(p),
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    if p.supports_pkce:
        token_data["code_verifier"] = verifier
    token = _json_request(p.token_url, data=token_data)
    access_token = str(token.get("access_token", ""))
    if not access_token:
        raise OAuthProviderError("provider_token_exchange_failed")

    if provider in {"google", "discord"}:
        info = _json_request(p.userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
    elif provider == "facebook":
        sep = "&" if "?" in p.userinfo_url else "?"
        info = _json_request(p.userinfo_url + sep + urllib.parse.urlencode({"access_token": access_token}))
    else:
        raise OAuthProviderError("unsupported_provider")

    subject = str(info.get("sub") or info.get("id") or "").strip()
    if not subject:
        raise OAuthProviderError("provider_subject_missing")
    email = str(info.get("email") or "").strip().lower()
    name = str(info.get("name") or info.get("global_name") or info.get("username") or email.split("@", 1)[0] or provider).strip()
    email_verified = bool(info.get("email_verified", provider != "google" or not email))
    return {
        "provider": provider,
        "subject": subject[:240],
        "email": email[:320],
        "email_verified": email_verified,
        "display_name": name[:120],
    }


async def exchange_identity(provider: str, *, code: str, redirect_uri: str, verifier: str) -> dict:
    return await asyncio.to_thread(_exchange_sync, provider, code, redirect_uri, verifier)
