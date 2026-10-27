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
    val permissionState: HeartRatePermissionState = HeartRatePermissionState.GRANTED,
    val sourceAvailable: Boolean = true,
    val readError: Boolean = false,
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

    private fun masked(state: HeartRateDisplayState) = HeartRateAssessment(
        state = state,
        beatsPerMinute = null,
        observedAtEpochMillis = null,
        sourcePackage = null,
        deviceType = HeartRateDeviceType.UNKNOWN,
        recordingMethod = HeartRateRecordingMethod.UNKNOWN,
        trustTier = HeartRateTrustTier.UNVERIFIED,
    )

    fun assess(evidence: HeartRateEvidence): HeartRateAssessment {
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
        if (!bpm.isFinite() || bpm !in 30.0..240.0 || observedAt == null || observedAt <= 0L) {
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

        val trustTier = when {
            evidence.origin == HeartRateOrigin.HEALTH_CONNECT_WEARABLE &&
                sourcePackage != null &&
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
