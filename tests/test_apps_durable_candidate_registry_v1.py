import copy, json, unittest
from pathlib import Path
from ReleaseOps.scripts.validate_apps_durable_candidate_registry_v1 import validate

REG=Path('ReleaseOps/apps/THF_APPS_DURABLE_CANDIDATE_REGISTRY_V1.json')

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads(REG.read_text(encoding='utf-8'))
    def assertRejected(self, mutate):
        d=copy.deepcopy(self.base); mutate(d)
        with self.assertRaises(SystemExit): validate(d)
    def test_baseline(self): self.assertTrue(validate(copy.deepcopy(self.base)))
    def test_reject_final_promotion(self): self.assertRejected(lambda d: d['candidates']['vault'].__setitem__('final_or_play_ready',True))
    def test_reject_physical_fake_pass(self): self.assertRejected(lambda d: d['candidates']['signal'].__setitem__('physical_device_pass',True))
    def test_reject_network_fake_pass(self): self.assertRejected(lambda d: d['global_release_truth'].__setitem__('network_release_ready',True))
    def test_reject_wrong_package(self): self.assertRejected(lambda d: d['candidates']['vault'].__setitem__('package_id','com.example.wrapper'))
    def test_reject_wrong_target_sdk(self): self.assertRejected(lambda d: d['candidates']['signal'].__setitem__('target_sdk',35))
    def test_reject_source_sha_drift(self): self.assertRejected(lambda d: d['candidates']['vault'].__setitem__('source_sha256','0'*64))
    def test_reject_apk_sha_drift(self): self.assertRejected(lambda d: d['candidates']['signal'].__setitem__('apk_sha256','1'*64))
    def test_reject_non_durable_library_id(self): self.assertRejected(lambda d: d['candidates']['vault']['durable_source'].__setitem__('library_file_id','artifact-10358840193'))
    def test_reject_wrong_library_root(self): self.assertRejected(lambda d: d['candidates']['signal']['durable_apk'].__setitem__('library_path','/tmp/signal.apk'))
    def test_reject_spark_false_resolution(self): self.assertRejected(lambda d: d['unresolved']['spark'].__setitem__('reason','PASS'))
    def test_reject_provider_kms_fake_pass(self): self.assertRejected(lambda d: d['global_release_truth'].__setitem__('provider_kms_boundary_proven',True))

if __name__=='__main__': unittest.main()
