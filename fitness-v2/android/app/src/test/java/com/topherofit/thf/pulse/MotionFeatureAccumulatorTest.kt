package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class MotionFeatureAccumulatorTest {
    private val caps = SensorCapabilities(
        stepCounter = true,
        stepDetector = true,
        accelerometer = true,
        gyroscope = true,
        activityRecognitionPermission = true,
    )

    @Test fun stepCounterDeltaAccumulatesAcrossNormalSamples() {
        val a = MotionFeatureAccumulator()
        a.start("session-0001", 1_000L, 1_000_000_000L, caps)
        a.acceptStepCounter(100f, 1_100_000_000L)
        a.acceptStepCounter(112f, 2_100_000_000L)
        assertEquals(12, a.snapshot(3_000L, 3_000_000_000L).stepDelta)
    }

    @Test fun counterResetStartsNewSegmentWithoutNegativeSteps() {
        val a = MotionFeatureAccumulator()
        a.start("session-0002", 1_000L, 1_000_000_000L, caps)
        listOf(500f, 510f, 3f, 8f).forEachIndexed { i, value ->
            a.acceptStepCounter(value, 1_100_000_000L + i * 100_000_000L)
        }
        val e = a.snapshot(3_000L, 3_000_000_000L)
        assertEquals(15, e.stepDelta)
        assertEquals(1, e.counterResetCount)
    }

    @Test fun duplicateAndOutOfOrderTimestampsAreIgnored() {
        val a = MotionFeatureAccumulator()
        a.start("session-0003", 1_000L, 1_000_000_000L, caps)
        a.acceptStepDetector(1_100_000_000L)
        a.acceptStepDetector(1_100_000_000L)
        a.acceptStepDetector(1_050_000_000L)
        a.acceptAccelerometer(0f, 0f, 9.81f, 1_200_000_000L)
        a.acceptAccelerometer(5f, 5f, 5f, 1_200_000_000L)
        val e = a.snapshot(2_000L, 2_000_000_000L)
        assertEquals(1, e.stepDetectorCount)
        assertEquals(1, e.accelerometerSampleCount)
    }

    @Test fun stationaryTraceProducesLowActivityConfidence() {
        val a = MotionFeatureAccumulator()
        a.start("session-0004", 1_000L, 1_000_000_000L, caps)
        repeat(20) { i ->
            val t = 1_100_000_000L + i * 100_000_000L
            a.acceptAccelerometer(0f, 0f, 9.81f, t)
            a.acceptGyroscope(0f, 0f, 0f, t)
        }
        val e = a.snapshot(4_000L, 4_000_000_000L)
        assertTrue(e.activeMotionMs <= 200L)
        assertTrue(e.localConfidence < 0.25)
    }

    @Test fun movingTraceProducesNonZeroMotionFeatures() {
        val stationary = MotionFeatureAccumulator().also {
            it.start("stationary-0001", 1_000L, 1_000_000_000L, caps)
            repeat(20) { i ->
                val t = 1_100_000_000L + i * 100_000_000L
                it.acceptAccelerometer(0f, 0f, 9.81f, t)
                it.acceptGyroscope(0f, 0f, 0f, t)
            }
        }.snapshot(4_000L, 4_000_000_000L)

        val moving = MotionFeatureAccumulator()
        moving.start("moving-000001", 1_000L, 1_000_000_000L, caps)
        repeat(20) { i ->
            val t = 1_100_000_000L + i * 100_000_000L
            val swing = if (i % 2 == 0) 4.0f else -4.0f
            moving.acceptAccelerometer(swing, 2.5f, 9.81f + swing, t)
            moving.acceptGyroscope(0.5f + i * 0.02f, 0.25f, 0.1f, t)
        }
        val e = moving.snapshot(4_000L, 4_000_000_000L)
        assertTrue(e.accelerometerMagnitudeVariance > 0.0)
        assertTrue(e.gyroscopeMagnitudeVariance > 0.0)
        assertTrue(e.localConfidence > stationary.localConfidence)
    }

    @Test fun interruptionTimeIsExcludedFromActiveDuration() {
        val a = MotionFeatureAccumulator()
        a.start("session-0005", 1_000L, 1_000_000_000L, caps)
        a.markInterrupted(2_000_000_000L)
        a.markResumed(4_000_000_000L)
        val e = a.snapshot(6_000L, 6_000_000_000L)
        assertEquals(2_000L, e.interruptionMs)
        assertEquals(3_000L, e.activeDurationMs)
    }
}
