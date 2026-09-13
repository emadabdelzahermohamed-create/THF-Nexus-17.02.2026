#!/usr/bin/env python3
"""Inventory source evidence for release-critical mobile capabilities.

This tool is deliberately non-promotional: a source hit is evidence for review, not runtime PASS.
It never upgrades readiness. Exact APK, reachable backend and physical-device gates remain separate.
"""
import argparse, json, re
from pathlib import Path

TEXT_SUFFIXES={'.java','.kt','.kts','.xml','.gradle','.properties','.json','.yaml','.yml','.py','.js','.ts','.tsx','.md','.txt'}
PATTERNS={
 'auth_session': re.compile(r'(?i)\b(auth|login|logout|session|refresh.?token|access.?token|bearer)\b'),
 'pass_federation': re.compile(r'(?i)(THF_PASS|passUrl|pass_url|federat|handoff|sso|oauth|openid)'),
 'secure_storage': re.compile(r'(?i)(EncryptedSharedPreferences|EncryptedFile|MasterKey|AndroidKeyStore|KeyStore|MODE_PRIVATE|secure.?stor)'),
 'offline_local': re.compile(r'(?i)(offline|RoomDatabase|SQLite|SharedPreferences|cache|local.?store|localStorage)'),
 'loading_error': re.compile(r'(?i)(loading|retry|error|timeout|empty.?state|progress)'),
 'notification': re.compile(r'(?i)(NotificationManager|NotificationChannel|FirebaseMessaging|push.?notification|POST_NOTIFICATIONS)'),
 'accessibility': re.compile(r'(?i)(contentDescription|importantForAccessibility|Accessibility|setContentDescription|screen.?reader)'),
 'data_saver': re.compile(r'(?i)(isActiveNetworkMetered|RESTRICT_BACKGROUND_STATUS|NetworkCapabilities|metered|data.?saver)'),
 'rtl': re.compile(r'(?i)(supportsRtl|layoutDirection|textDirection|locale|RTL|startToEnd|endToStart)'),
 'network_security': re.compile(r'(?i)(networkSecurityConfig|usesCleartextTraffic|CertificatePinner|hostnameVerifier)'),
 'websocket': re.compile(r'(?i)(wss://|WebSocket|newWebSocket)'),
 'admin_control': re.compile(r'(?i)(admin|control.?panel|moderation|operator)'),
}
URL_RE=re.compile(r'(?i)\b(?:https|wss|http|ws)://[^\s\"\'<>)]+' )


def scan(root: Path):
    counts={k:0 for k in PATTERNS}
    samples={k:[] for k in PATTERNS}
    urls=[]; files=0; locale_dirs=[]
    for d in root.rglob('values-*'):
        if d.is_dir() and '/res/' in d.as_posix(): locale_dirs.append(d.name)
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES: continue
        try: text=p.read_text(errors='ignore')
        except Exception: continue
        files+=1
        rel=p.relative_to(root).as_posix()
        for u in URL_RE.findall(text):
            if u not in urls: urls.append(u)
        for key,rx in PATTERNS.items():
            n=len(rx.findall(text)); counts[key]+=n
            if n and len(samples[key])<5: samples[key].append(rel)
    return {
      'schema':1,'root':str(root),'files_scanned':files,
      'capability_source_hits':counts,'sample_files':samples,
      'locale_resource_dirs':sorted(set(locale_dirs)),
      'locale_resource_dir_count':len(set(locale_dirs)),
      'urls':urls[:100],
      'truth_boundary':{
        'source_hit_is_not_runtime_pass':True,
        'source_hit_is_not_user_flow_proof':True,
        'exact_candidate_inspection_still_required':True,
        'reachable_backend_health_auth_still_required_when_networked':True,
        'physical_phone_acceptance_still_required':True
      }
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--json-out',type=Path)
    ns=ap.parse_args(); out=scan(ns.root)
    text=json.dumps(out,indent=2); print(text)
    if ns.json_out: ns.json_out.write_text(text+'\n')

if __name__=='__main__': main()
