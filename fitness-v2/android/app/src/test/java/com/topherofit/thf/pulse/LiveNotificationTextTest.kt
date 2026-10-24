package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class LiveNotificationTextTest {
    private fun snapshot(mode: ActivityMode) = ActivitySnapshot(true, mode, 1L, 600000L,
        1250.0, 432, 8.0, 7.5, 8.0, 55.0, 3, 8f, emptyList())

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
