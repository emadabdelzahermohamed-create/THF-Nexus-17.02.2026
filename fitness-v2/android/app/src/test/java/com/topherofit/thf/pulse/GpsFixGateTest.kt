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

    @Test fun deadbandUsesWorseAccuracyFromEitherEndpoint() {
        val poorAccuracyAnchor = first.copy(accuracyMetres = 25.0)
        val smallApparentMove = first.copy(
            latitude = 30.00003,
            accuracyMetres = 5.0,
            elapsedMs = 103_000L,
        )
        assertFalse(
            GpsFixGate.accepts(
                smallApparentMove, poorAccuracyAnchor, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )

        val displacementBeyondDeadband = first.copy(
            latitude = 30.00008,
            accuracyMetres = 5.0,
            elapsedMs = 105_000L,
        )
        assertTrue(
            GpsFixGate.accepts(
                displacementBeyondDeadband, poorAccuracyAnchor, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
    }

    @Test
    fun fusedSourceTransitionRejectsImpossibleCrossProviderJumpsButAllowsStationaryPromotion() {
        val frameworkFix = first.copy(elapsedMs = 100_000L, sourceLabel = "network")
        val stationaryFusedFix = frameworkFix.copy(
            accuracyMetres = 3.0,
            elapsedMs = 101_000L,
            sourceLabel = "fused",
        )
        val plausibleFusedFix = frameworkFix.copy(
            latitude = 30.00003,
            accuracyMetres = 3.0,
            elapsedMs = 103_000L,
            sourceLabel = "fused",
        )
        val teleportingFusedFix = frameworkFix.copy(
            latitude = 31.0,
            accuracyMetres = 3.0,
            elapsedMs = 101_000L,
            sourceLabel = "fused",
        )

        assertTrue(
            GpsFixGate.acceptsSourceTransition(
                stationaryFusedFix, frameworkFix, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
        assertTrue(
            GpsFixGate.acceptsSourceTransition(
                plausibleFusedFix, frameworkFix, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
        assertFalse(
            GpsFixGate.acceptsSourceTransition(
                teleportingFusedFix, frameworkFix, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
    }

    @Test
    fun fusedSourceTransitionRejectsDuplicateTimeButIgnoresAStaleHandoffAnchor() {
        val frameworkFix = first.copy(elapsedMs = 100_000L, sourceLabel = "network")
        val duplicateTimeFusedFix = frameworkFix.copy(sourceLabel = "fused")
        val staleFrameworkFix = frameworkFix.copy(elapsedMs = 70_000L)
        val freshFusedFix = first.copy(
            latitude = 30.00003,
            accuracyMetres = 3.0,
            elapsedMs = 103_000L,
            sourceLabel = "fused",
        )

        assertFalse(
            GpsFixGate.acceptsSourceTransition(
                duplicateTimeFusedFix, frameworkFix, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
        assertTrue(
            GpsFixGate.acceptsSourceTransition(
                freshFusedFix, staleFrameworkFix, ActivityMode.WALK, 90_000L, 110_000L,
            ),
        )
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
    @Test
    fun fixFreshnessWindowIncludesThirtySecondBoundaryAndRejectsInvalidTimes() {
        assertTrue(GpsFixGate.isFreshElapsedTime(80_000L, 110_000L))
        assertFalse(GpsFixGate.isFreshElapsedTime(79_999L, 110_000L))
        assertFalse(GpsFixGate.isFreshElapsedTime(110_001L, 110_000L))
        assertFalse(GpsFixGate.isFreshElapsedTime(-1L, 110_000L))
    }

    @Test
    fun staleCheckpointAnchorDoesNotRejectFirstFreshPostRestoreFix() {
        val staleCheckpoint = first.copy(latitude = 31.0, elapsedMs = 50_000L, sourceLabel = "thf_checkpoint")
        val firstAfterRestore = first.copy(latitude = 30.00003, elapsedMs = 103_000L, sourceLabel = "fused")

        assertFalse(GpsFixGate.isFreshElapsedTime(staleCheckpoint.elapsedMs, 110_000L))
        assertTrue(GpsFixGate.accepts(firstAfterRestore, staleCheckpoint, ActivityMode.WALK, 40_000L, 110_000L))
    }

    @Test
    fun freshCheckpointAnchorStillEnforcesTheSportSpeedGate() {
        val freshCheckpoint = first.copy(elapsedMs = 100_000L, sourceLabel = "thf_checkpoint")
        val jump = first.copy(latitude = 31.0, elapsedMs = 101_000L, sourceLabel = "fused")

        assertTrue(GpsFixGate.isFreshElapsedTime(freshCheckpoint.elapsedMs, 110_000L))
        assertFalse(GpsFixGate.accepts(jump, freshCheckpoint, ActivityMode.WALK, 90_000L, 110_000L))
    }

}
