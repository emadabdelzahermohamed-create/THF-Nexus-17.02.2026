#!/usr/bin/env python3
"""V13 physical-phone evidence validator for THF games.

Extends V12 by validating the semantics of each bounded raw ADB stdout payload,
not only its metadata binding. Offline capture must have connectivity-shaped
output with no VALIDATED network; local capture must contain a uiautomator
hierarchy for the exact game package; restored-online capture must contain a
VALIDATED network. This gate is fail-closed and never promotes FINAL/PLAY_READY.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("thf_device_v12", HERE / "validate_game_device_evidence_v12.py")
V12 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = V12
SPEC.loader.exec_module(V12)
V3, V4 = V12.V3, V12.V4

STDOUT_BEGIN = "THF_ADB_STDOUT_BEGIN"
STDOUT_END = "THF_ADB_STDOUT_END"
VALIDATED_RE = re.compile(r"(?:^|[\s,;:\[\]()])VALIDATED(?:$|[\s,;:\[\]()])", re.IGNORECASE)


def _stdout(text: str) -> str | None:
    if text.count(STDOUT_BEGIN) != 1 or text.count(STDOUT_END) != 1:
        return None
    start = text.index(STDOUT_BEGIN) + len(STDOUT_BEGIN)
    end = text.index(STDOUT_END)
    if end <= start:
        return None
    payload = text[start:end].strip()
    return payload if payload else None


def _connectivity_shape(payload: str) -> bool:
    lower = payload.lower()
    return any(marker in lower for marker in ("networkagentinfo", "networkcapabilities", "networkrequest", "connectivity"))


def validate_bundle(registry: dict, registry_sha: str, evidence: dict, root: Path) -> list[str]:
    errors = list(V12.validate_bundle(registry, registry_sha, evidence, root))
    row = V12._candidate(registry, evidence.get("product"))
    if row is None:
        errors.append("V13 requires exactly one authoritative candidate")
        return errors
    obs = evidence.get("offline_network_observation")
    raw = obs.get("raw_captures") if isinstance(obs, dict) else None
    if not isinstance(raw, dict) or set(raw) != set(V12.RAW_ORDER):
        errors.append("V13 requires V12 offline/local/online raw captures")
        return errors

    payloads: dict[str, str] = {}
    for kind in V12.RAW_ORDER:
        item = raw.get(kind)
        p = V4._safe_evidence_path(root, item.get("evidence_ref") if isinstance(item, dict) else None)
        if p is None or not p.is_file():
            errors.append(f"V13 raw {kind} evidence file required")
            continue
        payload = _stdout(p.read_text(encoding="utf-8", errors="replace"))
        if payload is None:
            errors.append(f"V13 raw {kind} bounded ADB stdout required")
            continue
        payloads[kind] = payload

    offline = payloads.get("offline")
    if offline is not None:
        if not _connectivity_shape(offline):
            errors.append("V13 offline raw stdout lacks connectivity structure")
        if VALIDATED_RE.search(offline):
            errors.append("V13 offline raw stdout unexpectedly contains VALIDATED network")

    online = payloads.get("online")
    if online is not None:
        if not _connectivity_shape(online):
            errors.append("V13 online raw stdout lacks connectivity structure")
        if VALIDATED_RE.search(online) is None:
            errors.append("V13 online raw stdout must contain VALIDATED network")

    local = payloads.get("local")
    if local is not None:
        package = str(row.get("package") or "")
        if "<hierarchy" not in local or "<node" not in local:
            errors.append("V13 local raw stdout must contain uiautomator hierarchy")
        if not package or re.search(rf'\bpackage=["\']{re.escape(package)}["\']', local) is None:
            errors.append("V13 local raw stdout must contain exact game package")

    if evidence.get("final_or_play_ready") is not False:
        errors.append("V13 cannot self-promote FINAL/PLAY_READY")
    return errors


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("registry", type=Path); ap.add_argument("evidence", type=Path); ap.add_argument("evidence_root", type=Path); ns = ap.parse_args()
    registry, registry_sha = V3.load_json(ns.registry); evidence, _ = V3.load_json(ns.evidence)
    errors = validate_bundle(registry, registry_sha, evidence, ns.evidence_root)
    if errors:
        for e in errors: print("ERROR: " + e, file=sys.stderr)
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V13=FAIL\nFINAL_OR_PLAY_READY=FALSE"); return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V13=PASS")
    print(f"PRODUCT={evidence['product']}\nEXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("RAW_ADB_SEMANTIC_VALIDATION=TRUE\nFINAL_OR_PLAY_READY=FALSE"); return 0


if __name__ == "__main__": raise SystemExit(main())
