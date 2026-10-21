package com.topherofit.thf.pulse

data class SensorCapabilities(
    val stepCounter: Boolean,
    val stepDetector: Boolean,
    val accelerometer: Boolean,
    val gyroscope: Boolean,
    val activityRecognitionPermission: Boolean,
)

enum class MotionSensorType { STEP_COUNTER, STEP_DETECTOR, ACCELEROMETER, GYROSCOPE }

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
    val evidenceDigest: String,
)
