package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Metadata

data class HealthRecordEvidenceAssessment(
    val integrityClass: IntegrityClass,
    val verifiedForRewards: Boolean,
    val reason: String,
)

object HealthRecordEvidencePolicy {
    fun assess(
        appPackageName: String,
        dataOrigin: String,
        recordType: String,
        recordId: String,
        trustedRecordingMethod: Boolean,
        deviceType: Int? = null,
        recordingMethod: Int? = null,
        exerciseType: Int? = null,
        startEpochMillis: Long? = null,
        endEpochMillis: Long? = null,
        isExerciseSession: Boolean = false,
    ): HealthRecordEvidenceAssessment {
        val app = appPackageName.trim()
        val origin = dataOrigin.trim()
        val type = recordType.trim()
        val id = recordId.trim()

        fun supported(reason: String) = HealthRecordEvidenceAssessment(
            integrityClass = IntegrityClass.SUPPORTED,
            verifiedForRewards = false,
            reason = reason,
        )

        if (origin.equals(app, ignoreCase = true) && app.isNotEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.REJECTED,
                verifiedForRewards = false,
                reason = "SELF_AUTHORED",
            )
        }
        if (!trustedRecordingMethod) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "MANUAL_OR_UNKNOWN_METHOD",
            )
        }
        if (origin.isEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "UNKNOWN_ORIGIN",
            )
        }
        if (type.isEmpty() || id.isEmpty()) {
            return supported("INCOMPLETE_PROVIDER_IDENTITY")
        }

        // The repository passes this typed flag from the actual record instance.
        // Keep the class-name fallback for existing direct policy callers, but do not rely on
        // simpleName alone because runtime minification may rename library classes.
        val isExerciseSessionRecord = isExerciseSession || type == ExerciseSessionRecord::class.simpleName
        if (isExerciseSessionRecord && exerciseType == null) {
            return supported("MISSING_EXERCISE_TYPE")
        }
        if (
            isExerciseSessionRecord &&
            (startEpochMillis == null || endEpochMillis == null ||
                startEpochMillis < 0L || endEpochMillis <= startEpochMillis)
        ) {
            return supported("INVALID_EXERCISE_SESSION_TIME")
        }
        if (!HealthSourceTrustPolicy.isApprovedHealthConnectProvider(origin)) {
            return supported("UNTRUSTED_PROVIDER")
        }
        if (!HealthSourceTrustPolicy.isCompatibleActivityDeviceType(deviceType)) {
            return supported("INCOMPATIBLE_OR_UNKNOWN_DEVICE_CLASS")
        }

        val swimmingSport = when (exerciseType) {
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL -> SportKind.SWIMMING_POOL
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER -> SportKind.SWIMMING_OPEN_WATER
            else -> null
        }
        if (isExerciseSessionRecord && swimmingSport != null) {
            val deviceLabel = HealthSourceTrustPolicy.swimmingDeviceLabel(deviceType)
            val swimmingOrigin = if (deviceLabel != null) {
                EvidenceOrigin.HEALTH_WEARABLE
            } else {
                EvidenceOrigin.HEALTH_IMPORTED
            }
            val swimmingMethod = when (recordingMethod) {
                Metadata.RECORDING_METHOD_ACTIVELY_RECORDED -> SwimmingRecordingMethod.ACTIVE
                Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED -> SwimmingRecordingMethod.AUTOMATIC
                else -> SwimmingRecordingMethod.UNKNOWN
            }
            val decision = SwimmingEligibilityPolicy.evaluate(
                SwimmingEvidence(
                    sport = swimmingSport,
                    origin = swimmingOrigin,
                    sourcePackage = origin,
                    deviceType = deviceLabel,
                    recordId = id,
                    recordKind = SwimmingRecordKind.EXERCISE_SESSION,
                    recordingMethod = swimmingMethod,
                    startEpochMillis = requireNotNull(startEpochMillis),
                    endEpochMillis = requireNotNull(endEpochMillis),
                ),
            )
            if (!decision.eligibleForVerifiedSwimmingProgress) {
                return supported("SWIMMING_INELIGIBLE_${decision.reason.name}")
            }
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.VERIFIED,
                verifiedForRewards = true,
                reason = "APPROVED_PROVIDER_WITH_COMPATIBLE_SWIMMING_WEARABLE_METADATA",
            )
        }

        return HealthRecordEvidenceAssessment(
            integrityClass = IntegrityClass.VERIFIED,
            verifiedForRewards = true,
            reason = "APPROVED_PROVIDER_WITH_DEVICE_METADATA",
        )
    }
}
