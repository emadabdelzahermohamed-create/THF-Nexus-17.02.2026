from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"
SERVICE = PKG / "ActivityTrackingService.kt"
MAIN = PKG / "MainActivity.kt"
CHECKPOINT = PKG / "ActivitySessionCheckpoint.kt"


class ActivitySessionRecoveryContractTest(unittest.TestCase):
    def test_live_activity_has_durable_checkpoint_and_null_intent_restore(self):
        service = SERVICE.read_text()
        checkpoint = CHECKPOINT.read_text()

        self.assertTrue(CHECKPOINT.exists(), "active session checkpoint codec/store contract is missing")
        for marker in (
            "data class ActivitySessionCheckpoint",
            "object ActivitySessionCheckpointCodec",
            "fun encode(",
            "fun decode(",
            "fun canRestore(",
        ):
            self.assertIn(marker, checkpoint)

        for marker in (
            "restorePersistedActivity",
            "saveActivityCheckpoint",
            "clearActivityCheckpoint",
            "if (intent == null)",
            "onTaskRemoved",
        ):
            self.assertIn(marker, service)

        self.assertIn("ActivitySessionCheckpointCodec.canRestore", service)

    def test_main_activity_reopen_requests_restore_before_host_motion_resumes(self):
        source = MAIN.read_text()
        start = source.index("override fun onResume()")
        end = source.index("override fun onPause()", start)
        on_resume = source[start:end]

        self.assertIn("ActivityTrackingService.restorePersistedActivityIfAvailable(this)", on_resume)
        self.assertIn("val activityRestorePending", on_resume)
        self.assertIn("!activityRestorePending", on_resume)
        self.assertLess(
            on_resume.index("restorePersistedActivityIfAvailable"),
            on_resume.index("motionEngine.onHostResume()"),
        )

    def test_service_has_explicit_reopen_restore_action_and_boot_identity(self):
        source = SERVICE.read_text()

        self.assertIn("ACTION_RESTORE_ACTIVITY", source)
        self.assertIn("Settings.Global.BOOT_COUNT", source)
        self.assertIn("bootCount = readBootCount(this)", source)
        self.assertIn("readBootCount(context)", source)
        self.assertIn("canRestore(checkpoint, nowElapsed, bootCount)", source)


if __name__ == "__main__":
    unittest.main()
