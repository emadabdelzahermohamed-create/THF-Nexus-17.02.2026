package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class MotionSessionEngineTest {
    private class FakeClock(var wall: Long = 1_000L, var elapsed: Long = 1_000_000_000L) : MotionClock {
        override fun wallTimeMs(): Long = wall
        override fun elapsedRealtimeNanos(): Long = elapsed
        fun advanceMs(ms: Long) { wall += ms; elapsed += ms * 1_000_000L }
    }

    private class FakeGateway(private val caps: SensorCapabilities) : MotionSensorGateway {
        var lowPowerStarts = 0
        var activeStarts = 0
        var activeStops = 0
        var allStops = 0
        var listener: MotionSensorListener? = null
        override fun capabilities(): SensorCapabilities = caps
        override fun startLowPower(listener: MotionSensorListener) { this.listener = listener; lowPowerStarts++ }
        override fun startActive(listener: MotionSensorListener) { this.listener = listener; activeStarts++ }
        override fun stopActive() { activeStops++ }
        override fun stopAll() { allStops++ }
        fun stepCounter(value: Float, t: Long) = listener?.onStepCounter(value, t)
        fun stepDetector(t: Long) = listener?.onStepDetector(t)
        fun accel(x: Float, y: Float, z: Float, t: Long) = listener?.onAccelerometer(x, y, z, t)
    }

    private fun caps(gyro: Boolean = true, detector: Boolean = true) = SensorCapabilities(
        stepCounter = true, stepDetector = detector, accelerometer = true, gyroscope = gyro,
        activityRecognitionPermission = true,
    )

    @Test fun resumeWithoutWorkoutStartsLowPowerOnly() {
        val gateway = FakeGateway(caps())
        val engine = MotionSessionEngine(gateway, FakeClock())
        engine.onHostResume()
        assertEquals(1, gateway.lowPowerStarts)
        assertEquals(0, gateway.activeStarts)
    }

    @Test fun startSessionEnablesActiveSensors() {
        val gateway = FakeGateway(caps())
        val engine = MotionSessionEngine(gateway, FakeClock())
        engine.onHostResume()
        val state = engine.startSession("session-1001")
        assertTrue(state.active)
        assertEquals("session-1001", state.sessionId)
        assertEquals(1, gateway.activeStarts)
    }

    @Test fun stopSessionReturnsEvidenceAndStopsHighRateSensors() {
        val gateway = FakeGateway(caps())
        val clock = FakeClock()
        val engine = MotionSessionEngine(gateway, clock)
        engine.onHostResume(); engine.startSession("session-1002")
        gateway.stepCounter(100f, clock.elapsed); clock.advanceMs(500)
        gateway.stepCounter(106f, clock.elapsed); gateway.stepDetector(clock.elapsed)
        val evidence = engine.stopSession()
        assertNotNull(evidence)
        assertEquals(6, evidence!!.stepDelta)
        assertTrue(gateway.activeStops >= 1)
        assertFalse(engine.currentState().active)
    }

    @Test fun pauseDuringSessionStopsAllSensorsAndMarksInterruption() {
        val gateway = FakeGateway(caps())
        val clock = FakeClock()
        val engine = MotionSessionEngine(gateway, clock)
        engine.onHostResume(); engine.startSession("session-1003")
        clock.advanceMs(1_000); engine.onHostPause()
        clock.advanceMs(2_000); engine.onHostResume()
        clock.advanceMs(1_000)
        val evidence = engine.stopSession()!!
        assertTrue(gateway.allStops >= 1)
        assertEquals(2_000L, evidence.interruptionMs)
    }

    @Test fun resumeDuringSessionRestartsActiveSensorsWithoutNewSession() {
        val gateway = FakeGateway(caps())
        val clock = FakeClock()
        val engine = MotionSessionEngine(gateway, clock)
        engine.onHostResume(); engine.startSession("session-1004")
        engine.onHostPause(); clock.advanceMs(500); engine.onHostResume()
        assertEquals("session-1004", engine.currentState().sessionId)
        assertEquals(2, gateway.activeStarts)
    }

    @Test fun missingGyroStillProducesPartialEvidence() {
        val gateway = FakeGateway(caps(gyro = false))
        val clock = FakeClock()
        val engine = MotionSessionEngine(gateway, clock)
        engine.onHostResume(); engine.startSession("session-1005")
        gateway.accel(3f, 2f, 11f, clock.elapsed); clock.advanceMs(250)
        gateway.accel(-3f, 2f, 7f, clock.elapsed)
        val evidence = engine.stopSession()!!
        assertFalse(evidence.capabilities.gyroscope)
        assertEquals(0, evidence.gyroscopeSampleCount)
        assertTrue(evidence.accelerometerSampleCount > 0)
    }

    @Test fun missingStepDetectorStillUsesStepCounter() {
        val gateway = FakeGateway(caps(detector = false))
        val clock = FakeClock()
        val engine = MotionSessionEngine(gateway, clock)
        engine.onHostResume(); engine.startSession("session-1006")
        gateway.stepCounter(50f, clock.elapsed); clock.advanceMs(500); gateway.stepCounter(55f, clock.elapsed)
        val evidence = engine.stopSession()!!
        assertEquals(5, evidence.stepDelta)
        assertEquals(0, evidence.stepDetectorCount)
    }

    @Test fun doubleStartSameSessionIsIdempotent() {
        val gateway = FakeGateway(caps())
        val engine = MotionSessionEngine(gateway, FakeClock())
        engine.onHostResume()
        val first = engine.startSession("session-1007")
        val second = engine.startSession("session-1007")
        assertEquals(first.sessionId, second.sessionId)
        assertEquals(1, gateway.activeStarts)
    }

    @Test(expected = IllegalStateException::class)
    fun startDifferentSessionWhileActiveIsRejected() {
        val engine = MotionSessionEngine(FakeGateway(caps()), FakeClock())
        engine.onHostResume(); engine.startSession("session-1008")
        engine.startSession("session-OTHER")
    }
}
