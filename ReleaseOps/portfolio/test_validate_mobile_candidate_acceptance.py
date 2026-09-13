import copy, importlib.util, pathlib, unittest

P=pathlib.Path(__file__).with_name('validate_mobile_candidate_acceptance.py')
spec=importlib.util.spec_from_file_location('v',P); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

BASE={
 'candidate_sha256':'a'*64,'package':'com.topherofit.thf.pulse','target_sdk':36,
 'payload_inspection':'PASS','package_identity':'PASS','qa_signature_only':True,'production_signing':False,
 'lane':'mobile-app',
 'network':{'required':True,'base_url':'https://staging.topherofit.example','health':'PASS','auth':'PASS','placeholder_or_loopback':False,'authoritative_remote_state_offline':False},
 'device':{'model':'QA Phone','android_version':'16','candidate_sha256':'a'*64,'checks':{k:'PASS' for k in v.REQUIRED_DEVICE_CHECKS}}
}

class T(unittest.TestCase):
 def test_good_mobile(self): self.assertEqual(v.validate(copy.deepcopy(BASE)),[])
 def test_loopback_rejected(self):
  d=copy.deepcopy(BASE); d['network']['base_url']='https://127.0.0.1'; self.assertTrue(v.validate(d))
 def test_sha_binding_required(self):
  d=copy.deepcopy(BASE); d['device']['candidate_sha256']='b'*64; self.assertTrue(v.validate(d))
 def test_pending_device_rejected(self):
  d=copy.deepcopy(BASE); d['device']['checks']['touch']='PENDING'; self.assertTrue(v.validate(d))
 def test_fake_offline_rejected(self):
  d=copy.deepcopy(BASE); d['network']={'required':False,'authoritative_remote_state_offline':True}; self.assertTrue(v.validate(d))
 def test_game_perf_required(self):
  d=copy.deepcopy(BASE); d['lane']='mobile-game'; d['game']={'player_avatar_load':'PASS','movement_camera_gameplay':'PASS','performance':{'fps_observed':60,'ram_mb_observed':512,'thermal_observed':'nominal'}}; self.assertEqual(v.validate(d),[])

if __name__=='__main__': unittest.main()
