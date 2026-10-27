package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityNotificationTimingPolicyTest {
    private fun snapshot(phase: ActivitySessionPhase, startedAtWallMs: Long) = ActivitySnapshot(
        active = true,
        mode = ActivityMode.WALK,
        startedAtWallMs = startedAtWallMs,
        elapsedMs = 0L,
        distanceMetres = 0.0,
        stepDelta = 0,
        currentSpeedKph = 0.0,
        averageSpeedKph = 0.0,
        paceMinutesPerKm = null,
        estimatedCaloriesKcal = 0.0,
        gpsPointCount = 0,
        lastAccuracyMetres = null,
        route = emptyList(),
        phase = phase,
    )

    @Test
    fun armedActivityDoesNotShowAnElapsedChronometer() {
        val timing = ActivityNotificationTimingPolicy.forActivity(
            snapshot(ActivitySessionPhase.ARMED, startedAtWallMs = 1_000L),
            nowWallMs = 9_000L,
        )

        assertEquals(9_000L, timing.whenWallMs)
        assertFalse(timing.showWhen)
        assertFalse(timing.usesChronometer)
    }

    @Test
    fun activeActivityChronometerStartsAtValidatedActivationTime() {
        val timing = ActivityNotificationTimingPolicy.forActivity(
            snapshot(ActivitySessionPhase.ACTIVE, startedAtWallMs = 2_500L),
            nowWallMs = 9_000L,
        )

        assertEquals(2_500L, timing.whenWallMs)
        assertTrue(timing.showWhen)
        assertTrue(timing.usesChronometer)
    }

    @Test
    fun workoutChronometerStillUsesTheWorkoutStart() {
        val timing = ActivityNotificationTimingPolicy.forWorkout(sessionStartedAtWallMs = 1_500L)

        assertEquals(1_500L, timing.whenWallMs)
        assertTrue(timing.showWhen)
        assertTrue(timing.usesChronometer)
    }
}
