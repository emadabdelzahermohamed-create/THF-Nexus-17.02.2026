#!/usr/bin/env python3
"""Fail closed on arbitrary repository-defined artifact size caps.

THF policy: artifact size is telemetry/optimization, not a reason to delete validated
content. Real provider/platform constraints may be documented, but must be explicitly
marked EXTERNAL_PLATFORM_LIMIT and must not silently prune content.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN_ROOTS = [ROOT / ".github", ROOT / "ReleaseOps"]
SELF = pathlib.Path(__file__).resolve()
TEXT_SUFFIXES = {".yml", ".yaml", ".py", ".sh", ".md", ".json", ".txt"}

# Build legacy literals without embedding them verbatim in this validator.
LEGACY_BYTES = str(100 * 1024 * 1024)
LEGACY_TEXT = "100" + "MB"
LEGACY_TEXT_SPACED = "100" + " MB"

# Hard-gate indicators. Size reporting/advisory text is allowed.
HARD_WORDS = re.compile(
    r"(?i)(fail|exit\s+1|raise|error|reject|abort|maximum|max[_ -]?(?:apk|aab|artifact|file)?[_ -]?size|size[_ -]?limit|too[_ -]?large)"
)
SIZE_WORDS = re.compile(r"(?i)(apk|aab|artifact|bundle|package|file).{0,40}(size|bytes|mb)|(?:size|bytes|mb).{0,40}(apk|aab|artifact|bundle|package|file)")
EXTERNAL_MARKER = "EXTERNAL_PLATFORM_LIMIT"

violations: list[str] = []
checked = 0
for base in SCAN_ROOTS:
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if not path.is_file() or path.resolve() == SELF or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked += 1
        lines = text.splitlines()
        for idx, line in enumerate(lines, 1):
            compact = line.replace(" ", "")
            has_legacy = LEGACY_BYTES in line or LEGACY_TEXT.lower() in compact.lower() or LEGACY_TEXT_SPACED.lower() in line.lower()
            if not has_legacy:
                continue
            window = "\n".join(lines[max(0, idx - 3): min(len(lines), idx + 2)])
            if EXTERNAL_MARKER in window:
                continue
            if HARD_WORDS.search(window) and SIZE_WORDS.search(window):
                violations.append(f"{path.relative_to(ROOT)}:{idx}: arbitrary hard artifact-size cap")

print(f"THF_SIZE_POLICY_FILES_CHECKED={checked}")
print("THF_ARBITRARY_SIZE_CAP_POLICY=NO_CONTENT_PRUNING_FOR_REPOSITORY_DEFINED_LIMITS")
if violations:
    print("THF_ARBITRARY_SIZE_CAP_GATE=FAIL")
    for item in violations:
        print(item)
    print(f"THF_ARBITRARY_SIZE_CAP_VIOLATIONS={len(violations)}")
    sys.exit(1)

print("THF_ARBITRARY_SIZE_CAP_VIOLATIONS=0")
print("THF_ARBITRARY_SIZE_CAP_GATE=PASS")
print("THF_SIZE_OPTIMIZATION_MODE=ADVISORY_OR_LOSSLESS")
print("THF_VALIDATED_CONTENT_PRUNING_FOR_SIZE=FORBIDDEN")
