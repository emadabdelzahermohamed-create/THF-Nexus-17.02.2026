#!/usr/bin/env python3
import json, sys
from pathlib import Path

REQ_APPS={"pulse","forge","echo","codex","spark","rush","vault","signal","command"}
REQ_TRUE={
"permission_request_contextual","permission_denial_non_blocking","channel_creation_required_before_post",
"provider_token_secure_storage","provider_token_never_in_query_string","provider_token_registration_authenticated",
"provider_token_rotation_supported","provider_token_revocation_on_logout","notification_deeplink_allowlist_required",
"notification_deeplink_must_not_embed_credentials","data_saver_aware","rtl_localized_content_required",
"accessibility_label_required","physical_device_evidence_required"}

def fail(msg):
    raise SystemExit("NOTIFICATION_CONTRACT_FAIL: "+msg)

def main(path):
    d=json.loads(Path(path).read_text())
    if d.get("schema")!="thf.notifications.contract.v1": fail("schema")
    t=d.get("truth_boundary",{})
    if t.get("push_ready") is not False or t.get("final_or_play_ready") is not False: fail("truth boundary must remain false")
    if t.get("source_inventory_status")!="NONE_ACROSS_NINE_APPS": fail("inventory truth drift")
    if set(d.get("scope",[]))!=REQ_APPS: fail("scope")
    r=d.get("requirements",{})
    if r.get("android_api")!=36: fail("API 36")
    if set(r.get("runtime_endpoint_scheme",[]))!={"https","wss"}: fail("transport")
    for k in sorted(REQ_TRUE):
        if r.get(k) is not True: fail(k)
    offline=r.get("offline_behavior","")
    for word in ("must_not_fake","social","economy","ranked"):
        if word not in offline: fail("offline truth: "+word)
    p=d.get("promotion",{})
    for k in ("source_only_pass_forbidden","mock_only_pass_forbidden","provider_config_required_for_push_ready","reachable_authenticated_registration_required_for_push_ready","physical_receive_tap_background_resume_required_for_push_ready"):
        if p.get(k) is not True: fail(k)
    print("THF_NOTIFICATIONS_CONTRACT=PASS")
    print("PUSH_READY=FALSE")
    print("FINAL_OR_PLAY_READY=FALSE")

if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "ReleaseOps/apps_factory/contracts/thf_notifications_v1.json")
