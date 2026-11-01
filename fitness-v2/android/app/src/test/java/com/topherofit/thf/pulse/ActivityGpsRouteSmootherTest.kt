package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityGpsRouteSmootherTest {
    private fun point(
        seconds: Long,
        northMetres: Double,
        eastMetres: Double = 0.0,
        accuracyMetres: Float = 2f,
        altitudeMetres: Double? = null,
    ) = ActivityRoutePoint(
        latitude = 30.0 + northMetres / 111_000.0,
        longitude = 31.0 + eastMetres / (111_000.0 * kotlin.math.cos(Math.toRadians(30.0))),
        altitudeMetres = altitudeMetres,
        accuracyMetres = accuracyMetres,
        elapsedMs = seconds * 1_000L,
    )

    @Test fun preservesEndpointsAndAllNonCoordinateEvidence() {
        val points = listOf(
            point(0, 0.0, altitudeMetres = 11.0),
            point(5, 10.0, eastMetres = 4.0, accuracyMetres = 4f, altitudeMetres = 12.0),
            point(10, 20.0, altitudeMetres = 13.0),
        )

        val smoothed = ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.WALK)

        assertEquals(points.first(), smoothed.first())
        assertEquals(points.last(), smoothed.last())
        assertEquals(points[1].elapsedMs, smoothed[1].elapsedMs)
        assertEquals(points[1].accuracyMetres, smoothed[1].accuracyMetres)
        assertEquals(points[1].altitudeMetres, smoothed[1].altitudeMetres)
    }

    @Test fun smoothsSmallLateralJitterWithinTheBoundedShift() {
        val points = listOf(
            point(0, 0.0),
            point(5, 10.0, eastMetres = 4.0, accuracyMetres = 4f),
            point(10, 20.0),
        )

        val smoothed = ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.WALK)
        val shift = ActivityMetrics.distanceMetres(
            points[1].latitude, points[1].longitude,
            smoothed[1].latitude, smoothed[1].longitude,
        )

        assertTrue("expected a bounded display correction", shift > 0.1)
        assertTrue("display correction must not exceed 2 m for a 4 m accuracy fix", shift <= 2.0)
    }

    @Test fun leavesStraightTrackUnchanged() {
        val points = listOf(point(0, 0.0), point(5, 10.0), point(10, 20.0))
        assertEquals(points, ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.RUN))
    }

    @Test fun leavesSharpTurnUnchangedInsteadOfCuttingTheCorner() {
        val points = listOf(
            point(0, 0.0, eastMetres = 0.0),
            point(5, 10.0, eastMetres = 0.0),
            point(10, 10.0, eastMetres = 10.0),
        )
        assertEquals(points, ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.WALK))
    }

    @Test fun doesNotSmoothAcrossAStaleOrLargeTimeGap() {
        val points = listOf(point(0, 0.0), point(5, 10.0, eastMetres = 4.0, accuracyMetres = 4f), point(20, 20.0))
        assertEquals(points, ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.WALK))
    }

    @Test fun doesNotSmoothPoorAccuracyFixesForTheSelectedSport() {
        val points = listOf(
            point(0, 0.0),
            point(5, 10.0, eastMetres = 4.0, accuracyMetres = 26f),
            point(10, 20.0),
        )
        assertEquals(points, ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.WALK))
        assertEquals(points, ActivityGpsRouteSmoother.smoothForDisplay(points, ActivityMode.RUN))
    }

    @Test fun keepsShortRoutesUnchanged() {
        val one = listOf(point(0, 0.0))
        val two = listOf(point(0, 0.0), point(5, 10.0, eastMetres = 4.0, accuracyMetres = 4f))
        assertEquals(one, ActivityGpsRouteSmoother.smoothForDisplay(one, ActivityMode.WALK))
        assertEquals(two, ActivityGpsRouteSmoother.smoothForDisplay(two, ActivityMode.WALK))
    }
}
