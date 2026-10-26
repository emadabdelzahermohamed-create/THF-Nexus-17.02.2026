package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
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
    fun invalidCoordinatesDoNotProduceRouteDistance() {
        assertEquals(0.0, ActivityMetrics.distanceMetres(Double.NaN, 29.9187, 31.2011, 29.9187), 0.0)
        assertEquals(0.0, ActivityMetrics.distanceMetres(91.0, 29.9187, 31.2011, 29.9187), 0.0)
        assertEquals(0.0, ActivityMetrics.distanceMetres(31.2001, 181.0, 31.2011, 29.9187), 0.0)
    }

    @Test
    fun paceAndSpeedAreDerivedFromDistanceAndDuration() {
        assertEquals(10.0, ActivityMetrics.averageSpeedKph(distanceMetres = 5000.0, durationMs = 1_800_000), 0.01)
        assertEquals(6.0, requireNotNull(ActivityMetrics.paceMinutesPerKm(distanceMetres = 5000.0, durationMs = 1_800_000)), 0.01)
    }

    @Test
    fun nonFiniteDistanceNeverProducesSpeedOrPace() {
        assertEquals(0.0, ActivityMetrics.averageSpeedKph(Double.NaN, 60_000), 0.0)
        assertEquals(0.0, ActivityMetrics.averageSpeedKph(Double.POSITIVE_INFINITY, 60_000), 0.0)
        assertNull(ActivityMetrics.paceMinutesPerKm(Double.NaN, 60_000))
        assertNull(ActivityMetrics.paceMinutesPerKm(Double.POSITIVE_INFINITY, 60_000))
    }

    @Test
    fun paceIsUnavailableUntilThereIsUsableDistanceAndDuration() {
        assertNull(ActivityMetrics.paceMinutesPerKm(0.0, 60_000))
        assertNull(ActivityMetrics.paceMinutesPerKm(9.0, 60_000))
        assertNull(ActivityMetrics.paceMinutesPerKm(100.0, 0))
    }

    @Test
    fun caloriesAreExplicitlyWeightAndModeBased() {
        val calories = ActivityMetrics.estimatedCalories(ActivityMode.RUN, weightKg = 70.0, durationMs = 3_600_000)
        assertEquals(581.0, calories, 2.0)
    }

    @Test
    fun caloriesStayZeroWhenWeightOrDurationIsInvalid() {
        assertEquals(0.0, ActivityMetrics.estimatedCalories(ActivityMode.WALK, Double.NaN, 60_000), 0.0)
        assertEquals(0.0, ActivityMetrics.estimatedCalories(ActivityMode.RUN, Double.POSITIVE_INFINITY, 60_000), 0.0)
        assertEquals(0.0, ActivityMetrics.estimatedCalories(ActivityMode.CYCLE, 70.0, 0), 0.0)
        assertEquals(0.0, ActivityMetrics.estimatedCalories(ActivityMode.CYCLE, 70.0, -1), 0.0)
    }
}
