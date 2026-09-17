#!/usr/bin/env python3
"""Remove deprecated Terra humanoid runtime fallbacks from the current source copy.

This patch is intentionally narrow: it only rewrites active runtime/config references
from thf_humanoid_v1..v6 to the approved Stage16A MPFB/MakeHuman asset, removes the
old avatar files from the active assets folder, and deletes generated Android/Godot
caches so stale exported resources cannot leak into a new candidate.

Historical release evidence is not rewritten; history belongs in release evidence,
not in active runtime fallbacks.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path.cwd()
CANONICAL_REL = Path("web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")
CANONICAL_RES = f"res://{CANONICAL_REL.as_posix()}"
CANONICAL_STATIC = "/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
CANONICAL_BARE = "thf_mpfb_stage16a_ual12_animated.glb"
LEGACY_RE = re.compile(r"thf_humanoid_v[1-6]\.glb", re.IGNORECASE)


def replacement_for(value: str) -> str:
    if not LEGACY_RE.search(value):
        return value
    if value.startswith("res://"):
        return LEGACY_RE.sub(CANONICAL_RES, value)
    if value.startswith("/static/"):
        return LEGACY_RE.sub(CANONICAL_STATIC, value)
    if "/" not in value and "\\" not in value:
        return LEGACY_RE.sub(CANONICAL_BARE, value)
    # Preserve surrounding path only when it is not a known avatar path.
    return LEGACY_RE.sub(CANONICAL_BARE, value)


def rewrite_json_value(value):
    if isinstance(value, str):
        return replacement_for(value)
    if isinstance(value, list):
        return [rewrite_json_value(v) for v in value]
    if isinstance(value, dict):
        return {k: rewrite_json_value(v) for k, v in value.items()}
    return value


def patch_text_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    updated = original
    updated = re.sub(
        r"res://web/static/assets/avatars/thf_humanoid_v[1-6]\.glb",
        CANONICAL_RES,
        updated,
        flags=re.IGNORECASE,
    )
    updated = re.sub(
        r"/static/assets/avatars/thf_humanoid_v[1-6]\.glb",
        CANONICAL_STATIC,
        updated,
        flags=re.IGNORECASE,
    )
    updated = LEGACY_RE.sub(CANONICAL_BARE, updated)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def active_text_candidates() -> list[Path]:
    candidates: list[Path] = []
    direct = [ROOT / "project.godot", ROOT / "export_presets.cfg"]
    candidates.extend([p for p in direct if p.is_file()])
    for base_name in ("native", "config", "web"):
        base = ROOT / base_name
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT).as_posix()
            # Keep historical evidence intact. It is excluded from active checks/package use.
            upper = p.name.upper()
            if (
                "RELEASE_MANIFEST" in upper
                or "PROVENANCE" in upper
                or "PACKAGE_SHA" in upper
                or rel.endswith("README_AR.md")
                or "/history/" in rel.lower()
            ):
                continue
            if p.suffix.lower() in {".gd", ".py", ".js", ".json", ".cfg", ".toml", ".yml", ".yaml", ".html", ".css", ".txt", ".tscn", ".tres"}:
                candidates.append(p)
    return candidates


def main() -> int:
    canonical = ROOT / CANONICAL_REL
    if not canonical.is_file():
        raise SystemExit(f"canonical MPFB asset missing: {CANONICAL_REL}")

    # Never trust old generated payloads as source authority.
    for generated in (
        ROOT / ".godot",
        ROOT / "android" / "build" / "build",
        ROOT / "android" / "build" / "src" / "main" / "assets",
    ):
        if generated.exists():
            shutil.rmtree(generated)

    deleted: list[str] = []
    avatar_dir = ROOT / "web" / "static" / "assets" / "avatars"
    if avatar_dir.exists():
        for p in avatar_dir.glob("thf_humanoid_v[1-6].glb*"):
            if p.is_file():
                deleted.append(p.relative_to(ROOT).as_posix())
                p.unlink()

    changed: list[str] = []
    for p in active_text_candidates():
        if p.suffix.lower() == ".json":
            try:
                original = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                if patch_text_file(p):
                    changed.append(p.relative_to(ROOT).as_posix())
                continue
            updated = rewrite_json_value(original)
            if updated != original:
                p.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                changed.append(p.relative_to(ROOT).as_posix())
        elif patch_text_file(p):
            changed.append(p.relative_to(ROOT).as_posix())

    # Exact runtime contract: WorldMain may only use the canonical human path for lite/remote fallback.
    world = ROOT / "native" / "world" / "WorldMain.gd"
    if world.is_file():
        text = world.read_text(encoding="utf-8")
        if "REMOTE_LITE_PATH" in text and CANONICAL_RES not in text:
            raise SystemExit("WorldMain REMOTE_LITE_PATH did not converge to canonical MPFB")

    # Active runtime/config source must now be legacy-free.
    residual: list[str] = []
    for p in active_text_candidates():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_RE.search(text):
            residual.append(p.relative_to(ROOT).as_posix())
    if residual:
        raise SystemExit("legacy humanoid active references remain: " + ", ".join(residual[:20]))

    report = {
        "status": "PASS",
        "canonical_avatar": CANONICAL_REL.as_posix(),
        "deleted_legacy_files": sorted(deleted),
        "patched_active_files": sorted(set(changed)),
        "generated_caches_removed": [
            ".godot",
            "android/build/build",
            "android/build/src/main/assets",
        ],
        "history_rewritten": False,
    }
    out = ROOT / "TERRA_MODERN_HUMAN_PATCH_RESULT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
