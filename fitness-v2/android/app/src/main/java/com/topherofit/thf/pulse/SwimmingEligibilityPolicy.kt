package com.topherofit.thf.pulse

import java.util.Locale

/** Health Connect metadata required before a swimming record may enter the verified-progress path. */
enum class SwimmingRecordKind { EXERCISE_SESSION, OTHER }
enum class SwimmingRecordingMethod { AUTOMATIC, ACTIVE, MANUAL, UNKNOWN }

enum class SwimmingEligibilityReason {
    ELIGIBLE,
    NOT_SWIMMING,
    ANOMALY_REJECTED,
    INVALID_TIME_RANGE,
    NON_WEARABLE_ORIGIN,
    MISSING_SOURCE_PACKAGE,
    UNTRUSTED_SOURCE_PACKAGE,
    INCOMPATIBLE_DEVICE,
    NOT_EXERCISE_SESSION,
    UNSUPPORTED_RECORDING_METHOD,
    MISSING_RECORD_ID,
}

data class SwimmingEvidence(
    val sport: SportKind,
    val origin: EvidenceOrigin,
    val sourcePackage: String?,
    val deviceType: String?,
    val recordId: String?,
    val recordKind: SwimmingRecordKind,
    val recordingMethod: SwimmingRecordingMethod,
    val startEpochMillis: Long,
    val endEpochMillis: Long,
    val anomalyRejected: Boolean = false,
)

data class SwimmingEligibilityDecision(
    val eligibleForVerifiedSwimmingProgress: Boolean,
    val reason: SwimmingEligibilityReason,
)

/**
 * Conservative metadata gate only. It does not attest that a watch or sensor is genuine.
 * Callers must derive these fields from the Health Connect record, preserve its provenance,
 * and keep physical-device and downstream anti-cheat checks as separate gates.
 */
object SwimmingEligibilityPolicy {
    private val compatibleDeviceTypes = setOf("watch", "smartwatch", "fitness_band", "fitness_tracker")

    fun evaluate(evidence: SwimmingEvidence): SwimmingEligibilityDecision {
        fun reject(reason: SwimmingEligibilityReason) = SwimmingEligibilityDecision(false, reason)

        if (evidence.sport != SportKind.SWIMMING_POOL && evidence.sport != SportKind.SWIMMING_OPEN_WATER) {
            return reject(SwimmingEligibilityReason.NOT_SWIMMING)
        }
        if (evidence.anomalyRejected) return reject(SwimmingEligibilityReason.ANOMALY_REJECTED)
        if (evidence.startEpochMillis < 0L || evidence.endEpochMillis <= evidence.startEpochMillis) {
            return reject(SwimmingEligibilityReason.INVALID_TIME_RANGE)
        }
        if (evidence.origin != EvidenceOrigin.HEALTH_WEARABLE) {
            return reject(SwimmingEligibilityReason.NON_WEARABLE_ORIGIN)
        }
        if (evidence.sourcePackage.isNullOrBlank()) {
            return reject(SwimmingEligibilityReason.MISSING_SOURCE_PACKAGE)
        }
        if (!HealthSourceTrustPolicy.isApprovedHealthConnectProvider(evidence.sourcePackage)) {
            return reject(SwimmingEligibilityReason.UNTRUSTED_SOURCE_PACKAGE)
        }
        if (evidence.deviceType?.trim()?.lowercase(Locale.ROOT) !in compatibleDeviceTypes) {
            return reject(SwimmingEligibilityReason.INCOMPATIBLE_DEVICE)
        }
        if (evidence.recordKind != SwimmingRecordKind.EXERCISE_SESSION) {
            return reject(SwimmingEligibilityReason.NOT_EXERCISE_SESSION)
        }
        if (evidence.recordingMethod != SwimmingRecordingMethod.AUTOMATIC &&
            evidence.recordingMethod != SwimmingRecordingMethod.ACTIVE) {
            return reject(SwimmingEligibilityReason.UNSUPPORTED_RECORDING_METHOD)
        }
        if (evidence.recordId.isNullOrBlank()) {
            return reject(SwimmingEligibilityReason.MISSING_RECORD_ID)
        }
        return SwimmingEligibilityDecision(true, SwimmingEligibilityReason.ELIGIBLE)
    }
}
