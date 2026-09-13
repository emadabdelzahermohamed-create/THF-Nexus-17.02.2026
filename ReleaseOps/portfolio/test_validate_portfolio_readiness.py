import copy, importlib.util, json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / 'ReleaseOps/portfolio/validate_portfolio_readiness.py'
SPEC = importlib.util.spec_from_file_location('validator', MOD_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
BASE = json.loads((ROOT / 'ReleaseOps/portfolio/portfolio_readiness_v1.json').read_text('utf-8'))


def good_mobile_evidence(sha):
    return {
        'candidate_sha256': sha,
        'payload_inspection_pass': True,
        'package_identity_pass': True,
        'reachable_backend_health_auth_pass': True,
        'phone_install_launch_pass': True,
        'touch_layout_orientation_pass': True,
        'background_resume_pass': True,
        'offline_network_transition_pass': True,
        'core_journey_pass': True,
        'crash_free_smoke_pass': True,
        'localization_rtl_pass': True,
        'accessibility_pass': True,
        'data_saver_pass': True,
        'rollback_pass': True,
        'backend': {'scheme':'https','placeholder_or_loopback':False},
    }


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

    def test_mobile_final_without_candidate_evidence_is_rejected(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS')
        self.assertTrue(any('candidate_evidence object' in e for e in validator.validate(d)))

    def test_mobile_final_rejects_placeholder_backend(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS')
        core['candidate_evidence']=good_mobile_evidence(core['candidate_sha256'])
        core['candidate_evidence']['backend']['placeholder_or_loopback']=True
        self.assertTrue(any('placeholder/loopback' in e for e in validator.validate(d)))

    def test_mobile_final_rejects_unbound_evidence_sha(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS')
        core['candidate_evidence']=good_mobile_evidence('0'*64)
        self.assertTrue(any('not bound to exact candidate SHA' in e for e in validator.validate(d)))

    def test_mobile_final_accepts_complete_real_function_evidence(self):
        d=copy.deepcopy(BASE)
        core=next(p for p in d['products'] if p['name']=='THF Core')
        core.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS')
        core['candidate_evidence']=good_mobile_evidence(core['candidate_sha256'])
        self.assertEqual([], validator.validate(d))

    def test_game_final_requires_gameplay_and_performance_observation(self):
        d=copy.deepcopy(BASE)
        terra=next(p for p in d['products'] if p['name']=='THF Terra')
        terra.update(readiness='FINAL', physical_device_gate='PASS', play_internal='PASS')
        terra['candidate_evidence']=good_mobile_evidence(terra['candidate_sha256'])
        errors=validator.validate(d)
        self.assertTrue(any('player_avatar_load_pass' in e for e in errors))
        terra['candidate_evidence'].update(
            player_avatar_load_pass=True,
            movement_camera_gameplay_pass=True,
            fps_ram_thermal_observed=True,
        )
        self.assertEqual([], validator.validate(d))

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
