#!/usr/bin/env python3
import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/ruinsciv-android-qa-build-v1.yml"
RECOVERY_WORKFLOW = ROOT / ".github/workflows/ruinsciv-rc34-source-recovery-v1.yml"
RECOVERY_HELPER = ROOT / "ReleaseOps/RuinsCiv/recover_ruinsciv_rc34_source_from_builder.sh"
BACKLOG = ROOT / "ReleaseOps/RuinsCiv/RUINSCIV_UNIFIED_BACKLOG_V1_20260918.json"


class RuinsCivAndroidQaWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.recovery_workflow = RECOVERY_WORKFLOW.read_text(encoding="utf-8")
        cls.recovery_helper = RECOVERY_HELPER.read_text(encoding="utf-8")

    def test_godot_472_uses_versioned_isolated_settings(self):
        self.assertIn('editor_settings-4.7.tres', self.workflow)
        self.assertNotIn('editor_settings-4.tres', self.workflow)
        self.assertIn('ISO="$BASE_HOME/ruinsciv-qa-godot-home"', self.workflow)
        self.assertIn('export HOME="$ISO"', self.workflow)

    def test_only_official_472_android_source_template_is_restored(self):
        self.assertIn('4.7.2.stable', self.workflow)
        self.assertIn('android_source.zip', self.workflow)
        self.assertNotIn('TEMPLATE_DIR=', self.workflow)
        self.assertNotIn('TPL_ZIP=', self.workflow)
        self.assertIn("rel.is_absolute() or '..' in rel.parts", self.workflow)
        self.assertIn('target != dst and dst not in target.parents', self.workflow)

    def test_identity_and_readiness_remain_fail_closed(self):
        self.assertIn('com.topherofit.ruins.civ.phoneqa', self.workflow)
        self.assertIn('com\\.topherofit\\.thf\\.terra', self.workflow)
        self.assertIn('physical_device_status=PENDING', self.workflow)
        self.assertIn('final_or_play_ready=FALSE', self.workflow)

    def test_pull_request_gate_is_serialized_per_candidate(self):
        self.assertIn('pull_request:', self.workflow)
        self.assertIn('group: ruinsciv-android-qa-', self.workflow)
        self.assertIn('cancel-in-progress: false', self.workflow)

    def test_runtime_and_package_gates_are_required(self):
        self.assertIn('--quit-after 30 --verbose', self.workflow)
        self.assertIn('godot-scene-boot.log', self.workflow)
        self.assertIn('unzip -tq', self.workflow)
        self.assertIn('verify --verbose --print-certs', self.workflow)
        self.assertIn('aapt-badging.txt', self.workflow)
        self.assertIn('required-asset-hits.txt', self.workflow)

    def test_source_provenance_is_stable_across_build(self):
        self.assertIn('source-content-before.sha256', self.workflow)
        self.assertIn('source-content-after.sha256', self.workflow)
        self.assertIn('cmp -s', self.workflow)
        self.assertIn('source_manifest_sha256=', self.workflow)
        self.assertIn('source_stable_during_build=TRUE', self.workflow)

    def test_sensitive_material_is_rejected_from_source_and_apk(self):
        self.assertIn('SENSITIVE_FILE_IN_APK', self.workflow)
        self.assertIn('RUINSCIV_RC34_SENSITIVE_FILE_INVENTORY.txt', self.recovery_helper)
        self.assertIn('SENSITIVE_SOURCE_MATERIAL_DETECTED', self.recovery_helper)
        self.assertIn("--exclude='*.keystore'", self.recovery_helper)

    def test_recovery_runs_on_same_repo_pull_requests_in_isolation(self):
        self.assertIn('pull_request:', self.recovery_workflow)
        self.assertIn('group: ruinsciv-source-recovery-', self.recovery_workflow)
        self.assertIn('cancel-in-progress: false', self.recovery_workflow)

    def test_remote_script_parses_as_bash(self):
        marker = "<<'REMOTE'\n"
        start = self.workflow.index(marker) + len(marker)
        end = self.workflow.index("\n          REMOTE", start)
        body = "\n".join(
            line[10:] if line.startswith(" " * 10) else line
            for line in self.workflow[start:end].splitlines()
        )
        result = subprocess.run(
            ["bash", "-n"], input=body, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_backlog_does_not_self_promote(self):
        backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
        self.assertFalse(backlog["final_or_play_ready"])
        self.assertEqual(backlog["phone_qa"], "PENDING")
        self.assertEqual(backlog["play_upload"], "NOT_CLAIMED")
        self.assertEqual(backlog["authority"]["engine"], "Godot 4.7.2")
        self.assertEqual(backlog["authority"]["target_sdk"], 36)
        self.assertEqual(backlog["authority"]["abi"], "arm64-v8a")


if __name__ == "__main__":
    unittest.main()
