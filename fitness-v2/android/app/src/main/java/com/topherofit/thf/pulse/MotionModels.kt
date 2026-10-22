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
     * Conservative local reward gate. A session must be plausible, confidently classified,
     * include a hardware step signal, and contain accelerometer evidence. Manual entry alone
     * can therefore never satisfy this gate. Server/high-value actions may impose stronger
     * checks (for example Play Integrity) without blocking ordinary local tracking.
     *
     * Require the hardware step capability as well as observed step evidence. This prevents
     * imported/manual step values from becoming reward-verifying evidence on devices where
     * no Step Counter/Detector was actually available to the session.
     *
     * Cross-check cumulative Step Counter evidence against Step Detector events whenever both
     * sensors are available. Requiring both signals for reward credit makes synthetic/imported
     * step injection materially harder while preserving tracking on devices that expose only
     * one of the two Android step sensors.
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
     * Very short bursts are useful for live UI/activity detection, but are too easy to spoof
     * or misclassify to serve as reward evidence. This does not block local tracking.
     */
    val hasSufficientRewardEvidenceWindow: Boolean
        get() = elapsedDurationMs >= 10_000L &&
            activeDurationMs >= 5_000L &&
            activeMotionMs >= 3_000L &&
            interruptionMs.coerceAtLeast(0L) <= elapsedDurationMs / 2

    val sensorVerifiedForRewards: Boolean
        get() = plausibleForRewards &&
            capabilities.activityRecognitionPermission &&
            (capabilities.stepCounter || capabilities.stepDetector) &&
            capabilities.accelerometer &&
            localConfidence >= 0.60 &&
            activityConfidence >= 0.60 &&
            hasConsistentHardwareStepEvidence &&
            hasSufficientRewardEvidenceWindow &&
            accelerometerSampleCount > 0 &&
            detectedActivity != DetectedActivity.STATIONARY &&
            detectedActivity != DetectedActivity.UNKNOWN
}
