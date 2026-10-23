package com.topherofit.thf.pulse

import android.os.SystemClock

interface MotionClock {
    fun wallTimeMs(): Long
    fun elapsedRealtimeNanos(): Long
}

object AndroidMotionClock : MotionClock {
    override fun wallTimeMs(): Long = System.currentTimeMillis()
    override fun elapsedRealtimeNanos(): Long = SystemClock.elapsedRealtimeNanos()
}

data class MotionSessionState(
    val active: Boolean,
    val sessionId: String?,
    val hostResumed: Boolean,
    val capabilities: SensorCapabilities,
)

class MotionSessionEngine(
    private val gateway: MotionSensorGateway,
    private val clock: MotionClock = AndroidMotionClock,
) : MotionSensorListener {
    private var hostResumed = false
    private var interrupted = false
    private var activeSessionId: String? = null
    private var accumulator: MotionFeatureAccumulator? = null

    fun onHostResume() {
        if (hostResumed) return
        hostResumed = true
        val current = accumulator
        if (current != null) {
            if (interrupted) {
                current.markResumed(clock.elapsedRealtimeNanos())
                interrupted = false
            }
            gateway.startActive(this)
        } else {
            gateway.startLowPower(this)
        }
    }

    fun onHostPause() {
        if (!hostResumed) return
        if (accumulator != null && !interrupted) {
            accumulator?.markInterrupted(clock.elapsedRealtimeNanos())
            interrupted = true
        }
        gateway.stopAll()
        hostResumed = false
    }

    fun startSession(sessionId: String): MotionSessionState {
        require(sessionId.isNotBlank()) { "sessionId is required" }
        val existing = activeSessionId
        if (existing != null) {
            check(existing == sessionId) { "a different motion session is already active" }
            return currentState()
        }
        val next = MotionFeatureAccumulator()
        next.start(
            sessionId = sessionId,
            startedAtWallMs = clock.wallTimeMs(),
            startedAtElapsedNanos = clock.elapsedRealtimeNanos(),
            capabilities = gateway.capabilities(),
        )
        activeSessionId = sessionId
        accumulator = next
        interrupted = false
        if (hostResumed) gateway.startActive(this)
        return currentState()
    }

    fun snapshot(): MotionEvidence? = accumulator?.snapshot(
        endedAtWallMs = clock.wallTimeMs(),
        endedAtElapsedNanos = clock.elapsedRealtimeNanos(),
    )

    fun stopSession(): MotionEvidence? {
        val current = accumulator ?: return null
        val evidence = current.snapshot(clock.wallTimeMs(), clock.elapsedRealtimeNanos())
        accumulator = null
        activeSessionId = null
        interrupted = false
        if (hostResumed) {
            gateway.stopActive()
            gateway.startLowPower(this)
        } else {
            gateway.stopAll()
        }
        return evidence
    }

    fun capabilities(): SensorCapabilities = gateway.capabilities()

    fun currentState(): MotionSessionState = MotionSessionState(
        active = accumulator != null,
        sessionId = activeSessionId,
        hostResumed = hostResumed,
        capabilities = gateway.capabilities(),
    )

    override fun onStepCounter(rawCount: Float, elapsedNanos: Long) {
        accumulator?.acceptStepCounter(rawCount, elapsedNanos)
    }

    override fun onStepDetector(elapsedNanos: Long) {
        accumulator?.acceptStepDetector(elapsedNanos)
    }

    override fun onAccelerometer(x: Float, y: Float, z: Float, elapsedNanos: Long) {
        accumulator?.acceptAccelerometer(x, y, z, elapsedNanos)
    }

    override fun onGyroscope(x: Float, y: Float, z: Float, elapsedNanos: Long) {
        accumulator?.acceptGyroscope(x, y, z, elapsedNanos)
    }
}
