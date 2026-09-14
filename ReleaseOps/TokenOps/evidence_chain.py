#!/usr/bin/env python3
"""THF TokenOps immutable evidence-chain and freshness gate.

Binds a fresh read-only Mainnet audit to invariant/readiness/provenance evidence and
canonical policy files. This module never creates transaction/instruction bytes and
cannot sign, submit, broadcast, transfer, burn, settle, or mutate policy.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

from tokenops_guard import MINT, NETWORK, TOKEN_PROGRAM, DECIMALS, scan_for_secrets, sha256

SCHEMA = "thf-tokenops-evidence-chain/v1"
MAX_AUDIT_AGE_SECONDS = 15 * 60
MAX_FUTURE_SKEW_SECONDS = 120


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("observed_at_utc must be timezone-aware")
    return parsed.astimezone(dt.timezone.utc)


def recompute_embedded_sha(obj: Dict[str, Any], field: str) -> str:
    copy = dict(obj)
    copy.pop(field, None)
    return sha256(copy)


def build_chain(
    audit: Dict[str, Any],
    gate: Dict[str, Any],
    readiness: Dict[str, Any],
    provenance: Dict[str, Any],
    policy: Dict[str, Any],
    treasury_policy: Dict[str, Any],
    *,
    now: dt.datetime | None = None,
    source_commit_sha: str | None = None,
    component_file_hashes: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    for value in (audit, gate, readiness, provenance, policy, treasury_policy):
        scan_for_secrets(value)

    current = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    observed = parse_utc(str(audit.get("observed_at_utc")))
    age_seconds = (current - observed).total_seconds()

    checks = {
        "audit_fresh": -MAX_FUTURE_SKEW_SECONDS <= age_seconds <= MAX_AUDIT_AGE_SECONDS,
        "network": audit.get("network") == NETWORK,
        "mint": audit.get("mint") == MINT,
        "program": audit.get("program_id") == TOKEN_PROGRAM,
        "decimals": int(audit.get("decimals", -1)) == DECIMALS,
        "mint_authority_disabled": audit.get("mint_authority") is None,
        "freeze_authority_disabled": audit.get("freeze_authority") is None,
        "audit_sha_self_consistent": audit.get("audit_sha256") == recompute_embedded_sha(audit, "audit_sha256"),
        "invariant_gate_pass": gate.get("status") == "PASS" and not gate.get("failed"),
        "readiness_binds_audit": readiness.get("audit_sha256") == audit.get("audit_sha256"),
        "readiness_binds_policy": readiness.get("policy_sha256") == sha256(policy),
        "readiness_binds_treasury_policy": readiness.get("treasury_policy_sha256") == sha256(treasury_policy),
        "provenance_wave_excluded": provenance.get("wave_in_inventory") is False and provenance.get("wave_touched") is False,
        "provenance_no_financial_effect": provenance.get("financial_effect") is False and provenance.get("broadcast") is False,
    }
    if source_commit_sha:
        checks["provenance_binds_commit"] = provenance.get("source_commit_sha") == source_commit_sha

    failed = sorted(name for name, ok in checks.items() if not ok)
    components = dict(sorted((component_file_hashes or {}).items()))
    root_material = {
        "schema": SCHEMA,
        "source_commit_sha": source_commit_sha or provenance.get("source_commit_sha"),
        "tokenops_source_root_sha256": provenance.get("tokenops_source_root_sha256"),
        "audit_sha256": audit.get("audit_sha256"),
        "gate_sha256": gate.get("gate_sha256"),
        "readiness_sha256": sha256(readiness),
        "policy_sha256": sha256(policy),
        "treasury_policy_sha256": sha256(treasury_policy),
        "components": components,
    }
    result = {
        "schema": SCHEMA,
        "status": "PASS" if not failed else "FAIL_CLOSED",
        "observed_at_utc": audit.get("observed_at_utc"),
        "evaluated_at_utc": current.isoformat(),
        "audit_age_seconds": round(age_seconds, 3),
        "max_audit_age_seconds": MAX_AUDIT_AGE_SECONDS,
        "checks": checks,
        "failed": failed,
        "evidence_root_sha256": sha256(root_material),
        "root_material": root_material,
        "execution_authorized": False,
        "transaction_bytes_created": False,
        "instruction_bytes_created": False,
        "signed": False,
        "submitted": False,
        "broadcast": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_touched": False,
    }
    scan_for_secrets(result)
    result["chain_packet_sha256"] = sha256(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", default="out/tokenops-v3")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default="out/tokenops-v3/evidence-chain.json")
    args = ap.parse_args()
    evidence_dir = Path(args.evidence_dir)
    repo_root = Path(args.repo_root)
    names = ["token-audit.json", "invariant-gate.json", "financial-readiness.json", "source-provenance.json"]
    objs = [json.loads((evidence_dir / n).read_text()) for n in names]
    policy = json.loads((repo_root / "ReleaseOps/TokenOps/policy.json").read_text())
    treasury_policy = json.loads((repo_root / "ReleaseOps/TokenOps/treasury_policy.json").read_text())
    hashes = {n: file_sha256(evidence_dir / n) for n in names}
    packet = build_chain(*objs, policy, treasury_policy, source_commit_sha=os.getenv("GITHUB_SHA"), component_file_hashes=hashes)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n")
    print("EVIDENCE_CHAIN_STATUS=" + packet["status"])
    print("EVIDENCE_ROOT_SHA256=" + packet["evidence_root_sha256"])
    print("AUDIT_AGE_SECONDS=" + str(packet["audit_age_seconds"]))
    if packet["failed"]:
        print("EVIDENCE_CHAIN_FAILED=" + ",".join(packet["failed"]))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
