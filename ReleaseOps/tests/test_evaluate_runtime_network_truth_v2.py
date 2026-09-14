import json
import tempfile
import unittest
from pathlib import Path

from ReleaseOps.validators.evaluate_runtime_network_truth_v2 import evaluate


class RuntimeNetworkTruthTests(unittest.TestCase):
    def make_registry(self):
        return {
            "candidates": [
                {"name":"core","source_sha256":"0"*64,"status":"PENDING_PHYSICAL_PHONE"},
                {"name":"pulse","source_sha256":"1"*64,"status":"PENDING_PHYSICAL_PHONE"},
            ]
        }

    def audit(self, *, urls=None, insecure=None, placeholders=None, config=None, auth=None):
        return {
            "runtime_urls": urls or [],
            "runtime_insecure_urls": insecure or [],
            "runtime_placeholder_urls": placeholders or [],
            "build_config_endpoint_runtime_files": config or ["MainActivity.java"],
            "pass_or_auth_runtime_files": auth or ["MainActivity.java"],
        }

    def run_eval(self, audit):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; out.mkdir()
            (root/"registry.json").write_text(json.dumps(self.make_registry()))
            (out/"pulse.runtime.json").write_text(json.dumps(audit))
            return evaluate(out, root/"registry.json")

    def test_third_party_https_does_not_become_backend_proof(self):
        report=self.run_eval(self.audit(urls=[{"url":"https://www.who.int/x","file":"seed.py"}]))
        app=report["apps"][0]
        self.assertEqual(app["runtime_https_wss_reference_count"],1)
        self.assertEqual(app["source_bound_backend_literal_count"],0)
        self.assertFalse(app["backend_health_auth_proof"])
        self.assertFalse(report["network_release_ready"])

    def test_backend_literal_still_does_not_prove_health_or_auth(self):
        report=self.run_eval(self.audit(urls=[{"url":"https://api.thf.invalid/v1","file":"MainActivity.java"}]))
        app=report["apps"][0]
        self.assertEqual(app["source_bound_backend_literal_count"],1)
        self.assertFalse(app["backend_health_auth_proof"])
        self.assertFalse(report["final_or_play_ready"])

    def test_missing_runtime_audit_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); out=root/"out"; out.mkdir()
            (root/"registry.json").write_text(json.dumps(self.make_registry()))
            with self.assertRaisesRegex(ValueError,"missing runtime endpoint audit"):
                evaluate(out, root/"registry.json")

    def test_placeholder_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"placeholder runtime URL"):
            self.run_eval(self.audit(placeholders=[{"url":"https://example.invalid","file":"MainActivity.java"}]))

    def test_insecure_runtime_url_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"insecure runtime URL"):
            self.run_eval(self.audit(insecure=[{"url":"http://api.test","file":"MainActivity.java"}]))


if __name__ == "__main__":
    unittest.main()
