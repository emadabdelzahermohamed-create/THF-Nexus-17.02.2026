package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class HighValueActionPolicyTest {
    @Test fun highValueActionRequiresServerIntegrityAndFreshReceipt() {
        val decision = HighValueActionPolicy.evaluate(
            HighValueActionEvidence(HighValueAction.REWARD_CLAIM, "receipt-1", true, false, false, true)
        )
        assertFalse(decision.allowed)
        assertTrue("PLAY_INTEGRITY_NOT_SERVER_VERIFIED" in decision.rejectionReasons)
    }

    @Test fun manualOnlyEvidenceCannotAuthorizeReward() {
        val decision = HighValueActionPolicy.evaluate(
            HighValueActionEvidence(HighValueAction.REWARD_CLAIM, "receipt-2", false, false, true, true)
        )
        assertFalse(decision.allowed)
        assertTrue("VERIFIED_ACTIVITY_EVIDENCE_MISSING" in decision.rejectionReasons)
    }

    @Test fun verifiedSensorEvidenceCanAuthorizeFreshServerAttestedAction() {
        val decision = HighValueActionPolicy.evaluate(
            HighValueActionEvidence(HighValueAction.LEADERBOARD_SUBMIT, "receipt-3", true, false, true, true)
        )
        assertTrue(decision.allowed)
        assertTrue(decision.rejectionReasons.isEmpty())
    }
}
