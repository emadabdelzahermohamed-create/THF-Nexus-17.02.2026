#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

SHA_RE = re.compile(r'^[0-9a-f]{64}$')
LIB_RE = re.compile(r'^libfile_[0-9a-f]+$')
EXPECTED = {
  'vault': ('com.topherofit.thf.vault','052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432','7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e'),
  'signal': ('com.topherofit.thf.signal','f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275','c7eb1044426423862687f93a875208a5ea8c5703d4978efb93eb4b54a1555d75')
}
TRUTH_KEYS = ['production_signature','physical_device_pass','network_release_ready','push_ready','final_or_play_ready']
GLOBAL_FALSE = ['stable_external_trusted_tls_thf_pass_backend','auth_session_federation_external_proof','provider_kms_boundary_proven','physical_device_pass','network_release_ready','push_ready','production_signing_performed','play_public_rollout_performed','final_or_play_ready']

def fail(msg):
    raise SystemExit(f'FAIL: {msg}')

def validate(data):
    if data.get('schema') != 'thf.apps.durable-candidate-registry.v1': fail('schema')
    if data.get('policy') != 'MOBILE_REAL_FUNCTION_RELEASE_POLICY': fail('policy')
    source_ev=data.get('source_evidence',{})
    if source_ev.get('workflow_run') != 34869083968: fail('workflow_run provenance')
    if source_ev.get('workflow_artifact_id') != 10358840193: fail('artifact provenance')
    if source_ev.get('workflow_artifact_sha256') != '6385525db6cd5d6bb7049b38ee53b79e95ccc2b488689617cd02e94848e33ccc': fail('artifact sha provenance')
    candidates=data.get('candidates',{})
    if set(candidates) != set(EXPECTED): fail('candidate set')
    seen=set()
    for app,(package,source_sha,apk_sha) in EXPECTED.items():
        c=candidates[app]
        if c.get('package_id') != package: fail(f'{app} package')
        if c.get('target_sdk') != 36: fail(f'{app} target sdk')
        if c.get('source_sha256') != source_sha or not SHA_RE.fullmatch(c.get('source_sha256','')): fail(f'{app} source sha')
        if c.get('apk_sha256') != apk_sha or not SHA_RE.fullmatch(c.get('apk_sha256','')): fail(f'{app} apk sha')
        if c.get('source_sha256') in seen or c.get('apk_sha256') in seen: fail(f'{app} duplicate sha')
        seen.update([c['source_sha256'],c['apk_sha256']])
        if c.get('payload_gate') != 'PASS' or c.get('clean_extract_integrity') != 'PASS': fail(f'{app} integrity gate')
        if c.get('authority') != 'CANONICAL_QA_CANDIDATE_NOT_FINAL': fail(f'{app} authority')
        for k in TRUTH_KEYS:
            if c.get(k) is not False: fail(f'{app} {k} must remain false')
        for kind in ('durable_source','durable_apk'):
            d=c.get(kind,{})
            if not isinstance(d.get('library_path'),str) or not d['library_path'].startswith('/THF/ReleaseOps/Apps/2026-09-14/'):
                fail(f'{app} {kind} library path')
            if not LIB_RE.fullmatch(d.get('library_file_id','')): fail(f'{app} {kind} library id')
    unresolved=data.get('unresolved',{})
    if set(unresolved) != {'spark','rush'}: fail('unresolved set')
    for app in ('spark','rush'):
        if unresolved[app].get('reason') != 'SOURCE_BYTES_NOT_PROVEN': fail(f'{app} unresolved reason')
        if not SHA_RE.fullmatch(unresolved[app].get('source_sha256','')): fail(f'{app} unresolved sha')
    truth=data.get('global_release_truth',{})
    for k in GLOBAL_FALSE:
        if truth.get(k) is not False: fail(f'global {k} must remain false')
    return True

def main():
    p=Path(sys.argv[1] if len(sys.argv)>1 else 'ReleaseOps/apps/THF_APPS_DURABLE_CANDIDATE_REGISTRY_V1.json')
    validate(json.loads(p.read_text(encoding='utf-8')))
    print('THF_APPS_DURABLE_CANDIDATE_REGISTRY_V1=PASS')

if __name__=='__main__': main()
