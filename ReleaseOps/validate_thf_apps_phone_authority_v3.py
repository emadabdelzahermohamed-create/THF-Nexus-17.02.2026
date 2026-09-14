#!/usr/bin/env python3
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EXPECTED_SCOPE=['core','forge','echo','codex','vault','signal','command']
EXPECTED_EXCLUDED=['pulse','games','wave']
EXPECTED={
 'forge':('THF Market','com.topherofit.thf.forge',21102,'2.1.1-phone3','75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8'),
 'echo':('THF Community','com.topherofit.thf.echo',21102,'2.1.1-phone3','3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9'),
 'codex':('THF Learn','com.topherofit.thf.codex',21102,'2.1.1-phone3','44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950'),
 'vault':('THF Wallet','com.topherofit.thf.vault',12002,'1.2.0-apps-rc4','e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585'),
 'signal':('THF Publisher','com.topherofit.thf.signal',12002,'1.2.0-apps-rc4','3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef'),
 'command':('THF Admin','com.topherofit.thf.command',12002,'1.2.0-apps-rc4','314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc')}
REQUIRED={'onboarding','explicit_account_route','explicit_logout_route','explicit_delete_account_route','trusted_https_fail_closed','validated_network_required','system_data_saver','offline_loading_error_states','notification_channel','notification_runtime_permission','rtl','accessibility_preferences','adaptive_icon','monochrome_icon','store_icon'}

def validate(d):
 assert d['schema']=='thf-apps-phone-fundamentals-source-v3'
 assert d['scope']==EXPECTED_SCOPE and d['excluded']==EXPECTED_EXCLUDED
 assert d['shared_identity_authority']=='thf.shared.integration.v4'
 c=d['core']; assert c=={'same_sha_skip':True,'source_sha256':'6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a','package_id':'com.topherofit.thf.core'}
 assert set(d['source_candidates'])==set(EXPECTED)
 for slug,(name,pkg,vc,vn,sha) in EXPECTED.items():
  a=d['source_candidates'][slug]
  assert (a['user_facing_name'],a['package_id'],a['version_code'],a['version_name'],a['sha256'])==(name,pkg,vc,vn,sha)
  assert a['target_sdk']==36 and a['resource_locales']==20
  assert a['android_build_status']=='NEEDS_EXACT_SOURCE_BUILD' and a['eligible_apk_sha256'] is None
  assert REQUIRED.issubset(set(a['phone_fundamentals']))
 assert d['source_candidates']['signal']['private_access']=={'no_launcher':True,'signature_entry_boundary':True,'server_role_claim_required':True,'thf_pass_handoff_required':True,'allowed_roles':['publisher','admin','owner']}
 assert d['source_candidates']['command']['private_access']=={'no_launcher':True,'signature_entry_boundary':True,'server_role_claim_required':True,'thf_pass_handoff_required':True,'allowed_roles':['admin','owner']}
 for k in ('android_exact_build','network_release_ready','push_provider_ready','physical_device_pass','production_signing','final_or_play_ready'): assert d['release_truth'][k] is False
 return True

def latest_manifest():
 candidates=[]
 for p in ROOT.glob('THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V*_MANIFEST.json'):
  m=re.search(r'_V(\d+)_MANIFEST',p.name)
  if m:candidates.append((int(m.group(1)),p))
 assert candidates
 v,p=max(candidates)
 assert v==3, f'authority downgrade/unknown newer schema: resolved V{v}'
 return p

if __name__=='__main__':
 p=latest_manifest(); validate(json.loads(p.read_text()))
 print(f'PASS latest_authority={p.name} identity=thf.shared.integration.v4 final=false')
