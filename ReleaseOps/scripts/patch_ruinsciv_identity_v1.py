#!/usr/bin/env python3
"""Apply and verify the final RuinsCiv public identity on an active source copy.

Historical evidence is intentionally left untouched. Active runtime/export/web/native
sources must not ship the superseded THF World/Terra package identity.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd()
OLD_PACKAGE = "com.topherofit.thf.terra"
NEW_PACKAGE = "com.topherofit.ruins.civ"
OLD_PUBLIC_NAMES = ("THF Terra", "THF World", "Nexus World")
NEW_PUBLIC_NAME = "RuinsCiv"
TEXT_SUFFIXES = {".gd", ".py", ".js", ".json", ".cfg", ".toml", ".yml", ".yaml", ".html", ".css", ".txt", ".tscn", ".tres", ".gradle", ".properties", ".xml", ".java", ".kt", ".md"}

ACTIVE_ROOTS = [
    "project.godot", "export_presets.cfg", "native", "web", "config", "android", "app",
]

def candidates():
    for item in ACTIVE_ROOTS:
        p = ROOT / item
        if p.is_file():
            yield p
        elif p.is_dir():
            for q in p.rglob("*"):
                if not q.is_file():
                    continue
                rel = q.relative_to(ROOT).as_posix().lower()
                if any(x in rel for x in ("/build/", "/.godot/", "/history/", "/logs/")):
                    continue
                if q.suffix.lower() in TEXT_SUFFIXES or q.name in {"AndroidManifest.xml"}:
                    yield q

def main() -> int:
    changed = []
    for p in candidates():
        try:
            old = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = old.replace(OLD_PACKAGE, NEW_PACKAGE)
        for name in OLD_PUBLIC_NAMES:
            new = new.replace(name, NEW_PUBLIC_NAME)
        if p.name == "project.godot":
            new = re.sub(r'(?m)^config/name="[^"]*"$', 'config/name="RuinsCiv"', new, count=1)
        if p.name == "export_presets.cfg":
            new = re.sub(r'package/unique_name="[^"]*"', f'package/unique_name="{NEW_PACKAGE}"', new)
        if new != old:
            p.write_text(new, encoding="utf-8")
            changed.append(p.relative_to(ROOT).as_posix())

    residual_package = []
    residual_brand = []
    for p in candidates():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if OLD_PACKAGE in text:
            residual_package.append(rel)
        if any(name in text for name in OLD_PUBLIC_NAMES):
            residual_brand.append(rel)

    if residual_package:
        raise SystemExit("legacy package remains in active source: " + ", ".join(residual_package[:30]))
    if residual_brand:
        raise SystemExit("legacy public brand remains in active source: " + ", ".join(residual_brand[:30]))

    report = {
        "status": "PASS",
        "final_name": NEW_PUBLIC_NAME,
        "final_package_id": NEW_PACKAGE,
        "legacy_package_id": OLD_PACKAGE,
        "legacy_public_names": list(OLD_PUBLIC_NAMES),
        "patched_active_files": sorted(set(changed)),
        "legacy_package_in_active_source": False,
        "legacy_public_brand_in_active_source": False,
        "historical_evidence_rewritten": False,
    }
    (ROOT / "RUINSCIV_IDENTITY_PATCH_RESULT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
