package com.topherofit.thf.pulse

/**
 * Fail-closed policy for actions that turn locally measured fitness into scarce/public value.
 * Ordinary local tracking and QA builds do not call this gate.
 *
 * Play Integrity verdicts must be produced and verified server-side; a client boolean/token is
 * never treated as proof. The server binds the verdict to [workoutReceiptId] and rejects reuse.
 */
enum class HighValueAction { REWARD_CLAIM, LEADERBOARD_SUBMIT }

data class HighValueActionEvidence(
    val action: HighValueAction,
    val workoutReceiptId: String,
    val sensorVerifiedForRewards: Boolean,
    val healthVerifiedForRewards: Boolean,
    val playIntegrityVerifiedByServer: Boolean,
    val receiptFreshAndUnused: Boolean,
)

data class HighValueActionDecision(
    val allowed: Boolean,
    val rejectionReasons: List<String>,
)

object HighValueActionPolicy {
    fun evaluate(evidence: HighValueActionEvidence): HighValueActionDecision {
        val reasons = buildList {
            if (evidence.workoutReceiptId.isBlank()) add("WORKOUT_RECEIPT_MISSING")
            if (!evidence.sensorVerifiedForRewards && !evidence.healthVerifiedForRewards) {
                add("VERIFIED_ACTIVITY_EVIDENCE_MISSING")
            }
            if (!evidence.playIntegrityVerifiedByServer) add("PLAY_INTEGRITY_NOT_SERVER_VERIFIED")
            if (!evidence.receiptFreshAndUnused) add("WORKOUT_RECEIPT_REPLAY_OR_STALE")
        }
        return HighValueActionDecision(reasons.isEmpty(), reasons)
    }
}
