from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'ReleaseOps' / 'scripts' / 'core_runtime_configured_staging_v1.sh'
WORKFLOW = ROOT / '.github' / 'workflows' / 'thf-core-rc6-runtime-configured-staging-v1.yml'


class CoreRuntimeStagingContractTest(unittest.TestCase):
    def test_phone_qa_build_is_side_by_side_and_uses_verified_runtime(self):
        self.assertTrue(SCRIPT.exists(), 'runtime-configured Core staging script must be tracked')
        source = SCRIPT.read_text()
        for marker in (
            '6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a',
            'http://127.0.0.1:18080/health',
            'trycloudflare',
            "applicationId 'com.topherofit.thf.core.debug'",
            "versionCode 62203",
            "versionName '6.2.2-rc6-phoneqa3'",
            'service_health=PASS',
            'wave_untouched=true',
        ):
            self.assertIn(marker, source)
        self.assertNotIn('gcloud run deploy', source)

    def test_existing_workflow_executes_the_tracked_runtime_script(self):
        workflow = WORKFLOW.read_text()
        self.assertIn('ReleaseOps/scripts/core_runtime_configured_staging_v1.sh', workflow)
        self.assertIn('Build Core with verified HTTPS staging endpoint', workflow)
        self.assertIn('service_url_embedded=true', workflow)
        self.assertIn('service_health=PASS', workflow)


if __name__ == '__main__':
    unittest.main()
