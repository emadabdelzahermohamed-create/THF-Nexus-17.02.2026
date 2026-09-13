import copy, importlib.util, json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / 'ReleaseOps/portfolio/validate_portfolio_readiness.py'
SPEC = importlib.util.spec_from_file_location('validator', MOD_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
BASE = json.loads((ROOT / 'ReleaseOps/portfolio/portfolio_readiness_v1.json').read_text('utf-8'))

class PortfolioReadinessTests(unittest.TestCase):
    def test_current_matrix_is_truthful(self):
        self.assertEqual([], validator.validate(copy.deepcopy(BASE)))

    def test_final_without_device_evidence_is_rejected(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core['readiness']='FINAL'
        self.assertTrue(any('physical-device PASS' in e for e in validator.validate(d)))

    def test_final_without_exact_sha_is_rejected(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS', candidate_sha256=None)
        self.assertTrue(any('exact candidate SHA' in e for e in validator.validate(d)))

    def test_wave_identity_cannot_be_inferred_while_source_missing(self):
        d=copy.deepcopy(BASE)
        wave=next(p for p in d['products'] if p['name']=='WAVE MAWJA')
        wave['package']='com.example.guess'
        self.assertTrue(any('must not be inferred' in e for e in validator.validate(d)))

    def test_token_lane_cannot_silently_leave_read_only(self):
        d=copy.deepcopy(BASE)
        token=next(p for p in d['products'] if p['name']=='THF Token Program')
        token['runtime_gate']='PASS'
        self.assertTrue(any('read-only' in e for e in validator.validate(d)))

    def test_package_collision_rejected(self):
        d=copy.deepcopy(BASE)
        pulse=next(p for p in d['products'] if p['name']=='THF Pulse')
        pulse['package']='com.topherofit.thf.core'
        self.assertTrue(any('package identity collision' in e for e in validator.validate(d)))

if __name__ == '__main__': unittest.main()
