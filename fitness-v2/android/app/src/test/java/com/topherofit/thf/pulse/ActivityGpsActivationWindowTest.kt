package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityGpsActivationWindowTest {
    private fun point(seconds: Long, northMetres: Double, accuracyMetres: Float = 2f) =
        ActivityRoutePoint(
            latitude = 30.0 + northMetres / 111_000.0,
            longitude = 31.0,
            altitudeMetres = null,
            accuracyMetres = accuracyMetres,
            elapsedMs = seconds * 1_000L,
        )

    @Test
    fun selectsRecentMotionWindowAfterStationaryWarmup() {
        val points = listOf(
            point(0, 0.0),
            point(10, 1.2),
            point(20, 2.4),
            point(25, 5.0),
            point(30, 10.0),
            point(35, 16.0),
        )

        val window = requireNotNull(ActivityGpsActivationWindowPolicy.select(points, ActivityMode.WALK))

        assertEquals(25_000L, window.firstPoint.elapsedMs)
        assertEquals(35_000L, window.lastPoint.elapsedMs)
        assertEquals(3, window.pointCount)
        assertTrue(window.displacementMetres in 10.5..11.5)
        assertEquals(10_000L, window.durationMs)
    }

    @Test
    fun stationaryDriftNeverCreatesAQualifyingWindow() {
        val points = listOf(
            point(0, 0.0),
            point(10, 1.2),
            point(20, 2.4),
            point(30, 3.6),
            point(40, 4.8),
        )

        assertNull(ActivityGpsActivationWindowPolicy.select(points, ActivityMode.WALK))
    }

    @Test
    fun worstAccuracyAnywhereInsideWindowControlsActivation() {
        val points = listOf(
            point(0, 0.0, 2f),
            point(5, 10.0, 10f),
            point(10, 20.0, 2f),
        )

        assertNull(ActivityGpsActivationWindowPolicy.select(points, ActivityMode.WALK))
    }

    @Test
    fun rejectsNonMonotonicOrInvalidRouteEvidence() {
        val outOfOrder = listOf(point(0, 0.0), point(10, 10.0), point(5, 20.0))
        val invalidAccuracy = listOf(point(0, 0.0), point(5, 10.0, Float.NaN), point(10, 20.0))

        assertNull(ActivityGpsActivationWindowPolicy.select(outOfOrder, ActivityMode.WALK))
        assertNull(ActivityGpsActivationWindowPolicy.select(invalidAccuracy, ActivityMode.WALK))
    }
}
