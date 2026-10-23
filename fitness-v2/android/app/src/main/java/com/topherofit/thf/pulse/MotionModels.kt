package com.topherofit.thf.pulse

data class SensorCapabilities(
    val stepCounter: Boolean,
    val stepDetector: Boolean,
    val accelerometer: Boolean,
    val gyroscope: Boolean,
    val activityRecognitionPermission: Boolean,
)

enum class MotionSensorType { STEP_COUNTER, STEP_DETECTOR, ACCELEROMETER, GYROSCOPE }

enum class DetectedActivity { STATIONARY, WALKING, RUNNING, ACTIVE, UNKNOWN }

data class MotionEvidence(
    val sessionId: String,
    val startedAtWallMs: Long,
    val endedAtWallMs: Long,
    val elapsedDurationMs: Long,
    val activeDurationMs: Long,
    val stepDelta: Int,
    val stepDetectorCount: Int,
    val counterResetCount: Int,
    val accelerometerSampleCount: Int,
    val gyroscopeSampleCount: Int,
    val accelerometerMagnitudeMean: Double,
    val accelerometerMagnitudeVariance: Double,
    val accelerometerMagnitudePeak: Double,
    val gyroscopeMagnitudeMean: Double,
    val gyroscopeMagnitudeVariance: Double,
    val gyroscopeMagnitudePeak: Double,
    val activeMotionMs: Long,
    val stationaryFraction: Double,
    val interruptionMs: Long,
    val capabilities: SensorCapabilities,
    val localConfidence: Double,
    val detectedActivity: DetectedActivity,
    val activityConfidence: Double,
    val plausibleForRewards: Boolean,
    val plausibilityReasons: List<String>,
    val evidenceDigest: String,
) {
    /** Cross-check cumulative Step Counter against Step Detector when both are available. */
    val hasConsistentHardwareStepEvidence: Boolean
        get() {
            if (stepDelta < 0 || stepDetectorCount < 0) return false
            if (capabilities.stepCounter && capabilities.stepDetector) {
                if (stepDelta == 0 || stepDetectorCount == 0) return false
                val larger = maxOf(stepDelta, stepDetectorCount).toDouble()
                val difference = kotlin.math.abs(stepDelta - stepDetectorCount).toDouble()
                return difference / larger <= 0.35
            }
            return (capabilities.stepCounter && stepDelta > 0) ||
                (capabilities.stepDetector && stepDetectorCount > 0)
        }

    /** Short bursts may drive live UI/activity detection but cannot earn verified rewards. */
    val hasSufficientRewardEvidenceWindow: Boolean
        get() = elapsedDurationMs >= 10_000L &&
            activeDurationMs >= 5_000L &&
            activeMotionMs >= 3_000L &&
            interruptionMs.coerceAtLeast(0L) <= elapsedDurationMs / 2

    /** Require every motion axis available on the phone to participate in reward verification. */
    val hasAvailableMotionAxisEvidence: Boolean
        get() = capabilities.accelerometer &&
            accelerometerSampleCount > 0 &&
            (!capabilities.gyroscope || gyroscopeSampleCount > 0)

    /** Reject internally inconsistent timing/counter evidence before any reward decision. */
    val hasCoherentEvidenceBounds: Boolean
        get() = startedAtWallMs > 0L &&
            endedAtWallMs >= startedAtWallMs &&
            elapsedDurationMs >= 0L &&
            activeDurationMs in 0L..elapsedDurationMs &&
            activeMotionMs in 0L..activeDurationMs &&
            interruptionMs in 0L..elapsedDurationMs &&
            stepDelta >= 0 &&
            stepDetectorCount >= 0 &&
            counterResetCount >= 0 &&
            accelerometerSampleCount >= 0 &&
            gyroscopeSampleCount >= 0

    /**
     * Machine-readable rejection reasons make QA/reward decisions auditable without trusting a
     * Connected label or manual input. Empty means the local sensor evidence gate passed.
     */
    val rewardVerificationRejectionReasons: List<String>
        get() = buildList {
            if (!hasCoherentEvidenceBounds) add("EVIDENCE_BOUNDS_INVALID")
            if (!plausibleForRewards) add("IMPLAUSIBLE_MOTION")
            if (!capabilities.activityRecognitionPermission) add("ACTIVITY_RECOGNITION_MISSING")
            if (!capabilities.stepCounter && !capabilities.stepDetector) add("STEP_SENSOR_UNAVAILABLE")
            if (!hasConsistentHardwareStepEvidence) add("STEP_EVIDENCE_INCONSISTENT")
            if (!hasSufficientRewardEvidenceWindow) add("EVIDENCE_WINDOW_INSUFFICIENT")
            if (!hasAvailableMotionAxisEvidence) add("MOTION_AXIS_EVIDENCE_MISSING")
            if (localConfidence < 0.60) add("LOCAL_CONFIDENCE_LOW")
            if (activityConfidence < 0.60) add("ACTIVITY_CONFIDENCE_LOW")
            if (detectedActivity == DetectedActivity.STATIONARY) add("ACTIVITY_STATIONARY")
            if (detectedActivity == DetectedActivity.UNKNOWN) add("ACTIVITY_UNKNOWN")
        }

    /** Manual/imported values alone cannot satisfy this conservative local reward gate. */
    val sensorVerifiedForRewards: Boolean
        get() = rewardVerificationRejectionReasons.isEmpty()
}
