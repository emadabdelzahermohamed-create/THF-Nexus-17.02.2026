import copy, json, pathlib, importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "games_factory" / "THF_GAME_DEVICE_CANDIDATES_V1.json"
MOD_PATH = pathlib.Path(__file__).with_name("validate_game_device_candidates_v1.py")
spec = importlib.util.spec_from_file_location("validator", MOD_PATH)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def doc(): return json.loads(REG.read_text())

def test_registry_passes():
    assert mod.validate(doc()) == []

def test_rejects_final_claim():
    x=doc(); x["final_or_play_ready"]=True
    assert mod.validate(x)

def test_rejects_wrong_sha():
    x=doc(); x["candidates"][0]["apk_sha256"]="deadbeef"
    assert mod.validate(x)

def test_rejects_rift_without_combat():
    x=doc(); next(r for r in x["candidates"] if r["app"]=="rift")["requires_combat"]=False
    assert mod.validate(x)

def test_rejects_rush_without_sensor_motion():
    x=doc(); next(r for r in x["candidates"] if r["app"]=="rush")["requires_sensor_motion"]=False
    assert mod.validate(x)

def test_rejects_terra_desktop_override():
    x=doc(); next(r for r in x["candidates"] if r["app"]=="terra")["desktop_override_active"]=True
    assert mod.validate(x)

def test_rejects_current_candidate_in_historical_set():
    x=doc(); sha=x["candidates"][0]["apk_sha256"]; x["rejected_historical_candidates"].append(sha[:12])
    assert mod.validate(x)
