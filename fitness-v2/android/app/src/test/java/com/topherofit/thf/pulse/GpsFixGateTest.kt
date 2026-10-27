package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class GpsFixGateTest {
    private val first = GpsFix(30.0, 31.0, 5.0, 100_000L, false, null)
    private fun accepts(fix: GpsFix, previous: GpsFix? = null, mode: ActivityMode = ActivityMode.WALK) =
        GpsFixGate.accepts(fix, previous, mode, 90_000L, 110_000L)

    @Test fun acceptsFreshRealFix() { assertTrue(accepts(first)) }
    @Test fun rejectsMockEvenAsFirstPoint() { assertFalse(accepts(first.copy(mock = true))) }
    @Test fun rejectsMissingOrNonFiniteAccuracy() {
        for (accuracy in listOf(0.0, -1.0, Double.NaN, Double.POSITIVE_INFINITY, 81.0))
            assertFalse(accepts(first.copy(accuracyMetres = accuracy)))
    }
    @Test fun rejectsGpsAccuracyTooPoorForActivityMode() {
        assertFalse(accepts(first.copy(accuracyMetres = 26.0), mode = ActivityMode.WALK))
        assertFalse(accepts(first.copy(accuracyMetres = 26.0), mode = ActivityMode.RUN))
        assertTrue(accepts(first.copy(accuracyMetres = 26.0), mode = ActivityMode.CYCLE))
        assertFalse(accepts(first.copy(accuracyMetres = 41.0), mode = ActivityMode.CYCLE))
    }
    @Test fun rejectsInvalidCoordinates() {
        assertFalse(accepts(first.copy(latitude = Double.NaN)))
        assertFalse(accepts(first.copy(latitude = 91.0)))
        assertFalse(accepts(first.copy(longitude = -181.0)))
    }
    @Test fun rejectsStaleFutureAndPreSessionFixes() {
        assertFalse(accepts(first.copy(elapsedMs = 80_000L)))
        assertFalse(accepts(first.copy(elapsedMs = 110_001L)))
        assertFalse(GpsFixGate.accepts(first, null, ActivityMode.WALK, 90_000L, 140_001L))
    }
    @Test fun rejectsOutOfOrderAndDuplicateTime() {
        assertFalse(accepts(first, first))
        assertFalse(accepts(first.copy(elapsedMs = 99_999L), first))
    }
    @Test fun rejectsTeleportWithoutPoisoningNextGoodFix() {
        assertFalse(accepts(first.copy(latitude = 31.0, elapsedMs = 101_000L), first))
        assertTrue(accepts(first.copy(latitude = 30.00003, elapsedMs = 103_000L), first))
    }

    @Test fun rejectsStationaryGpsDriftWithoutAdvancingTheAcceptedAnchor() {
        assertFalse(accepts(first.copy(latitude = 30.000005, elapsedMs = 101_000L), first))
        assertTrue(accepts(first.copy(latitude = 30.00003, elapsedMs = 103_000L), first))
    }
    @Test fun appliesDifferentSportSpeedLimits() {
        val moving = first.copy(latitude = 30.0001, elapsedMs = 102_000L)
        assertFalse(accepts(moving, first, ActivityMode.WALK))
        assertTrue(accepts(moving, first, ActivityMode.RUN))
        assertTrue(accepts(moving, first, ActivityMode.CYCLE))
    }
    @Test fun rejectsInvalidReportedSpeed() {
        for (speed in listOf(-1.0, Double.NaN, Double.POSITIVE_INFINITY, 50.0))
            assertFalse(accepts(first.copy(speedMps = speed)))
    }
}
