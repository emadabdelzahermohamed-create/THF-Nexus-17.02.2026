package com.topherofit.thf.pulse

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityGpsMotionGateTest {
    private fun confirms(
        mode: ActivityMode,
        displacementMetres: Double,
        points: Int = 3,
        durationMs: Long = 5_000L,
        worstAccuracyMetres: Double = 5.0,
    ) = ActivityGpsMotionGate.confirmsMovement(
        mode = mode,
        displacementMetres = displacementMetres,
        acceptedPointCount = points,
        durationMs = durationMs,
        worstAccuracyMetres = worstAccuracyMetres,
    )

    @Test
    fun rejectsStationaryDriftEvenWhenManyFixesSpanLongTime() {
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 4.0, points = 12, durationMs = 30_000L))
        assertFalse(confirms(ActivityMode.RUN, displacementMetres = 7.0, points = 12, durationMs = 30_000L))
    }

    @Test
    fun requiresMultipleAcceptedFixesAndARealTimeWindow() {
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, points = 2))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, durationMs = 4_999L))
        assertTrue(confirms(ActivityMode.WALK, displacementMetres = 12.5))
    }

    @Test
    fun displacementMustExceedReportedLocationUncertainty() {
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 12.49, worstAccuracyMetres = 5.0))
        assertTrue(confirms(ActivityMode.WALK, displacementMetres = 12.5, worstAccuracyMetres = 5.0))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 19.9, worstAccuracyMetres = 8.0))
        assertTrue(confirms(ActivityMode.WALK, displacementMetres = 20.0, worstAccuracyMetres = 8.0, durationMs = 6_000L))
    }

    @Test
    fun cyclingRequiresItsOwnConservativeDisplacementThreshold() {
        assertFalse(confirms(ActivityMode.CYCLE, displacementMetres = 17.99))
        assertTrue(confirms(ActivityMode.CYCLE, displacementMetres = 18.0))
    }

    @Test
    fun rejectsInvalidAccuracyDistancePointCountAndDuration() {
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = Double.NaN))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = Double.POSITIVE_INFINITY))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = -1.0))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, points = 0))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, durationMs = -1L))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, worstAccuracyMetres = 0.0))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, worstAccuracyMetres = Double.NaN))
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 20.0, worstAccuracyMetres = 26.0))
    }

    @Test
    fun rejectsDisplacementThatImpliesImpossibleSportSpeed() {
        assertFalse(confirms(ActivityMode.WALK, displacementMetres = 40.0))
        assertFalse(confirms(ActivityMode.RUN, displacementMetres = 100.0))
        assertFalse(confirms(ActivityMode.CYCLE, displacementMetres = 200.0))
    }
}
