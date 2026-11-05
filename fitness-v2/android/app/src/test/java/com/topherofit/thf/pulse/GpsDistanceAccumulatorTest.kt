package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertNotNull
import org.junit.Test

class GpsDistanceAccumulatorTest {
    private fun fix(
        metres: Double,
        seconds: Long,
        accuracy: Double = 2.0,
        source: String? = "fused",
        mock: Boolean = false,
    ) = GpsFix(
        latitude = latitudeForMeters(metres),
        longitude = 0.0,
        accuracyMetres = accuracy,
        elapsedMs = seconds * 1_000L,
        mock = mock,
        speedMps = null,
        sourceLabel = source,
    )

    @Test
    fun smallUncertainMovesAccumulateFromStableAnchorAndRequireConfirmation() {
        val accumulator = GpsDistanceAccumulator()
        assertNull(accumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(accumulator.offer(fix(metres = 3.0, seconds = 3)))
        assertNull(accumulator.offer(fix(metres = 6.0, seconds = 6)))
        assertNull(accumulator.offer(fix(metres = 8.0, seconds = 8)))

        val credit = accumulator.offer(fix(metres = 10.0, seconds = 10))
        assertNotNull(credit)
        assertEquals(10.0, credit!!.distanceMetres, 0.15)
        assertEquals(10_000L, credit.elapsedMs)
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
        val credit = accumulator.offer(afterCorner)
        assertNotNull(credit)
        assertEquals(13.0, credit!!.distanceMetres, 0.3)
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

        val credit = accumulator.offer(fix(metres = 40.0, seconds = 14, accuracy = 2.0))
        assertNotNull(credit)
        assertEquals(40.0, credit!!.distanceMetres, 0.3)
    }

    @Test
    fun providerChangeAndLongGapReanchorWithoutBridging() {
        val providerAccumulator = GpsDistanceAccumulator()
        assertNull(providerAccumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(providerAccumulator.offer(fix(metres = 20.0, seconds = 10, source = "gps")))
        assertNull(providerAccumulator.offer(fix(metres = 30.0, seconds = 20, source = "gps")))
        val afterProviderChange = providerAccumulator.offer(fix(metres = 40.0, seconds = 30, source = "gps"))
        assertNotNull(afterProviderChange)
        assertEquals(20.0, afterProviderChange!!.distanceMetres, 0.15)

        val gapAccumulator = GpsDistanceAccumulator()
        assertNull(gapAccumulator.offer(fix(metres = 0.0, seconds = 0)))
        assertNull(gapAccumulator.offer(fix(metres = 50.0, seconds = 121)))
        assertNull(gapAccumulator.offer(fix(metres = 60.0, seconds = 131)))
        val afterGap = gapAccumulator.offer(fix(metres = 70.0, seconds = 141))
        assertNotNull(afterGap)
        assertEquals(20.0, afterGap!!.distanceMetres, 0.15)
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

        val confirmedMovement = accumulator.offer(fix(metres = 20.0, seconds = 8, source = "gps"))
        assertNotNull(confirmedMovement)
        assertEquals(20.0, confirmedMovement!!.distanceMetres, 0.15)
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

    private fun latitudeForMeters(metres: Double): Double =
        Math.toDegrees(metres / 6_371_000.0)
}
