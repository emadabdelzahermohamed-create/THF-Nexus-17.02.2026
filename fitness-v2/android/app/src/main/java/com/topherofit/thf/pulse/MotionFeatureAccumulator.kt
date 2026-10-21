package com.topherofit.thf.pulse

import java.security.MessageDigest
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sqrt

class MotionFeatureAccumulator {
    private data class OnlineStats(var count: Int = 0, var mean: Double = 0.0, var m2: Double = 0.0, var peak: Double = 0.0) {
        fun add(value: Double) {
            count += 1
            val delta = value - mean
            mean += delta / count
            m2 += delta * (value - mean)
            peak = max(peak, value)
        }
        fun variance(): Double = if (count > 1) m2 / count else 0.0
    }

    private var sessionId = ""
    private var startedAtWallMs = 0L
    private var startedAtElapsedNanos = 0L
    private var capabilities = SensorCapabilities(false, false, false, false, false)
    private var started = false

    private var lastStepCounterTimestamp = Long.MIN_VALUE
    private var lastStepCounterRaw: Float? = null
    private var stepDelta = 0
    private var counterResetCount = 0
    private var lastStepDetectorTimestamp = Long.MIN_VALUE
    private var stepDetectorCount = 0

    private var lastAccelTimestamp = Long.MIN_VALUE
    private var lastGyroTimestamp = Long.MIN_VALUE
    private val accelStats = OnlineStats()
    private val gyroStats = OnlineStats()
    private var activeMotionNanos = 0L
    private var lastAccelWasActive = false

    private var interruptionStartedNanos: Long? = null
    private var interruptionNanos = 0L

    fun start(sessionId: String, startedAtWallMs: Long, startedAtElapsedNanos: Long, capabilities: SensorCapabilities) {
        require(sessionId.isNotBlank())
        this.sessionId = sessionId
        this.startedAtWallMs = startedAtWallMs
        this.startedAtElapsedNanos = startedAtElapsedNanos
        this.capabilities = capabilities
        started = true
    }

    fun acceptStepCounter(rawCount: Float, elapsedNanos: Long) {
        ensureStarted()
        if (elapsedNanos <= lastStepCounterTimestamp || !rawCount.isFinite() || rawCount < 0f) return
        val previous = lastStepCounterRaw
        if (previous != null) {
            if (rawCount >= previous) stepDelta += (rawCount - previous).toInt()
            else counterResetCount += 1
        }
        lastStepCounterRaw = rawCount
        lastStepCounterTimestamp = elapsedNanos
    }

    fun acceptStepDetector(elapsedNanos: Long) {
        ensureStarted()
        if (elapsedNanos <= lastStepDetectorTimestamp) return
        stepDetectorCount += 1
        lastStepDetectorTimestamp = elapsedNanos
    }

    fun acceptAccelerometer(x: Float, y: Float, z: Float, elapsedNanos: Long) {
        ensureStarted()
        if (elapsedNanos <= lastAccelTimestamp) return
        val magnitude = magnitude(x, y, z)
        if (!magnitude.isFinite()) return
        if (lastAccelTimestamp != Long.MIN_VALUE && lastAccelWasActive) {
            activeMotionNanos += (elapsedNanos - lastAccelTimestamp).coerceAtLeast(0L)
        }
        accelStats.add(magnitude)
        lastAccelWasActive = abs(magnitude - GRAVITY) >= ACTIVE_ACCEL_DEVIATION
        lastAccelTimestamp = elapsedNanos
    }

    fun acceptGyroscope(x: Float, y: Float, z: Float, elapsedNanos: Long) {
        ensureStarted()
        if (elapsedNanos <= lastGyroTimestamp) return
        val magnitude = magnitude(x, y, z)
        if (!magnitude.isFinite()) return
        gyroStats.add(magnitude)
        lastGyroTimestamp = elapsedNanos
    }

    fun markInterrupted(startedAtElapsedNanos: Long) {
        ensureStarted()
        if (interruptionStartedNanos == null) interruptionStartedNanos = startedAtElapsedNanos.coerceAtLeast(this.startedAtElapsedNanos)
    }

    fun markResumed(resumedAtElapsedNanos: Long) {
        ensureStarted()
        val interruptionStart = interruptionStartedNanos ?: return
        if (resumedAtElapsedNanos > interruptionStart) interruptionNanos += resumedAtElapsedNanos - interruptionStart
        interruptionStartedNanos = null
    }

    fun snapshot(endedAtWallMs: Long, endedAtElapsedNanos: Long): MotionEvidence {
        ensureStarted()
        val totalNanos = (endedAtElapsedNanos - startedAtElapsedNanos).coerceAtLeast(0L)
        val openInterruption = interruptionStartedNanos?.let { (endedAtElapsedNanos - it).coerceAtLeast(0L) } ?: 0L
        val interruptions = (interruptionNanos + openInterruption).coerceAtMost(totalNanos)
        val activeDurationNanos = (totalNanos - interruptions).coerceAtLeast(0L)
        val activeMotionMs = (activeMotionNanos.coerceAtMost(activeDurationNanos) / NANOS_PER_MS)
        val activeDurationMs = activeDurationNanos / NANOS_PER_MS
        val stationaryFraction = if (activeDurationMs <= 0L) 1.0 else (1.0 - activeMotionMs.toDouble() / activeDurationMs).coerceIn(0.0, 1.0)
        val motionFraction = if (activeDurationMs <= 0L) 0.0 else (activeMotionMs.toDouble() / activeDurationMs).coerceIn(0.0, 1.0)
        val stepSignal = (stepDelta.coerceAtMost(20) / 20.0).coerceIn(0.0, 1.0)
        val detectorSignal = (stepDetectorCount.coerceAtMost(20) / 20.0).coerceIn(0.0, 1.0)
        val inertialSignal = ((accelStats.variance() / 12.0) + (gyroStats.variance() / 1.5)).coerceIn(0.0, 1.0)
        val confidence = (0.45 * motionFraction + 0.20 * inertialSignal + 0.20 * stepSignal + 0.15 * detectorSignal).coerceIn(0.0, 1.0)

        val canonical = listOf(
            sessionId, startedAtWallMs, endedAtWallMs, totalNanos / NANOS_PER_MS, activeDurationMs,
            stepDelta, stepDetectorCount, counterResetCount, accelStats.count, gyroStats.count,
            "%.6f".format(java.util.Locale.ROOT, accelStats.mean), "%.6f".format(java.util.Locale.ROOT, accelStats.variance()),
            "%.6f".format(java.util.Locale.ROOT, gyroStats.mean), "%.6f".format(java.util.Locale.ROOT, gyroStats.variance()),
            activeMotionMs, interruptions / NANOS_PER_MS
        ).joinToString("|")

        return MotionEvidence(
            sessionId = sessionId,
            startedAtWallMs = startedAtWallMs,
            endedAtWallMs = endedAtWallMs,
            elapsedDurationMs = totalNanos / NANOS_PER_MS,
            activeDurationMs = activeDurationMs,
            stepDelta = stepDelta,
            stepDetectorCount = stepDetectorCount,
            counterResetCount = counterResetCount,
            accelerometerSampleCount = accelStats.count,
            gyroscopeSampleCount = gyroStats.count,
            accelerometerMagnitudeMean = accelStats.mean,
            accelerometerMagnitudeVariance = accelStats.variance(),
            accelerometerMagnitudePeak = accelStats.peak,
            gyroscopeMagnitudeMean = gyroStats.mean,
            gyroscopeMagnitudeVariance = gyroStats.variance(),
            gyroscopeMagnitudePeak = gyroStats.peak,
            activeMotionMs = activeMotionMs,
            stationaryFraction = stationaryFraction,
            interruptionMs = interruptions / NANOS_PER_MS,
            capabilities = capabilities,
            localConfidence = confidence,
            evidenceDigest = sha256(canonical),
        )
    }

    private fun ensureStarted() = check(started) { "motion accumulator has not started" }
    private fun magnitude(x: Float, y: Float, z: Float): Double = sqrt(x.toDouble()*x + y.toDouble()*y + z.toDouble()*z)
    private fun sha256(value: String): String = MessageDigest.getInstance("SHA-256")
        .digest(value.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }

    companion object {
        private const val NANOS_PER_MS = 1_000_000L
        private const val GRAVITY = 9.80665
        private const val ACTIVE_ACCEL_DEVIATION = 1.25
    }
}
