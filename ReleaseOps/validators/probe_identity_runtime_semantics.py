#!/usr/bin/env python3
"""Read-only THF identity/runtime semantics probe.

This probe is deliberately fail-closed. It never creates accounts, never submits
real credentials, and never upgrades auth/Pass readiness from route names alone.
It compares candidate routes against a randomized not-found control so SPA/static
fallbacks cannot masquerade as API routes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List

UA = "THF-ReleaseOps-IdentityProbe/1.0"

ROUTES: Dict[str, List[str]] = {
    "login": ["/auth/login", "/api/auth/login", "/v1/auth/login", "/auth/token", "/api/auth/token"],
    "refresh": ["/auth/refresh", "/api/auth/refresh", "/v1/auth/refresh", "/token/refresh"],
    "logout": ["/auth/logout", "/api/auth/logout", "/v1/auth/logout", "/session/logout"],
    "revoke": ["/auth/revoke", "/api/auth/revoke", "/v1/auth/revoke", "/token/revoke"],
    "federation": ["/auth/federation", "/api/auth/federation", "/federation", "/handoff", "/auth/handoff"],
}

@dataclass
class Obs:
    path: str
    method: str
    status: int
    content_type: str
    body_sha256: str
    body_len: int
    error: str = ""


def request(base: str, path: str, method: str, body: bytes | None = None) -> Obs:
    url = base.rstrip("/") + path
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12, context=ssl.create_default_context()) as r:
            raw = r.read(131072)
            return Obs(path, method, int(r.status), r.headers.get("Content-Type", ""), hashlib.sha256(raw).hexdigest(), len(raw))
    except urllib.error.HTTPError as e:
        raw = e.read(131072)
        return Obs(path, method, int(e.code), e.headers.get("Content-Type", ""), hashlib.sha256(raw).hexdigest(), len(raw))
    except Exception as e:  # network/tooling evidence, never readiness
        return Obs(path, method, 0, "", "", 0, f"{type(e).__name__}: {e}")


def distinct(a: Obs, control: Obs) -> bool:
    if a.status == 0:
        return False
    if a.status != control.status:
        return True
    if a.content_type.split(";", 1)[0].strip().lower() != control.content_type.split(";", 1)[0].strip().lower():
        return True
    return a.body_sha256 != control.body_sha256


def semantic_status_ok(o: Obs) -> bool:
    # Safe malformed/anonymous POST must not succeed. Validation/auth/method failures
    # are useful evidence that a server-side surface exists; 2xx/3xx is rejected.
    return o.status in {400, 401, 403, 405, 409, 415, 422, 429}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base_url")
    ap.add_argument("--json-out", required=True)
    ns = ap.parse_args()
    base = ns.base_url.rstrip("/")
    if not base.startswith("https://"):
        raise SystemExit("secure HTTPS staging URL required")

    health = request(base, "/health", "GET")
    nonce = secrets.token_hex(12)
    control = request(base, f"/__thf_releaseops_not_found_{nonce}", "GET")
    result = {
        "schema": 1,
        "base_url_class": "https",
        "health": asdict(health),
        "control": asdict(control),
        "categories": {},
        "surface_complete": False,
        "auth_semantics_proven": False,
        "valid_credential_flow_proven": False,
        "server_side_revocation_proven": False,
        "final_or_play_ready": False,
    }

    for category, paths in ROUTES.items():
        observations = []
        for path in paths:
            o = request(base, path, "POST", b"{}")
            d = asdict(o)
            d["distinct_from_control"] = distinct(o, control)
            d["safe_semantic_status"] = semantic_status_ok(o)
            observations.append(d)
        qualifying = [o for o in observations if o["distinct_from_control"] and o["safe_semantic_status"]]
        result["categories"][category] = {
            "surface_detected": bool(qualifying),
            "observations": observations,
        }

    health_json = False
    if health.status == 200:
        try:
            # We intentionally re-fetch a tiny health payload for semantic JSON check.
            with urllib.request.urlopen(base + "/health", timeout=12) as r:
                payload = json.load(r)
            health_json = isinstance(payload, dict) and payload.get("ok") is True
        except Exception:
            health_json = False
    result["health_json_ok"] = health_json
    result["surface_complete"] = health_json and all(v["surface_detected"] for v in result["categories"].values())

    # Route/safe-negative behavior is not a successful auth flow. Keep the truth
    # boundary explicit regardless of surface completeness.
    result["auth_semantics_proven"] = False

    with open(ns.json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps({
        "health_json_ok": result["health_json_ok"],
        "surface_complete": result["surface_complete"],
        "detected": {k: v["surface_detected"] for k, v in result["categories"].items()},
        "auth_semantics_proven": False,
        "final_or_play_ready": False,
    }, sort_keys=True))
    return 0 if health_json else 2

if __name__ == "__main__":
    sys.exit(main())
