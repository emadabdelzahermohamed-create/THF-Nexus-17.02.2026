#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import stat
import sys
import zipfile
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: package_authoritative_android_source_v2.py <project-root> <output.zip>")

project = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
if not project.is_dir():
    raise SystemExit(f"missing project directory: {project}")

EXCLUDED_DIRS = {
    ".git", ".gradle", ".idea", "build", "captures", "out", "gradle-home"
}
EXCLUDED_NAMES = {
    "local.properties", ".DS_Store"
}
EXCLUDED_SUFFIXES = {
    ".apk", ".aab", ".keystore", ".jks", ".p12", ".der", ".pem", ".key"
}

files: list[Path] = []
for p in project.rglob("*"):
    rel = p.relative_to(project)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        continue
    if p.is_dir():
        continue
    if p.name in EXCLUDED_NAMES or p.suffix.lower() in EXCLUDED_SUFFIXES:
        continue
    if p.is_symlink():
        raise SystemExit(f"symlink forbidden in canonical source: {rel}")
    files.append(p)

if not files:
    raise SystemExit("canonical source would be empty")

out.parent.mkdir(parents=True, exist_ok=True)
if out.exists():
    out.unlink()

fixed_time = (2026, 9, 14, 0, 0, 0)
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for p in sorted(files, key=lambda x: x.relative_to(project).as_posix()):
        rel = p.relative_to(project).as_posix()
        data = p.read_bytes()
        info = zipfile.ZipInfo(rel, fixed_time)
        info.create_system = 3
        mode = stat.S_IFREG | (0o755 if os.access(p, os.X_OK) else 0o644)
        info.external_attr = mode << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        info.flag_bits |= 0x800
        zf.writestr(info, data)

with zipfile.ZipFile(out, "r") as zf:
    names = zf.namelist()
    if len(names) != len(set(names)):
        raise SystemExit("duplicate paths in canonical source")
    if any(name.startswith("/") or "../" in name or name.endswith("/") for name in names):
        raise SystemExit("unsafe path in canonical source")
    if any("/build/" in f"/{name}" or name.startswith("build/") for name in names):
        raise SystemExit("build output leaked into canonical source")
    if any(name.endswith((".apk", ".aab", ".jks", ".keystore", ".p12", ".pem", ".key")) for name in names):
        raise SystemExit("binary/signing material leaked into canonical source")
    if not any(name.endswith("AndroidManifest.xml") for name in names):
        raise SystemExit("AndroidManifest.xml missing")
    if not any(name.endswith("MainActivity.java") for name in names):
        raise SystemExit("native MainActivity.java missing")

sha = hashlib.sha256(out.read_bytes()).hexdigest()
print(f"canonical_source_path={out}")
print(f"canonical_source_sha256={sha}")
print(f"canonical_source_files={len(files)}")
print("canonical_source_clean=PASS")
