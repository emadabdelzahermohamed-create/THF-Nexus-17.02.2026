#!/usr/bin/env python3
"""Create a reversible mobile-settings overlay on a disposable THF Terra/Rift tree.

This tool NEVER edits canonical archives. It changes only project.godot in the supplied
clean-extracted candidate tree and emits non-secret evidence. Network endpoints are
intentionally not rewritten: localhost/placeholder markers remain a separate authority gate.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, sys

TARGETS = {
    "window/handheld/orientation": "4",  # Godot SCREEN_SENSOR_LANDSCAPE
    "window/stretch/aspect": '"expand"',
}
OVERRIDES = {
    "window/size/window_width_override",
    "window/size/window_height_override",
    "window_width_override",
    "window_height_override",
}
TEXT_EXT = {".gd", ".godot", ".cfg", ".ini", ".json", ".tscn", ".tres"}
PLACEHOLDER_RE = re.compile(
    r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?|"
    r"wss?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?|"
    r"REPLACE[_ -]?ME|YOUR[_ -]?(?:API|URL|HOST)|placeholder[_ -]?(?:url|endpoint)",
    re.I,
)

def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def project_file(root: pathlib.Path) -> pathlib.Path:
    found = sorted(root.rglob("project.godot"))
    if len(found) != 1:
        raise SystemExit(f"expected exactly one project.godot, found {len(found)}")
    return found[0]

def patch_project(p: pathlib.Path) -> dict:
    before = sha256(p)
    lines = p.read_text(errors="strict").splitlines()
    display_start = None
    display_end = len(lines)
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "[display]":
            display_start = i
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith("[") and lines[j].strip().endswith("]"):
                    display_end = j
                    break
            break
    if display_start is None:
        if lines and lines[-1].strip():
            lines.append("")
        display_start = len(lines)
        lines.append("[display]")
        display_end = len(lines)

    changed = []
    present = set()
    for i in range(display_start + 1, display_end):
        raw = lines[i]
        if "=" not in raw or raw.lstrip().startswith((";", "#")):
            continue
        key = raw.split("=", 1)[0].strip()
        if key in TARGETS:
            present.add(key)
            wanted = f"{key}={TARGETS[key]}"
            if raw.strip() != wanted:
                lines[i] = wanted
                changed.append(key)
        elif key in OVERRIDES:
            wanted = f"{key}=0"
            if raw.strip() != wanted:
                lines[i] = wanted
                changed.append(key)

    insert_at = display_end
    additions = []
    for key, value in TARGETS.items():
        if key not in present:
            additions.append(f"{key}={value}")
            changed.append(key)
    if additions:
        lines[insert_at:insert_at] = additions

    p.write_text("\n".join(lines) + "\n")
    after = sha256(p)
    return {
        "project_path": p.as_posix(),
        "project_sha256_before": before,
        "project_sha256_after": after,
        "changed_keys": sorted(set(changed)),
        "changed": before != after,
    }

def endpoint_inventory(root: pathlib.Path) -> dict:
    paths = []
    marker_count = 0
    runtime_config_markers = 0
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        hits = PLACEHOLDER_RE.findall(text)
        if hits:
            marker_count += len(hits)
            paths.append(p.relative_to(root).as_posix())
        if re.search(r"OS\.get_environment|ProjectSettings\.get_setting|THF_(?:BASE|API|WS|WORLD|ARENA)_URL", text, re.I):
            runtime_config_markers += 1
    return {
        "placeholder_marker_count": marker_count,
        "placeholder_paths": sorted(set(paths)),
        "runtime_config_file_count": runtime_config_markers,
        "endpoint_values_redacted": True,
        "network_authority_gate": "PASS" if marker_count == 0 else "BLOCKED",
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--kind", choices=["terra", "rift"], required=True)
    ap.add_argument("--json-out", required=True)
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    if not root.is_dir():
        raise SystemExit("candidate root missing")
    pf = project_file(root)
    patch = patch_project(pf)
    net = endpoint_inventory(root)
    result = {
        "schema": "thf-terra-rift-mobile-overlay-v1",
        "kind": a.kind,
        "candidate_only": True,
        "canonical_archive_mutated": False,
        "mobile_settings": patch,
        "network": net,
        "device_status": "PENDING",
        "final_status": "NOT_FINAL",
    }
    pathlib.Path(a.json_out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
