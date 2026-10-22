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
    /**
     * Cross-check cumulative Step Counter evidence against Step Detector events whenever both
     * sensors are available. Devices exposing only one Android step sensor remain supported.
     */
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

    /**
     * Require a minimum evidence window before issuing locally verified reward credit.
     * Very short bursts remain useful for live activity detection but cannot earn rewards.
     */
    val hasSufficientRewardEvidenceWindow: Boolean
        get() = elapsedDurationMs >= 10_000L &&
            activeDurationMs >= 5_000L &&
            activeMotionMs >= 3_000L &&
            interruptionMs.coerceAtLeast(0L) <= elapsedDurationMs / 2

    /**
     * Require the motion axes actually available on the device to participate in verification.
     * Accelerometer evidence is mandatory. When a gyroscope exists, reward verification also
     * requires gyroscope samples, preventing a step-only/injected stream from bypassing the
     * richer motion evidence available on capable phones. Devices without a gyro are not
     * penalized and ordinary local tracking is unaffected.
     */
    val hasAvailableMotionAxisEvidence: Boolean
        get() = capabilities.accelerometer &&
            accelerometerSampleCount > 0 &&
            (!capabilities.gyroscope || gyroscopeSampleCount > 0)

    /**
     * Conservative local reward gate. Manual/imported values alone cannot satisfy it. Server
     * and high-value actions may impose stronger checks such as Play Integrity independently.
     */
    val sensorVerifiedForRewards: Boolean
        get() = plausibleForRewards &&
            capabilities.activityRecognitionPermission &&
            (capabilities.stepCounter || capabilities.stepDetector) &&
            localConfidence >= 0.60 &&
            activityConfidence >= 0.60 &&
            hasConsistentHardwareStepEvidence &&
            hasSufficientRewardEvidenceWindow &&
            hasAvailableMotionAxisEvidence &&
            detectedActivity != DetectedActivity.STATIONARY &&
            detectedActivity != DetectedActivity.UNKNOWN
}
