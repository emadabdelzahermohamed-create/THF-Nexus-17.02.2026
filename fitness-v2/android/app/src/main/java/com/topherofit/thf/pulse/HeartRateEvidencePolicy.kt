package com.topherofit.thf.pulse

/**
 * Pure policy for optional heart-rate presentation and provenance.
 *
 * The caller must populate these fields from the actual Health Connect record metadata.
 * This class does not request permissions, read health data, persist samples, or verify a sport session.
 */
enum class HeartRatePermissionState { GRANTED, NOT_GRANTED, REVOKED }

enum class HeartRateOrigin {
    HEALTH_CONNECT_WEARABLE,
    HEALTH_CONNECT_IMPORTED,
    PHONE_SENSOR,
    MANUAL,
    UNKNOWN,
}

enum class HeartRateDeviceType { WATCH, SMARTWATCH, FITNESS_BAND, FITNESS_TRACKER, PHONE, OTHER, UNKNOWN }

enum class HeartRateRecordingMethod {
    AUTOMATICALLY_RECORDED,
    ACTIVELY_RECORDED,
    MANUAL_ENTRY,
    UNKNOWN,
}

enum class HeartRateDisplayState {
    AVAILABLE,
    PERMISSION_REQUIRED,
    PERMISSION_REVOKED,
    SOURCE_UNAVAILABLE,
    NO_DATA,
    STALE_DATA,
    ERROR,
    INVALID_DATA,
}

enum class HeartRateTrustTier { TRUSTED_WEARABLE, IMPORTED_UNVERIFIED, UNVERIFIED, REJECTED }

data class HeartRateEvidence(
    val beatsPerMinute: Double?,
    val observedAtEpochMillis: Long?,
    val sourcePackage: String? = null,
    val deviceType: HeartRateDeviceType = HeartRateDeviceType.UNKNOWN,
    val origin: HeartRateOrigin = HeartRateOrigin.UNKNOWN,
    val recordingMethod: HeartRateRecordingMethod = HeartRateRecordingMethod.UNKNOWN,
    // Least privilege: require the caller to confirm a current grant before exposing a sample.
    val permissionState: HeartRatePermissionState = HeartRatePermissionState.NOT_GRANTED,
    val sourceAvailable: Boolean = true,
    val readError: Boolean = false,
    val recordId: String? = null,
)

data class HeartRateStableRecordKey(
    val sourcePackage: String,
    val recordId: String,
)

data class HeartRateAssessment(
    val state: HeartRateDisplayState,
    val beatsPerMinute: Double?,
    val observedAtEpochMillis: Long?,
    val sourcePackage: String?,
    val deviceType: HeartRateDeviceType,
    val recordingMethod: HeartRateRecordingMethod,
    val trustTier: HeartRateTrustTier,
) {
    /** Heart rate alone is never sufficient evidence to verify a sport session. */
    val canVerifySportProgress: Boolean
        get() = false
}

object HeartRateEvidencePolicy {
    /** Maximum age for a sample to be displayed as current. */
    const val MAX_SAMPLE_AGE_MILLIS: Long = 5 * 60 * 1000L

    /** Allowed future timestamp skew for device/source clock differences. */
    const val MAX_FUTURE_SKEW_MILLIS: Long = 30 * 1000L

    private val wearableDeviceTypes = setOf(
        HeartRateDeviceType.WATCH,
        HeartRateDeviceType.SMARTWATCH,
        HeartRateDeviceType.FITNESS_BAND,
        HeartRateDeviceType.FITNESS_TRACKER,
    )

    private val acceptedRecordingMethods = setOf(
        HeartRateRecordingMethod.AUTOMATICALLY_RECORDED,
        HeartRateRecordingMethod.ACTIVELY_RECORDED,
    )

    /**
     * Stable deduplication identity for Health Connect records only.
     * Exact source package + record ID is required; cross-source IDs never collide.
     * A null result means the sample must not be deduplicated by stable identity.
     */
    fun stableRecordKey(evidence: HeartRateEvidence): HeartRateStableRecordKey? {
        if (evidence.origin != HeartRateOrigin.HEALTH_CONNECT_WEARABLE &&
            evidence.origin != HeartRateOrigin.HEALTH_CONNECT_IMPORTED
        ) return null
        val sourcePackage = evidence.sourcePackage?.trim()?.takeIf { it.isNotEmpty() } ?: return null
        val recordId = evidence.recordId?.trim()?.takeIf { it.isNotEmpty() } ?: return null
        return HeartRateStableRecordKey(sourcePackage, recordId)
    }

    private fun masked(state: HeartRateDisplayState) = HeartRateAssessment(
        state = state,
        beatsPerMinute = null,
        observedAtEpochMillis = null,
        sourcePackage = null,
        deviceType = HeartRateDeviceType.UNKNOWN,
        recordingMethod = HeartRateRecordingMethod.UNKNOWN,
        trustTier = HeartRateTrustTier.UNVERIFIED,
    )

    /**
     * [nowEpochMillis] is injected by the caller so freshness decisions are deterministic.
     * Samples older than [MAX_SAMPLE_AGE_MILLIS] are stale; timestamps more than
     * [MAX_FUTURE_SKEW_MILLIS] ahead of the supplied clock are rejected.
     */
    fun assess(evidence: HeartRateEvidence, nowEpochMillis: Long): HeartRateAssessment {
        when (evidence.permissionState) {
            HeartRatePermissionState.REVOKED -> return masked(HeartRateDisplayState.PERMISSION_REVOKED)
            HeartRatePermissionState.NOT_GRANTED -> return masked(HeartRateDisplayState.PERMISSION_REQUIRED)
            HeartRatePermissionState.GRANTED -> Unit
        }
        if (evidence.readError) return masked(HeartRateDisplayState.ERROR)
        if (!evidence.sourceAvailable) return masked(HeartRateDisplayState.SOURCE_UNAVAILABLE)

        val sourcePackage = evidence.sourcePackage?.trim()?.takeIf { it.isNotEmpty() }
        val bpm = evidence.beatsPerMinute
        if (bpm == null) {
            return HeartRateAssessment(
                state = HeartRateDisplayState.NO_DATA,
                beatsPerMinute = null,
                observedAtEpochMillis = null,
                sourcePackage = sourcePackage,
                deviceType = evidence.deviceType,
                recordingMethod = HeartRateRecordingMethod.UNKNOWN,
                trustTier = HeartRateTrustTier.UNVERIFIED,
            )
        }

        val observedAt = evidence.observedAtEpochMillis
        if (!bpm.isFinite() || bpm !in 30.0..240.0 ||
            observedAt == null || observedAt <= 0L || nowEpochMillis <= 0L
        ) {
            return HeartRateAssessment(
                state = HeartRateDisplayState.INVALID_DATA,
                beatsPerMinute = null,
                observedAtEpochMillis = null,
                sourcePackage = sourcePackage,
                deviceType = evidence.deviceType,
                recordingMethod = evidence.recordingMethod,
                trustTier = HeartRateTrustTier.REJECTED,
            )
        }

        if (observedAt > nowEpochMillis &&
            observedAt - nowEpochMillis > MAX_FUTURE_SKEW_MILLIS
        ) {
            return HeartRateAssessment(
                state = HeartRateDisplayState.INVALID_DATA,
                beatsPerMinute = null,
                observedAtEpochMillis = null,
                sourcePackage = sourcePackage,
                deviceType = evidence.deviceType,
                recordingMethod = evidence.recordingMethod,
                trustTier = HeartRateTrustTier.REJECTED,
            )
        }

        if (nowEpochMillis > observedAt &&
            nowEpochMillis - observedAt > MAX_SAMPLE_AGE_MILLIS
        ) {
            return HeartRateAssessment(
                state = HeartRateDisplayState.STALE_DATA,
                beatsPerMinute = null,
                observedAtEpochMillis = observedAt,
                sourcePackage = sourcePackage,
                deviceType = evidence.deviceType,
                recordingMethod = evidence.recordingMethod,
                trustTier = HeartRateTrustTier.UNVERIFIED,
            )
        }

        val trustTier = when {
            evidence.origin == HeartRateOrigin.HEALTH_CONNECT_WEARABLE &&
                sourcePackage != null &&
                HealthSourceTrustPolicy.isApprovedHealthConnectProvider(sourcePackage) &&
                stableRecordKey(evidence) != null &&
                evidence.deviceType in wearableDeviceTypes &&
                evidence.recordingMethod in acceptedRecordingMethods ->
                HeartRateTrustTier.TRUSTED_WEARABLE

            evidence.origin == HeartRateOrigin.HEALTH_CONNECT_IMPORTED ||
                evidence.origin == HeartRateOrigin.MANUAL ||
                evidence.recordingMethod == HeartRateRecordingMethod.MANUAL_ENTRY ->
                HeartRateTrustTier.IMPORTED_UNVERIFIED

            else -> HeartRateTrustTier.UNVERIFIED
        }

        return HeartRateAssessment(
            state = HeartRateDisplayState.AVAILABLE,
            beatsPerMinute = bpm,
            observedAtEpochMillis = observedAt,
            sourcePackage = sourcePackage,
            deviceType = evidence.deviceType,
            recordingMethod = evidence.recordingMethod,
            trustTier = trustTier,
        )
    }
}
