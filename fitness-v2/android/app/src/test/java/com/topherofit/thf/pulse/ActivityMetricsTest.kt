package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityMetricsTest {
    @Test
    fun walkingAndRunningUseStepsButCyclingDoesNot() {
        assertTrue(ActivityMode.WALK.usesSteps)
        assertTrue(ActivityMode.RUN.usesSteps)
        assertFalse(ActivityMode.CYCLE.usesSteps)
    }

    @Test
    fun routeDistanceUsesGeodesicDistance() {
        val metres = ActivityMetrics.distanceMetres(31.2001, 29.9187, 31.2011, 29.9187)
        assertEquals(111.2, metres, 2.0)
    }

    @Test
    fun paceAndSpeedAreDerivedFromDistanceAndDuration() {
        assertEquals(10.0, ActivityMetrics.averageSpeedKph(distanceMetres = 5000.0, durationMs = 1_800_000), 0.01)
        assertEquals(6.0, ActivityMetrics.paceMinutesPerKm(distanceMetres = 5000.0, durationMs = 1_800_000), 0.01)
    }

    @Test
    fun caloriesAreExplicitlyWeightAndModeBased() {
        val calories = ActivityMetrics.estimatedCalories(ActivityMode.RUN, weightKg = 70.0, durationMs = 3_600_000)
        assertEquals(581.0, calories, 2.0)
    }
}
