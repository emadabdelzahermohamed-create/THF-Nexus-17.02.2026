import copy
from ReleaseOps.validators.validate_game_backend_authority_dynamic_v1 import validate

SHA = "a" * 64


def good():
    probes=[]
    for i,path in enumerate([
        "/api/world/environment","/api/social/position","/api/social/send",
        "/api/avatar/generate","/api/arena/start","/api/arena/action","/api/economy/internal-award"
    ]):
        probes.append({"name":f"p{i}","path":path,"method":"POST","status":401 if i%2==0 else 403,"unauthorized_rejected":True})
    return {
        "schema":"thf-game-backend-authority-dynamic-v1",
        "runtime_source_sha256":SHA,
        "canonical_source_sha256_after":SHA,
        "canonical_source_modified":False,
        "external_network_allowed":False,
        "production_credentials_used":False,
        "wave_files_read_or_changed":False,
        "final_or_play_ready":False,
        "probes":probes,
        "probe_count":len(probes),
        "unauthorized_rejection_count":len(probes),
        "all_unauthorized_mutations_rejected":True,
    }


def test_accepts_strict_401_403_evidence():
    assert validate(good()) == []


def test_rejects_404_as_false_authority_pass():
    d=good(); d["probes"][0]["status"]=404
    assert any("401/403" in e for e in validate(d))


def test_rejects_500_as_false_authority_pass():
    d=good(); d["probes"][0]["status"]=500
    assert any("401/403" in e for e in validate(d))


def test_rejects_probe_error():
    d=good(); d["probes"][0]["probe_error"]="TimeoutError"
    assert any("probe_error" in e for e in validate(d))


def test_rejects_network_or_wave_access():
    d=good(); d["external_network_allowed"]=True; d["wave_files_read_or_changed"]=True
    errs=validate(d)
    assert any("external_network_allowed" in e for e in errs)
    assert any("wave_files_read_or_changed" in e for e in errs)


def test_rejects_canonical_source_change():
    d=good(); d["canonical_source_modified"]=True; d["canonical_source_sha256_after"]="b"*64
    errs=validate(d)
    assert any("canonical source SHA" in e for e in errs)
    assert any("canonical_source_modified" in e for e in errs)


def test_rejects_final_claim():
    d=good(); d["final_or_play_ready"]=True
    assert any("final_or_play_ready" in e for e in validate(d))


def test_rejects_fewer_than_five_probes():
    d=good(); d["probes"]=d["probes"][:4]; d["probe_count"]=4; d["unauthorized_rejection_count"]=4
    assert any("fewer than 5" in e for e in validate(d))
