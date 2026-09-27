#!/usr/bin/env python3
"""Ephemeral HTTPS E2E gate for the immutable THF Fitness Backend V52 source.

The gate launches the exact extracted source with a temporary SQLite database and
TLS certificate, exercises only disposable non-privileged accounts, and emits a
machine-readable evidence record.  It never needs production credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _expect(response: httpx.Response, status: int, label: str) -> Any:
    if response.status_code != status:
        raise AssertionError(
            f"{label}: expected HTTP {status}, got {response.status_code}: "
            f"{response.text[:500]}"
        )
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return None


def _wait_ready(base_url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 25
    with httpx.Client(verify=False, timeout=2, trust_env=False) as client:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=3)
                raise RuntimeError(
                    f"backend exited before readiness ({process.returncode})\n"
                    f"stdout:\n{stdout}\nstderr:\n{stderr}"
                )
            try:
                response = client.get(f"{base_url}/health")
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.2)
    raise TimeoutError("backend did not become ready within 25 seconds")


def _register(client: httpx.Client, email: str, password: str) -> None:
    response = client.post(
        "/auth/register",
        data={"email": email, "password": password, "display_name": "Ephemeral QA"},
    )
    _expect(response, 303, "register")
    cookie = client.cookies.get("thf_fitness_session")
    if not cookie:
        raise AssertionError("registration did not establish the secure session cookie")


def _login(client: httpx.Client, email: str, password: str) -> None:
    _expect(
        client.post("/auth/login", data={"email": email, "password": password}),
        303,
        "login",
    )


def _run_gate(source_root: Path, source_sha256: str, output: Path) -> dict[str, Any]:
    if not (source_root / "app" / "main.py").is_file():
        raise FileNotFoundError(f"not a THF Fitness backend source: {source_root}")
    port = _free_port()
    base_url = f"https://127.0.0.1:{port}"
    steps: list[dict[str, Any]] = []

    def passed(name: str, **details: Any) -> None:
        steps.append({"name": name, "result": "PASS", **details})

    with tempfile.TemporaryDirectory(prefix="thf-backend-v52-e2e-") as tmp:
        root = Path(tmp)
        database = root / "fitness-e2e.db"
        certificate = root / "localhost.crt"
        private_key = root / "localhost.key"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-keyout",
                str(private_key),
                "-out",
                str(certificate),
                "-subj",
                "/CN=127.0.0.1",
                "-days",
                "1",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        env = os.environ.copy()
        env.update(
            {
                "DB_PATH": str(database),
                "THF_ENV": "production",
                "THF_PUBLIC_BASE_URL": base_url,
                "PYTHONUNBUFFERED": "1",
            }
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--ssl-keyfile",
                str(private_key),
                "--ssl-certfile",
                str(certificate),
                "--log-level",
                "warning",
            ],
            cwd=source_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            _wait_ready(base_url, process)
            passed("ephemeral_https_boot", tls=True, environment="production")

            account_tag = uuid.uuid4().hex
            email = f"fitness-e2e-{account_tag}@example.test"
            other_email = f"fitness-e2e-other-{account_tag}@example.test"
            password = "e2e-correct-horse-50002"
            common = {
                "base_url": base_url,
                "verify": False,
                "follow_redirects": False,
                "timeout": 10,
                "trust_env": False,
            }

            with httpx.Client(**common) as first, httpx.Client(**common) as second, httpx.Client(**common) as isolated:
                _expect(first.post("/api/sync", json={"cursor": 0}), 401, "unauthenticated sync")
                _expect(
                    first.post(
                        "/api/workouts/start",
                        json={"program_slug": "beginner-full-body", "day_index": 0},
                    ),
                    401,
                    "unauthenticated workout mutation",
                )
                passed("production_auth_boundary")

                _register(first, email, password)
                me = _expect(first.get("/api/me"), 200, "first session identity")
                user_id = str(me["user"]["id"])
                passed("disposable_registration_and_session")

                started = _expect(
                    first.post(
                        "/api/workouts/start",
                        json={"program_slug": "beginner-full-body", "day_index": 0},
                    ),
                    200,
                    "start workout",
                )
                session_id = int(started["session_id"])
                set_payload = {
                    "exercise_name": started["expectedExercise"],
                    "set_no": started["expectedSet"],
                    "reps": 10,
                    "load_kg": 12.5,
                    "duration_sec": 35,
                    "rir": 2,
                    "clientEventId": "https-e2e-set-0001",
                }
                accepted = _expect(
                    first.post(f"/api/workouts/{session_id}/sets", json=set_payload),
                    200,
                    "server-authoritative set",
                )
                if not accepted["accepted"] or accepted["idempotent"]:
                    raise AssertionError("first server-authoritative set was not newly accepted")
                replay = _expect(
                    first.post(f"/api/workouts/{session_id}/sets", json=set_payload),
                    200,
                    "idempotent set replay",
                )
                if not replay["idempotent"]:
                    raise AssertionError("set replay was not idempotent")
                passed("scoped_server_authoritative_workout_write", sessionId=session_id)

                stamp = 2_000_000_100
                health = {
                    "sourceId": "android.health.connect",
                    "sourceRecordId": "https-e2e-health-001",
                    "recordType": "steps",
                    "recordedStart": stamp,
                    "recordedEnd": stamp + 60,
                    "payload": {"count": 120},
                    "provenance": {
                        "provider": "Health Connect",
                        "appPackage": "com.topherofit.thf.pulse",
                        "capturedAt": stamp + 61,
                        "lastModifiedAt": stamp + 62,
                        "deviceIdHash": "a" * 64,
                    },
                }
                ingested = _expect(first.post("/api/health/records", json={"records": [health]}), 200, "health ingest")
                duplicate = _expect(first.post("/api/health/records", json={"records": [health]}), 200, "health dedup")
                if ingested["accepted"] != 1 or duplicate["deduplicated"] != 1:
                    raise AssertionError("Health Connect provenance/dedup contract failed")
                passed("health_provenance_and_dedup")

                _login(second, email, password)
                snapshot = _expect(second.post("/api/sync", json={"cursor": 0, "limit": 100}), 200, "second-client sync")
                sessions = snapshot["snapshot"]["sessions"]
                sets = snapshot["snapshot"]["sets"]
                health_records = snapshot["snapshot"]["healthRecords"]
                if not any(int(row["id"]) == session_id for row in sessions):
                    raise AssertionError("second client did not receive the workout session")
                if not any(int(row["session_id"]) == session_id for row in sets):
                    raise AssertionError("second client did not receive the accepted workout set")
                if len(health_records) != 1:
                    raise AssertionError("second client did not receive the deduplicated health record")
                passed("second_client_account_sync")

                _register(isolated, other_email, password)
                isolated_snapshot = _expect(
                    isolated.post("/api/sync", json={"cursor": 0, "limit": 100}),
                    200,
                    "isolated-account sync",
                )
                if isolated_snapshot["snapshot"]["sessions"] or isolated_snapshot["snapshot"]["healthRecords"]:
                    raise AssertionError("cross-account data leaked into an isolated account")
                passed("account_scope_isolation")

                _expect(first.post("/auth/logout"), 303, "logout")
                _expect(first.get("/api/me"), 401, "revoked first session")
                _expect(second.get("/api/me"), 200, "independent second session remains valid")
                passed("logout_session_revocation")

                deleted = _expect(second.post("/api/account/delete"), 200, "account deletion")
                if deleted != {"deleted": True}:
                    raise AssertionError("account deletion response is not explicit")
                _expect(second.get("/api/me"), 401, "all sessions revoked after deletion")
                _expect(
                    second.post("/auth/login", data={"email": email, "password": password}),
                    401,
                    "deleted-account login",
                )
                passed("account_deletion_and_global_session_revocation")

            with sqlite3.connect(database) as connection:
                deleted_at = connection.execute("SELECT deleted_at FROM users WHERE id=?", (user_id,)).fetchone()
                remaining_sessions = connection.execute(
                    "SELECT COUNT(*) FROM auth_sessions WHERE user_id=? AND revoked_at IS NULL", (user_id,)
                ).fetchone()[0]
                remaining_workouts = connection.execute(
                    "SELECT COUNT(*) FROM workout_sessions WHERE user_id=?", (user_id,)
                ).fetchone()[0]
                remaining_health = connection.execute(
                    "SELECT COUNT(*) FROM health_records WHERE user_id=?", (user_id,)
                ).fetchone()[0]
            if not deleted_at or remaining_sessions or remaining_workouts or remaining_health:
                raise AssertionError("account deletion did not purge product data and revoke all sessions")
            passed("deletion_persistence_audit")
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)

    evidence = {
        "schema": "thf-fitness-backend-v52-https-e2e-v1",
        "result": "PASS",
        "recordedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sourceSha256": source_sha256,
        "sourceRootManifestSha256": _sha256(source_root / "BACKEND_SUCCESSOR_V52.json"),
        "target": "ephemeral GitHub Actions runner / production mode / loopback TLS",
        "database": "ephemeral isolated SQLite",
        "credentials": "disposable non-privileged test-only accounts",
        "stepCount": len(steps),
        "steps": steps,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = _run_gate(args.source_root.resolve(), args.source_sha256, args.output.resolve())
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
