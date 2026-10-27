package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class LiveNotificationTextTest {
    private fun snapshot(
        mode: ActivityMode,
        phase: ActivitySessionPhase = ActivitySessionPhase.ACTIVE,
    ): ActivitySnapshot {
        val armed = phase == ActivitySessionPhase.ARMED
        return ActivitySnapshot(
            active = true,
            mode = mode,
            startedAtWallMs = 1L,
            elapsedMs = if (armed) 0L else 600_000L,
            distanceMetres = if (armed) 0.0 else 1_250.0,
            stepDelta = if (armed) 0 else 432,
            currentSpeedKph = if (armed) 0.0 else 8.0,
            averageSpeedKph = if (armed) 0.0 else 7.5,
            paceMinutesPerKm = if (armed) null else 8.0,
            estimatedCaloriesKcal = if (armed) 0.0 else 55.0,
            gpsPointCount = if (armed) 0 else 3,
            lastAccuracyMetres = 8f,
            route = emptyList(),
            phase = phase,
        )
    }

    @Test fun walkIncludesSessionStepsAndEstimatedCalories() {
        val text = LiveNotificationText.activity(snapshot(ActivityMode.WALK), true, "GPS متصل")
        assertTrue(text.compact.contains("432"))
        assertTrue(text.expanded.contains("1.25"))
        assertTrue(text.expanded.contains("تقديرية"))
    }

    @Test fun runLeadsWithDistanceAndCycleDoesNotInventSteps() {
        assertTrue(LiveNotificationText.activity(snapshot(ActivityMode.RUN), true, "GPS متصل").compact.startsWith("1.25"))
        val cycle = LiveNotificationText.activity(snapshot(ActivityMode.CYCLE), false, "GPS متصل")
        assertFalse(cycle.expanded.contains("خطوة"))
        assertTrue(cycle.expanded.contains("km/h"))
    }

    @Test fun unavailableSensorIsNotZeroMeasuredSteps() {
        val text = LiveNotificationText.activity(snapshot(ActivityMode.WALK), false, "GPS غير متاح")
        assertTrue(text.expanded.contains("الخطوات غير متاحة"))
        assertTrue(text.expanded.contains("GPS غير متاح"))
        assertFalse(text.compact.contains("432"))
    }

    @Test fun armedActivityClearlyWaitsForMeasuredMovement() {
        val text = LiveNotificationText.activity(snapshot(ActivityMode.WALK, ActivitySessionPhase.ARMED), true, "GPS متصل")
        assertTrue(text.compact.contains("بانتظار حركة مقاسة"))
        assertTrue(text.expanded.contains("بانتظار حركة مقاسة"))
        assertTrue(text.compact.contains("0.00 km"))
        assertFalse(text.expanded.contains("55 kcal"))
    }

    @Test fun workoutDoesNotInventDistanceCaloriesOrStepsForStrength() {
        val text = LiveNotificationText.workout(null, "ثبات", null)
        assertFalse(text.expanded.contains("kcal"))
        assertFalse(text.expanded.contains("km"))
        assertTrue(text.expanded.contains("خطوات غير مقاسة"))
    }

    @Test fun stepWorkoutReportsOnlyMeasuredSteps() {
        assertTrue(LiveNotificationText.workout(24, "خطوات", true).compact.contains("24"))
        assertTrue(LiveNotificationText.workout(null, "خطوات", false).expanded.contains("غير متاحة"))
    }
}
