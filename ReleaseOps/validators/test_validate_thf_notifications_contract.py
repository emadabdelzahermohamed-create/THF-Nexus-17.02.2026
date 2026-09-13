import copy, json, tempfile
from pathlib import Path
import pytest
from ReleaseOps.validators.validate_thf_notifications_contract import main

BASE=Path('ReleaseOps/apps_factory/contracts/thf_notifications_v1.json')

def run_bad(mutator):
    d=json.loads(BASE.read_text()); mutator(d)
    with tempfile.NamedTemporaryFile('w',delete=False,suffix='.json') as f:
        json.dump(d,f); name=f.name
    with pytest.raises(SystemExit): main(name)

def test_contract_passes():
    main(BASE)

def test_cannot_claim_push_ready():
    run_bad(lambda d:d['truth_boundary'].__setitem__('push_ready',True))

def test_api36_locked():
    run_bad(lambda d:d['requirements'].__setitem__('android_api',35))

def test_no_insecure_transport():
    run_bad(lambda d:d['requirements'].__setitem__('runtime_endpoint_scheme',['http']))

def test_no_fake_offline_claim():
    run_bad(lambda d:d['requirements'].__setitem__('offline_behavior','offline supported'))

def test_device_gate_required():
    run_bad(lambda d:d['requirements'].__setitem__('physical_device_evidence_required',False))

def test_scope_cannot_drop_app():
    run_bad(lambda d:d.__setitem__('scope',d['scope'][:-1]))
