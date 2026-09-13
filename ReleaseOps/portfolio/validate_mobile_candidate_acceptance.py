#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from urllib.parse import urlparse

SHA_RE=re.compile(r'^[0-9a-f]{64}$')
PKG_RE=re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+$')
REQUIRED_DEVICE_CHECKS=(
    'install','launch','touch','responsive_layout','orientation','background_resume',
    'offline_network_transition','core_user_journey','crash_free_smoke','accessibility',
    'data_saver','rtl','localization_smoke','rollback'
)


def validate(doc:dict)->list[str]:
    e=[]
    sha=doc.get('candidate_sha256')
    if not isinstance(sha,str) or not SHA_RE.fullmatch(sha): e.append('candidate_sha256 must be exact lowercase SHA-256')
    pkg=doc.get('package')
    if not isinstance(pkg,str) or not PKG_RE.fullmatch(pkg): e.append('package must be a valid locked Android package id')
    if doc.get('target_sdk') != 36: e.append('target_sdk must be 36')
    if doc.get('payload_inspection') != 'PASS': e.append('payload_inspection must PASS')
    if doc.get('package_identity') != 'PASS': e.append('package_identity must PASS')
    if doc.get('qa_signature_only') is not True: e.append('autonomous acceptance evidence must be QA-signature-only')
    if doc.get('production_signing') is not False: e.append('production_signing must remain false')

    net=doc.get('network',{})
    if net.get('required'):
        for key in ('base_url','health','auth'):
            v=net.get(key)
            if key=='base_url':
                try:
                    u=urlparse(v)
                    if u.scheme not in ('https','wss') or not u.hostname: raise ValueError
                    if u.hostname in ('localhost','127.0.0.1','10.0.2.2','0.0.0.0'): raise ValueError
                except Exception: e.append('network.base_url must be reachable-design HTTPS/WSS and non-loopback')
            elif v!='PASS': e.append(f'network.{key} must PASS for network-required candidate')
        if net.get('placeholder_or_loopback') is not False: e.append('network placeholder_or_loopback must be false')
    else:
        if net.get('authoritative_remote_state_offline') is True: e.append('offline mode cannot claim authoritative remote/economy/social/ranked state')

    dev=doc.get('device',{})
    if not dev.get('model'): e.append('device.model required')
    if not dev.get('android_version'): e.append('device.android_version required')
    if dev.get('candidate_sha256') != sha: e.append('device evidence must bind to exact candidate SHA')
    checks=dev.get('checks',{})
    for k in REQUIRED_DEVICE_CHECKS:
        if checks.get(k)!='PASS': e.append(f'device.checks.{k} must PASS')

    if doc.get('lane')=='mobile-game':
        game=doc.get('game',{})
        for k in ('player_avatar_load','movement_camera_gameplay'):
            if game.get(k)!='PASS': e.append(f'game.{k} must PASS')
        perf=game.get('performance',{})
        for k in ('fps_observed','ram_mb_observed','thermal_observed'):
            if perf.get(k) in (None,''): e.append(f'game.performance.{k} required')
    return e


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('manifest'); a=ap.parse_args()
    try: doc=json.load(open(a.manifest,encoding='utf-8'))
    except Exception as ex:
        print(json.dumps({'status':'BLOCKED','errors':[f'invalid manifest: {ex}']},indent=2)); return 2
    errors=validate(doc)
    print(json.dumps({'status':'PASS' if not errors else 'BLOCKED','errors':errors},indent=2))
    return 0 if not errors else 2

if __name__=='__main__': sys.exit(main())
