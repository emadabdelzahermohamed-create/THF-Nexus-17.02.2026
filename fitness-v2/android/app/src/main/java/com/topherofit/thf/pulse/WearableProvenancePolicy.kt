package com.topherofit.thf.pulse

enum class SportKind { WALKING, RUNNING, CYCLING, SWIMMING_POOL, SWIMMING_OPEN_WATER, OTHER }
enum class EvidenceOrigin { PHONE_MEASURED, HEALTH_WEARABLE, HEALTH_IMPORTED, MANUAL, UNKNOWN }
enum class CompetitionTrust { VERIFIED, TRUSTED, IMPORTED, MANUAL, REJECTED }

data class SportEvidence(
    val sport: SportKind,
    val origin: EvidenceOrigin,
    val sourcePackage: String? = null,
    val deviceType: String? = null,
    val recordId: String? = null,
    val startEpochMillis: Long,
    val endEpochMillis: Long,
    val hasAcceptedGps: Boolean = false,
    val anomalyRejected: Boolean = false,
)

object WearableProvenancePolicy {
    private val wearableDeviceTypes = setOf("watch", "smartwatch", "fitness_band", "fitness_tracker", "wearable")
    private val reconcilableSports = setOf(SportKind.WALKING, SportKind.RUNNING, SportKind.CYCLING)

    private fun hasWearableDeviceProvenance(evidence: SportEvidence): Boolean =
        !evidence.sourcePackage.isNullOrBlank() &&
            evidence.deviceType?.trim()?.lowercase() in wearableDeviceTypes

    private fun isHealthOrigin(origin: EvidenceOrigin): Boolean =
        origin == EvidenceOrigin.HEALTH_WEARABLE || origin == EvidenceOrigin.HEALTH_IMPORTED

    fun classify(evidence: SportEvidence): CompetitionTrust {
        if (evidence.anomalyRejected || evidence.endEpochMillis <= evidence.startEpochMillis) {
            return CompetitionTrust.REJECTED
        }
        if (evidence.origin == EvidenceOrigin.MANUAL) return CompetitionTrust.MANUAL

        if (evidence.sport == SportKind.SWIMMING_POOL || evidence.sport == SportKind.SWIMMING_OPEN_WATER) {
            // Phone GPS/sensors never verify swimming. Pool sessions legitimately need no GPS.
            val wearable = evidence.origin == EvidenceOrigin.HEALTH_WEARABLE && hasWearableDeviceProvenance(evidence)
            return if (wearable) CompetitionTrust.VERIFIED else when (evidence.origin) {
                EvidenceOrigin.HEALTH_IMPORTED -> CompetitionTrust.IMPORTED
                EvidenceOrigin.MANUAL -> CompetitionTrust.MANUAL
                else -> CompetitionTrust.REJECTED
            }
        }

        return when (evidence.origin) {
            EvidenceOrigin.PHONE_MEASURED -> if (evidence.hasAcceptedGps) CompetitionTrust.VERIFIED else CompetitionTrust.TRUSTED
            EvidenceOrigin.HEALTH_WEARABLE -> if (hasWearableDeviceProvenance(evidence)) CompetitionTrust.TRUSTED else CompetitionTrust.IMPORTED
            EvidenceOrigin.HEALTH_IMPORTED -> CompetitionTrust.IMPORTED
            EvidenceOrigin.MANUAL -> CompetitionTrust.MANUAL
            EvidenceOrigin.UNKNOWN -> CompetitionTrust.REJECTED
        }
    }

    fun isDuplicate(a: SportEvidence, b: SportEvidence, toleranceMillis: Long = 120_000L): Boolean {
        if (a.sport != b.sport) return false

        // A stable Health record identity is authoritative only within the same source package.
        if (!a.recordId.isNullOrBlank() && a.recordId == b.recordId && a.sourcePackage == b.sourcePackage) return true

        // Time proximity is deliberately limited to the P0 reconciliation case: the same
        // walking/running/cycling session observed by the phone and by Health/watch. Treating
        // arbitrary same-sport records as duplicates can silently erase two legitimate sessions.
        if (a.sport !in reconcilableSports) return false
        val phoneHealthPair =
            (a.origin == EvidenceOrigin.PHONE_MEASURED && isHealthOrigin(b.origin)) ||
                (b.origin == EvidenceOrigin.PHONE_MEASURED && isHealthOrigin(a.origin))
        if (!phoneHealthPair) return false

        val startClose = kotlin.math.abs(a.startEpochMillis - b.startEpochMillis) <= toleranceMillis
        val endClose = kotlin.math.abs(a.endEpochMillis - b.endEpochMillis) <= toleranceMillis
        return startClose && endClose
    }
}