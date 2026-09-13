#!/usr/bin/env python3
"""THF mobile release gate.

Static/package checks are intentionally strict. A PASS here is necessary but not
sufficient: FINAL/PLAY_READY also requires exact-candidate physical-device evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path

BAD_PLACEHOLDERS = (
    "YOUR-PRODUCTION-DOMAIN.example",
    "PROJECT_ID: 'my-project'",
    "SERVICE: 'my-service'",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_tree(root: Path) -> str:
    chunks=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.stat().st_size > 2_000_000:
            continue
        if p.suffix.lower() not in {'.gradle','.kts','.xml','.json','.toml','.properties','.godot','.gd','.kt','.java','.yml','.yaml','.md','.txt'}:
            continue
        try: chunks.append(p.read_text('utf-8', errors='ignore'))
        except OSError: pass
    return '\n'.join(chunks)


def apk_payload_gate(apk: Path, kind: str) -> list[str]:
    errs=[]
    if not apk.exists(): return [f"APK missing: {apk}"]
    if not zipfile.is_zipfile(apk): return ["APK is not a valid ZIP/APK"]
    with zipfile.ZipFile(apk) as z:
        names=z.namelist()
        if 'AndroidManifest.xml' not in names: errs.append('APK manifest missing')
        if kind == 'game':
            has_godot = any('libgodot_android.so' in n for n in names)
            if has_godot:
                assets=[n for n in names if n.startswith('assets/')]
                project_payload=[n for n in names if n.endswith(('.pck','project.binary','project.godot')) or '/.godot/' in n]
                if not assets and not project_payload:
                    errs.append('Godot template/engine APK has no exported game payload/assets')
    return errs


def source_gate(root: Path, kind: str, online_required: bool) -> list[str]:
    errs=[]
    text=read_tree(root)
    if not re.search(r'targetSdk\s*(?:=|\s)\s*36|target_sdk\s*=\s*36', text):
        errs.append('targetSdk 36 evidence not found')
    if online_required and any(x in text for x in BAD_PLACEHOLDERS):
        errs.append('production placeholder remains in network/deploy configuration')
    if kind == 'game':
        projects=list(root.rglob('project.godot'))
        if len(projects) != 1:
            errs.append(f'exactly one project.godot required for game source; found {len(projects)}')
        else:
            pgt=projects[0].read_text('utf-8', errors='ignore')
            if 'window/handheld/orientation=1' in pgt:
                errs.append('portrait orientation is forbidden for THF Terra/Rift landscape games')
            if 'window/handheld/orientation=4' not in pgt:
                errs.append('sensor-landscape orientation=4 required for THF Terra/Rift phone builds')
            if 'window/stretch/aspect="expand"' not in pgt:
                errs.append('mobile stretch aspect=expand required')
            if 'window/size/window_width_override' in pgt or 'window/size/window_height_override' in pgt:
                errs.append('desktop window override found in mobile game source')
        # Touch input must be present in game source; desktop-only keyboard/mouse shells are rejected.
        touch_markers=('InputEventScreenTouch','InputEventScreenDrag','TouchScreenButton','screen_touch','screen_drag')
        if not any(m in text for m in touch_markers):
            errs.append('touch-control evidence not found in game source')
    return errs


def device_gate(path: Path|None, kind: str, online_required: bool, expected_sha256: str|None) -> list[str]:
    if path is None or not path.exists():
        return ['physical-device acceptance evidence missing']
    try: d=json.loads(path.read_text('utf-8'))
    except Exception as e: return [f'invalid device evidence: {e}']
    required=['exact_candidate_sha256','install_pass','launch_pass','touch_pass','orientation_layout_pass','background_resume_pass','offline_network_transition_pass','crash_free_smoke_pass','core_user_journey_pass']
    if online_required: required += ['backend_https_pass','backend_health_auth_pass']
    if kind == 'game': required += ['avatar_or_player_load_pass','movement_camera_pass','gameplay_interaction_pass','fps_ram_thermal_observed']
    errs=[]
    for k in required:
        v=d.get(k)
        if k=='exact_candidate_sha256':
            if not isinstance(v,str) or not re.fullmatch(r'[0-9a-fA-F]{64}',v):
                errs.append(f'{k}=missing/invalid')
            elif expected_sha256 and v.lower() != expected_sha256.lower():
                errs.append(f'exact candidate SHA mismatch: evidence={v.lower()} apk={expected_sha256.lower()}')
        elif v is not True:
            errs.append(f'{k} != true')
    return errs


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--product', required=True)
    ap.add_argument('--kind', choices=['app','game'], required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--apk')
    ap.add_argument('--device-evidence')
    ap.add_argument('--online-required', action='store_true')
    a=ap.parse_args()
    root=Path(a.source)
    errs=[]
    if not root.is_dir(): errs.append('source directory missing')
    else: errs += source_gate(root,a.kind,a.online_required)
    apk_sha=None
    if a.apk:
        apk=Path(a.apk)
        errs += apk_payload_gate(apk,a.kind)
        if apk.exists() and apk.is_file():
            apk_sha=sha256_file(apk)
    else:
        errs.append('installable APK package evidence missing')
    errs += device_gate(Path(a.device_evidence) if a.device_evidence else None,a.kind,a.online_required,apk_sha)
    result={'product':a.product,'status':'PASS' if not errs else 'BLOCKED','apk_sha256':apk_sha,'errors':errs}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errs else 2

if __name__=='__main__':
    raise SystemExit(main())
