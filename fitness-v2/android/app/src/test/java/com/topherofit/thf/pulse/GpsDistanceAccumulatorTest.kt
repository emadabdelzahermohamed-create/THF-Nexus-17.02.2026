package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class GpsDistanceAccumulatorTest {
    private fun fix(
        metres: Double,
        seconds: Long,
        accuracy: Double = 2.0,
        source: String? = "fused",
        mock: Boolean = false,
        speedMps: Double? = null,
        speedAccuracyMps: Double? = null,
    ) = GpsFix(
        latitude = latitudeForMeters(metres),
        longitude = 0.0,
        accuracyMetres = accuracy,
        elapsedMs = seconds * 1_000L,
        mock = mock,
        speedMps = speedMps,
        sourceLabel = source,
        speedAccuracyMps = speedAccuracyMps,
    )

    @Test
    fun smallUncertainMovesAccumulateFromStableAnchorAndRequireConfirmation() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(accumulator.offer(fix(metres = 3.0, seconds = 3)))
        assertNull(accumulator.offer(fix(metres = 6.0, seconds = 6)))
        assertNull(accumulator.offer(fix(metres = 8.0, seconds = 8)))
        assertNull(accumulator.offer(fix(metres = 10.0, seconds = 10)))
        assertNull(accumulator.offer(fix(metres = 12.0, seconds = 12)))

        val credit = accumulator.offer(fix(metres = 16.0, seconds = 16))
        assertNotNull(credit)
        assertEquals(16.0, credit!!.distanceMetres, 0.15)
        assertEquals(16_000L, credit.elapsedMs)
    }

    @Test
    fun preservesAcceptedPathLengthWhenMovementTurns() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(accumulator.offer(fix(metres = 5.0, seconds = 2)))

        val corner = GpsFix(
            latitude = latitudeForMeters(5.0),
            longitude = Math.toDegrees(5.0 / 6_371_000.0),
            accuracyMetres = 2.0,
            elapsedMs = 4_000L,
            mock = false,
            speedMps = null,
            sourceLabel = "fused",
        )
        assertNull(accumulator.offer(corner))

        val afterCorner = GpsFix(
            latitude = latitudeForMeters(8.0),
            longitude = Math.toDegrees(5.0 / 6_371_000.0),
            accuracyMetres = 2.0,
            elapsedMs = 6_000L,
            mock = false,
            speedMps = null,
            sourceLabel = "fused",
        )
        assertNull(accumulator.offer(afterCorner))
        val afterCorner2 = GpsFix(
            latitude = latitudeForMeters(10.0),
            longitude = Math.toDegrees(5.0 / 6_371_000.0),
            accuracyMetres = 2.0,
            elapsedMs = 7_000L,
            mock = false,
            speedMps = null,
            sourceLabel = "fused",
        )
        assertNull(accumulator.offer(afterCorner2))
        val afterCorner3 = GpsFix(
            latitude = latitudeForMeters(12.0),
            longitude = Math.toDegrees(5.0 / 6_371_000.0),
            accuracyMetres = 2.0,
            elapsedMs = 9_000L,
            mock = false,
            speedMps = null,
            sourceLabel = "fused",
        )
        assertNull(accumulator.offer(afterCorner3))
        val afterCorner4 = GpsFix(
            latitude = latitudeForMeters(14.0),
            longitude = Math.toDegrees(5.0 / 6_371_000.0),
            accuracyMetres = 2.0,
            elapsedMs = 11_000L,
            mock = false,
            speedMps = null,
            sourceLabel = "fused",
        )
        val credit = accumulator.offer(afterCorner4)
        assertNotNull(credit)
        assertEquals(19.0, credit!!.distanceMetres, 0.3)
    }

    @Test
    fun stationaryJitterInsideAccuracyRadiiDoesNotAccumulate() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0, accuracy = 3.0)))
        assertNull(accumulator.offer(fix(metres = 3.0, seconds = 5, accuracy = 3.0)))
        assertNull(accumulator.offer(fix(metres = -2.0, seconds = 10, accuracy = 3.0)))
        assertNull(accumulator.offer(fix(metres = 4.0, seconds = 15, accuracy = 3.0)))
        assertNull(accumulator.offer(fix(metres = 8.0, seconds = 20, accuracy = 3.0)))
    }

    @Test
    fun poorIntermediateAccuracyRemainsInTheMovementDeadband() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0, accuracy = 2.0)))
        assertNull(accumulator.offer(fix(metres = 5.0, seconds = 2, accuracy = 20.0)))
        assertNull(accumulator.offer(fix(metres = 10.0, seconds = 4, accuracy = 2.0)))
        assertNull(accumulator.offer(fix(metres = 30.0, seconds = 10, accuracy = 2.0)))
        assertNull(accumulator.offer(fix(metres = 40.0, seconds = 14, accuracy = 2.0)))

        val credit = accumulator.offer(fix(metres = 50.0, seconds = 18, accuracy = 2.0))
        assertNotNull(credit)
        assertEquals(50.0, credit!!.distanceMetres, 0.3)
    }

    @Test
    fun providerChangeAndLongGapReanchorWithoutBridging() {
        val providerAccumulator = GpsDistanceAccumulator()
        assertNull(providerAccumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(providerAccumulator.offer(fix(metres = 20.0, seconds = 10, source = "gps")))
        assertNull(providerAccumulator.offer(fix(metres = 30.0, seconds = 20, source = "gps")))
        assertNull(providerAccumulator.offer(fix(metres = 40.0, seconds = 30, source = "gps")))
        val afterProviderChange = providerAccumulator.offer(fix(metres = 50.0, seconds = 40, source = "gps"))
        assertNotNull(afterProviderChange)
        assertEquals(30.0, afterProviderChange!!.distanceMetres, 0.15)

        val gapAccumulator = GpsDistanceAccumulator()
        assertNull(gapAccumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(gapAccumulator.offer(fix(metres = 50.0, seconds = 121)))
        assertNull(gapAccumulator.offer(fix(metres = 60.0, seconds = 131)))
        assertNull(gapAccumulator.offer(fix(metres = 70.0, seconds = 141)))
        val afterGap = gapAccumulator.offer(fix(metres = 80.0, seconds = 151))
        assertNotNull(afterGap)
        assertEquals(30.0, afterGap!!.distanceMetres, 0.15)
    }

    @Test
    fun gapBeyondFreshFixWindowReanchorsWithoutBridgingStaleDistance() {
        assertEquals(GpsFixGate.MAX_FIX_AGE_MS, GpsDistanceAccumulator.MAX_FIX_GAP_MS)
        assertEquals(120_000L, GpsDistanceAccumulator.MAX_ANCHOR_GAP_MS)
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        // A 31-second gap exceeds the shared 30-second freshness contract. The new point
        // starts a fresh measurement window; the 100 m gap must never enter credited distance.
        assertNull(accumulator.offer(fix(metres = 100.0, seconds = 31)))
        assertNull(accumulator.offer(fix(metres = 110.0, seconds = 36)))
        assertNull(accumulator.offer(fix(metres = 120.0, seconds = 41)))
        val credit = accumulator.offer(fix(metres = 130.0, seconds = 46))

        assertNotNull(credit)
        assertEquals(30.0, credit!!.distanceMetres, 0.2)
        assertEquals(15_000L, credit.elapsedMs)
    }

    @Test
    fun slowContinuousMovementCanAccumulateAcrossFreshFixesBeyondThirtySeconds() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        for (seconds in 1L..8L) {
            assertNull(accumulator.offer(fix(metres = seconds.toDouble(), seconds = seconds * 5L)))
        }
        val credit = accumulator.offer(fix(metres = 9.0, seconds = 45))

        assertNotNull(credit)
        assertEquals(9.0, credit!!.distanceMetres, 0.2)
        assertEquals(45_000L, credit.elapsedMs)
    }

    @Test
    fun oneFixExcursionThatReturnsIsDiscardedBeforeLaterMovement() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0, source = "gps")))
        // A 20 m / 2 s excursion is below the cycling speed ceiling, but one fix is not enough
        // to credit it. Returning to the anchor must discard the excursion's pending path.
        assertNull(accumulator.offer(fix(metres = 20.0, seconds = 2, source = "gps")))
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 4, source = "gps")))
        assertNull(accumulator.offer(fix(metres = 10.0, seconds = 6, source = "gps")))
        assertNull(accumulator.offer(fix(metres = 20.0, seconds = 8, source = "gps")))

        val confirmedMovement = accumulator.offer(fix(metres = 30.0, seconds = 14, source = "gps"))
        assertNotNull(confirmedMovement)
        assertEquals(30.0, confirmedMovement!!.distanceMetres, 0.15)
    }

    @Test
    fun twoFixStationaryDriftBurstIsDiscardedWhenItReturnsInsideDeadband() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0, source = "gps")))
        assertNull(accumulator.offer(fix(metres = 10.0, seconds = 5, source = "gps")))
        assertNull(accumulator.offer(fix(metres = 12.0, seconds = 7, source = "gps")))
        // A second above-deadband fix is still provisional. Returning to the anchor before
        // three fixes / six seconds discards the entire excursion.
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 9, source = "gps")))
    }

    @Test
    fun resetAndMockFixNeverBridgeOldAnchor() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        accumulator.reset()
        assertNull(accumulator.offer(fix(metres = 20.0, seconds = 10)))
        assertNull(accumulator.offer(fix(metres = 30.0, seconds = 20, mock = true)))
        assertNull(accumulator.offer(fix(metres = 40.0, seconds = 30)))
    }

    @Test
    fun dateLineDistanceUsesShortestLongitudeArc() {
        val distance = ActivityMetrics.distanceMetres(0.0, 179.999, 0.0, -179.999)
        assertEquals(222.39, distance, 1.0)
    }


    @Test
    fun oscillatingAcceptedFixesCannotInflateCreditedPathBeyondNetDisplacementEnvelope() {
        val accumulator = GpsDistanceAccumulator()
        var previous: GpsFix? = null
        var credit: GpsDistanceCredit? = null
        val positionsMetres = listOf(0.0, 4.0, 0.0, 4.0, 0.0, 4.0, 0.0, 8.0, 12.0, 16.0)

        positionsMetres.forEachIndexed { index, metres ->
            val current = fix(metres = metres, seconds = index * 5L)
            assertTrue(
                GpsFixGate.accepts(
                    current,
                    previous,
                    ActivityMode.CYCLE,
                    sessionStartedMs = 0L,
                    nowMs = current.elapsedMs,
                ),
            )
            credit = accumulator.offer(current) ?: credit
            previous = current
        }

        assertNotNull(credit)
        val netDisplacement = ActivityMetrics.distanceMetres(
            latitudeForMeters(0.0),
            0.0,
            latitudeForMeters(16.0),
            0.0,
        )
        assertEquals(
            netDisplacement * GpsDistanceAccumulator.MAX_PATH_TO_NET_RATIO,
            credit!!.distanceMetres,
            0.2,
        )
    }


    @Test
    fun repeatedConfidentStationarySpeedFixesReanchorAndDiscardSlowGpsDrift() {
        val accumulator = GpsDistanceAccumulator()
        fun stationary(metres: Double, seconds: Long) = fix(
            metres = metres,
            seconds = seconds,
            accuracy = 2.0,
            speedMps = 0.05,
            speedAccuracyMps = 0.10,
        )

        assertNull(accumulator.offer(stationary(0.0, 0)))
        assertNull(accumulator.offer(stationary(5.0, 5)))
        // Two low-speed observations spanning five seconds confirm a stationary window.
        assertNull(accumulator.offer(stationary(10.0, 10)))
        assertNull(accumulator.offer(stationary(15.0, 15)))
        assertNull(accumulator.offer(stationary(20.0, 20)))
    }

    @Test
    fun aSingleStationarySpeedObservationDoesNotSuppressMovementThatResumes() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(
            accumulator.offer(
                fix(metres = 0.5, seconds = 3, speedMps = 0.05, speedAccuracyMps = 0.10),
            ),
        )
        assertNull(
            accumulator.offer(
                fix(metres = 5.0, seconds = 5, speedMps = 1.2, speedAccuracyMps = 0.2),
            ),
        )
        assertNull(accumulator.offer(fix(metres = 9.0, seconds = 8, speedMps = 1.2, speedAccuracyMps = 0.2)))
        assertNull(accumulator.offer(fix(metres = 13.0, seconds = 11, speedMps = 1.2, speedAccuracyMps = 0.2)))
        val credit = accumulator.offer(fix(metres = 17.0, seconds = 14, speedMps = 1.2, speedAccuracyMps = 0.2))

        assertNotNull(credit)
        assertEquals(16.5, credit!!.distanceMetres, 0.2)
    }

    @Test
    fun lowReportedSpeedWithoutSpeedAccuracyIsNotTreatedAsStationaryEvidence() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0, speedMps = 0.05)))
        assertNull(accumulator.offer(fix(metres = 5.0, seconds = 5, speedMps = 0.05)))
        assertNull(accumulator.offer(fix(metres = 10.0, seconds = 10, speedMps = 0.05)))
        assertNull(accumulator.offer(fix(metres = 15.0, seconds = 15, speedMps = 0.05)))
        val credit = accumulator.offer(fix(metres = 20.0, seconds = 20, speedMps = 0.05))

        assertNotNull(credit)
        assertEquals(20.0, credit!!.distanceMetres, 0.2)
    }

    private fun latitudeForMeters(metres: Double): Double =
        Math.toDegrees(metres / 6_371_000.0)
}
