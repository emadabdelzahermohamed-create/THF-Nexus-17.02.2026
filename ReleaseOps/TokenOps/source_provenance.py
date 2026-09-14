#!/usr/bin/env python3
"""Deterministic provenance manifest for the THF TokenOps control plane.

Hashes only the explicit TokenOps control-plane inventory plus its workflows.
WAVE and unrelated repository areas are intentionally outside this inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
from typing import Any, Dict

from tokenops_guard import scan_for_secrets, sha256

SCHEMA = "thf-tokenops-source-provenance/v1"
INVENTORY = (
    ".github/workflows/thf-tokenops-autonomous-large-batch-v3.yml",
    ".github/workflows/thf-tokenops-policy-governance-gate-v1.yml",
    ".github/workflows/thf-tokenops-evidence-chain-gate-v1.yml",
    ".github/workflows/thf-tokenops-holder-concentration-probe-v1.yml",
    ".github/workflows/thf-tokenops-rpc-capability-gate-v1.yml",
    ".github/workflows/thf-tokenops-incident-response-gate-v1.yml",
    ".github/workflows/thf-tokenops-integration-contract-gate-v1.yml",
    "ReleaseOps/TokenOps/policy.json",
    "ReleaseOps/TokenOps/treasury_policy.json",
    "ReleaseOps/TokenOps/treasury_registry.json",
    "ReleaseOps/TokenOps/integration_contracts.json",
    "ReleaseOps/TokenOps/INCIDENT_RUNBOOK.md",
    "ReleaseOps/TokenOps/tokenops_guard.py",
    "ReleaseOps/TokenOps/financial_control_plane.py",
    "ReleaseOps/TokenOps/activity_planning.py",
    "ReleaseOps/TokenOps/epoch_commitment.py",
    "ReleaseOps/TokenOps/revenue_value_basis.py",
    "ReleaseOps/TokenOps/blocker_resolution.py",
    "ReleaseOps/TokenOps/operation_readiness.py",
    "ReleaseOps/TokenOps/review_intent_manifest.py",
    "ReleaseOps/TokenOps/policy_change_control.py",
    "ReleaseOps/TokenOps/recent_activity_semantics.py",
    "ReleaseOps/TokenOps/rpc_capability_probe.py",
    "ReleaseOps/TokenOps/holder_concentration_probe.py",
    "ReleaseOps/TokenOps/evidence_chain.py",
    "ReleaseOps/TokenOps/incident_response.py",
    "ReleaseOps/TokenOps/integration_contract_gate.py",
    "ReleaseOps/TokenOps/test_integration_contract_gate.py",
    "ReleaseOps/TokenOps/source_provenance.py",
)


def file_sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_provenance(repo_root: pathlib.Path, commit_sha: str | None = None) -> Dict[str, Any]:
    files: Dict[str, str] = {}
    missing = []
    for rel in INVENTORY:
        path = repo_root / rel
        if not path.is_file():
            missing.append(rel)
        else:
            files[rel] = file_sha256(path)
    if missing:
        raise ValueError("missing required TokenOps provenance inputs: " + ",".join(missing))
    root_material = [{"path": p, "sha256": files[p]} for p in sorted(files)]
    result: Dict[str, Any] = {
        "schema": SCHEMA,
        "source_commit_sha": commit_sha or None,
        "inventory_count": len(files),
        "files": dict(sorted(files.items())),
        "tokenops_source_root_sha256": sha256(root_material),
        "scope": "ReleaseOps/TokenOps plus dedicated TokenOps workflows only",
        "wave_in_inventory": any("wave" in p.lower() for p in files),
        "financial_effect": False,
        "broadcast": False,
        "private_key_used": False,
        "wave_touched": False,
    }
    scan_for_secrets(result)
    result["provenance_sha256"] = sha256(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default="out/tokenops-v3/source-provenance.json")
    args = ap.parse_args()
    result = build_provenance(pathlib.Path(args.repo_root), os.getenv("GITHUB_SHA"))
    if result["wave_in_inventory"]:
        raise SystemExit("WAVE path unexpectedly entered TokenOps provenance inventory")
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("TOKENOPS_SOURCE_ROOT_SHA256=" + result["tokenops_source_root_sha256"])
    print("TOKENOPS_SOURCE_INVENTORY_COUNT=" + str(result["inventory_count"]))
    print("WAVE_IN_PROVENANCE_INVENTORY=" + str(result["wave_in_inventory"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
