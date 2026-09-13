#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REQUIRED_PRODUCTS = [
    'THF Core','THF Pulse','THF Forge','THF Echo','THF Codex','THF Terra','THF Rift',
    'THF Spark','THF Rush','THF Vault','THF Signal','THF Command','THF Pass','WAVE MAWJA',
    'Platform / Release Infrastructure','THF Token Program'
]
SHA_RE = re.compile(r'^[0-9a-f]{64}$')
PROMOTED = {'FINAL','PLAY_READY','RELEASE_READY','PRODUCTION_READY'}
MOBILE_LANES = {'mobile-app','private-mobile-app','mobile-game','isolated-mobile-platform'}
PROMOTED_EVIDENCE = (
    'payload_inspection_pass',
    'package_identity_pass',
    'reachable_backend_health_auth_pass',
    'phone_install_launch_pass',
    'touch_layout_orientation_pass',
    'background_resume_pass',
    'offline_network_transition_pass',
    'core_journey_pass',
    'crash_free_smoke_pass',
    'localization_rtl_pass',
    'accessibility_pass',
    'data_saver_pass',
    'rollback_pass',
)
GAME_EVIDENCE = (
    'player_avatar_load_pass',
    'movement_camera_gameplay_pass',
    'fps_ram_thermal_observed',
)
PROHIBITED_FINAL_TOKENS = (
    'UI_ONLY','SHELL_ONLY','WRAPPER_ONLY','TEMPLATE_ONLY','SOURCE_ONLY','STATIC_ONLY',
    'PLACEHOLDER_ENDPOINT','FAKE_OFFLINE','FAKE_NETWORK'
)


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def validate(doc: dict) -> list[str]:
    errors: list[str] = []
    req = doc.get('global_requirements', {})
    if req.get('target_sdk') != 36:
        fail('global targetSdk must remain 36', errors)
    for k in ('exact_candidate_payload_inspection','physical_device_evidence_required_for_final',
              'localization_rtl_required','accessibility_required','data_saver_required',
              'rollback_required','project_isolation_required'):
        if req.get(k) is not True:
            fail(f'global requirement {k} must be true', errors)

    products = doc.get('products')
    if not isinstance(products, list):
        return errors + ['products must be a list']
    by_name = {p.get('name'): p for p in products if isinstance(p, dict)}
    missing = [n for n in REQUIRED_PRODUCTS if n not in by_name]
    if missing:
        fail('missing portfolio lanes: ' + ', '.join(missing), errors)

    known_packages: dict[str,str] = {}
    for name, p in by_name.items():
        readiness = str(p.get('readiness',''))
        sha = p.get('candidate_sha256')
        pkg = p.get('package')
        device = p.get('physical_device_gate')
        runtime = p.get('runtime_gate')
        static = p.get('static_package_gate')
        lane = p.get('lane')

        if sha is not None and (not isinstance(sha,str) or not SHA_RE.fullmatch(sha)):
            fail(f'{name}: candidate_sha256 must be lowercase SHA-256 or null', errors)
        if pkg:
            if pkg in known_packages:
                fail(f'package identity collision: {name} and {known_packages[pkg]} use {pkg}', errors)
            known_packages[pkg] = name

        if readiness in PROMOTED:
            if not sha:
                fail(f'{name}: promoted readiness without exact candidate SHA', errors)
            if runtime != 'PASS' or static != 'PASS':
                fail(f'{name}: promoted readiness without runtime/static PASS', errors)
            if device != 'PASS':
                fail(f'{name}: promoted readiness without physical-device PASS', errors)
            if p.get('play_internal') not in {'PASS','UPLOADED_PASS','PRIVATE_INTERNAL_ONLY'}:
                fail(f'{name}: promoted readiness without Play/Internal distribution evidence', errors)

            combined = ' '.join(str(p.get(k,'')) for k in ('runtime_gate','static_package_gate','readiness','evidence')).upper()
            for token in PROHIBITED_FINAL_TOKENS:
                if token in combined:
                    fail(f'{name}: prohibited weak-release marker present at promotion: {token}', errors)

            if lane in MOBILE_LANES:
                ev = p.get('candidate_evidence')
                if not isinstance(ev, dict):
                    fail(f'{name}: promoted mobile readiness without candidate_evidence object', errors)
                else:
                    for key in PROMOTED_EVIDENCE:
                        if ev.get(key) is not True:
                            fail(f'{name}: promoted mobile readiness without {key}=true', errors)
                    if lane == 'mobile-game':
                        for key in GAME_EVIDENCE:
                            if ev.get(key) is not True:
                                fail(f'{name}: promoted game readiness without {key}=true', errors)
                    if ev.get('candidate_sha256') != sha:
                        fail(f'{name}: candidate evidence is not bound to exact candidate SHA', errors)
                    backend = ev.get('backend')
                    if not isinstance(backend, dict) or backend.get('scheme') not in {'https','wss','https+wss'}:
                        fail(f'{name}: promoted network candidate lacks reachable HTTPS/WSS backend evidence', errors)
                    if isinstance(backend, dict) and backend.get('placeholder_or_loopback') is not False:
                        fail(f'{name}: promoted candidate backend may be placeholder/loopback', errors)

        if name == 'WAVE MAWJA' and readiness == 'BLOCKED_CANONICAL_SOURCE':
            if pkg is not None or sha is not None:
                fail('WAVE: current package/SHA must not be inferred while canonical source is missing', errors)
        if name == 'THF Token Program':
            if runtime != 'READ_ONLY_ONLY':
                fail('Token program must remain read-only at coordination gate', errors)
            if readiness not in {'OWNER_SIGNING_BLOCKED','SAFE_READ_ONLY'}:
                fail('Token program cannot be promoted without owner signing authorization', errors)
    return errors


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('matrix', nargs='?', default='ReleaseOps/portfolio/portfolio_readiness_v1.json')
    a=ap.parse_args()
    path=Path(a.matrix)
    try:
        doc=json.loads(path.read_text('utf-8'))
    except Exception as e:
        print(json.dumps({'status':'BLOCKED','errors':[f'invalid readiness document: {e}']}, indent=2))
        return 2
    errors=validate(doc)
    print(json.dumps({'status':'PASS' if not errors else 'BLOCKED','products':len(doc.get('products',[])),'errors':errors}, indent=2))
    return 0 if not errors else 2

if __name__ == '__main__':
    sys.exit(main())
