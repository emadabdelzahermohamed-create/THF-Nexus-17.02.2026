from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse"


class ActivitySessionRecoveryContractTest(unittest.TestCase):
    def test_live_activity_has_durable_checkpoint_and_null_intent_restore(self):
        checkpoint = PKG / "ActivitySessionCheckpoint.kt"
        service = (PKG / "ActivityTrackingService.kt").read_text()

        self.assertTrue(checkpoint.exists(), "active session checkpoint codec/store contract is missing")
        source = checkpoint.read_text()
        for marker in (
            "data class ActivitySessionCheckpoint",
            "object ActivitySessionCheckpointCodec",
            "fun encode(",
            "fun decode(",
            "fun canRestore(",
        ):
            self.assertIn(marker, source)

        for marker in (
            "restorePersistedActivity",
            "saveActivityCheckpoint",
            "clearActivityCheckpoint",
            "if (intent == null)",
            "onTaskRemoved",
        ):
            self.assertIn(marker, service)

        # Process restart must not silently claim reboot recovery: elapsedRealtime
        # continuity is required before restoring an in-flight session.
        self.assertIn("ActivitySessionCheckpointCodec.canRestore", service)


if __name__ == "__main__":
    unittest.main()
