#!/usr/bin/env python3
import copy,json
from pathlib import Path
from validate_thf_apps_phone_authority_v3 import validate
BASE=json.loads((Path(__file__).parent/'THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V3_MANIFEST.json').read_text())

def reject(mutator):
 d=copy.deepcopy(BASE); mutator(d)
 try: validate(d)
 except (AssertionError,KeyError,TypeError): return
 raise AssertionError('mutation unexpectedly accepted')

validate(copy.deepcopy(BASE))
reject(lambda d:d.update(shared_identity_authority='thf.shared.integration.v3'))
reject(lambda d:d['source_candidates']['forge'].update(sha256='0'*64))
reject(lambda d:d['source_candidates']['vault'].update(target_sdk=35))
reject(lambda d:d['source_candidates']['signal']['private_access'].update(no_launcher=False))
reject(lambda d:d['source_candidates']['signal']['private_access'].update(server_role_claim_required=False))
reject(lambda d:d['source_candidates']['command']['private_access'].update(allowed_roles=['publisher','admin','owner']))
reject(lambda d:d['release_truth'].update(final_or_play_ready=True))
reject(lambda d:d['source_candidates']['echo'].update(eligible_apk_sha256='1'*64,android_build_status='PASS'))
reject(lambda d:d['source_candidates']['codex']['phone_fundamentals'].remove('notification_channel'))
print('PASS V3 authority regression mutations rejected')
