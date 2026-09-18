#!/usr/bin/env python3
"""Fail-closed RuinsCiv release identity/export gate.

Run against the exact recovered RC34-or-better Godot work tree before any new
APK/AAB/web release. This gate never rewrites source; it rejects superseded
identity/resource leakage and WAVE secret reuse.
"""
from __future__ import annotations
import argparse
import pathlib
import re
import sys

PROD = "com.topherofit.ruins.civ"
QA = "com.topherofit.ruins.civ.phoneqa"
FORBIDDEN_TEXT = (
    "com.topherofit.thf.terra",
    "com.topherofit.thf.terra.phoneqa",
)
FORBIDDEN_ACTIVE_ASSET = re.compile(r"thf_humanoid_v[1-6](?:\.|\b)", re.I)
WAVE_SECRET = re.compile(r"\b(?:WAVE|WAVE_MAWJA)_[A-Z0-9_]*(?:SECRET|CLIENT|TOKEN|KEY)[A-Z0-9_]*\b")
OAUTH_SECRET = re.compile(r"\b[A-Z][A-Z0-9_]*(?:OAUTH|CLIENT|SECRET)[A-Z0-9_]*\b")
TEXT_EXT = {".cfg", ".gd", ".tscn", ".tres", ".json", ".yml", ".yaml", ".xml", ".html", ".js", ".ts", ".md", ".txt", ".env", ".properties", ".gradle", ".kts"}


def text_files(root: pathlib.Path):
    for p in root.rglob("*"):
        if p.is_file() and (p.suffix.lower() in TEXT_EXT or p.name in {"project.godot", "AndroidManifest.xml"}):
            yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=pathlib.Path)
    ap.add_argument("--surface", choices=("qa", "production"), required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    expected = QA if args.surface == "qa" else PROD
    errors: list[str] = []
    package_seen = False
    mpfb_seen = False

    if not (root / "project.godot").is_file():
        errors.append("project.godot missing")

    for p in text_files(root):
        try:
            s = p.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue
        rel = p.relative_to(root)
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in s:
                errors.append(f"superseded identity {forbidden!r} present in {rel}")
        if FORBIDDEN_ACTIVE_ASSET.search(s):
            errors.append(f"forbidden legacy humanoid v1..v6 reference present in {rel}")
        if WAVE_SECRET.search(s):
            errors.append(f"WAVE secret namespace reference present in {rel}")
        for token in OAUTH_SECRET.findall(s):
            if ("OAUTH" in token or "CLIENT" in token or "SECRET" in token) and not token.startswith("RUINSCIV_"):
                # Only enforce app-level uppercase secret-style identifiers.
                if token.startswith(("GOOGLE_", "APPLE_", "FACEBOOK_", "MICROSOFT_", "DISCORD_")):
                    errors.append(f"OAuth secret identifier must use RUINSCIV_* namespace: {token} in {rel}")
        if expected in s:
            package_seen = True
        if re.search(r"(?:mpfb|makehuman)", s, re.I):
            mpfb_seen = True

    # Scan path names too; binary payloads need not be decoded to catch legacy model filenames.
    for p in root.rglob("*"):
        if FORBIDDEN_ACTIVE_ASSET.search(p.name):
            errors.append(f"forbidden legacy humanoid file in candidate tree: {p.relative_to(root)}")
        if re.search(r"(?:mpfb|makehuman)", p.name, re.I):
            mpfb_seen = True

    if not package_seen:
        errors.append(f"expected package {expected!r} not proven in source/export configuration")
    if not mpfb_seen:
        errors.append("approved MPFB/MakeHuman runtime asset/reference not proven")

    if errors:
        print("RUINSCIV_RELEASE_IDENTITY_GATE=FAIL")
        for e in sorted(set(errors)):
            print(f"FAIL: {e}")
        return 2
    print("RUINSCIV_RELEASE_IDENTITY_GATE=PASS")
    print(f"surface={args.surface}")
    print(f"expected_package={expected}")
    print("legacy_humanoid_v1_v6=ABSENT")
    print("superseded_terra_identity=ABSENT")
    print("wave_secret_namespace=ABSENT")
    print("mpfb_makehuman_reference=PRESENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
