package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityEvidenceAnomalyPolicyTest {
    @Test
    fun creditsOnlyMovementBeyondBothFixesAccuracyRadii() {
        val assessment = ActivityEvidenceAnomalyPolicy.assessSegment(
            ActivityEvidenceSport.WALKING,
            fix(seconds = 0, latitude = 0.0, accuracy = 2.0),
            fix(seconds = 10, latitude = latitudeForMeters(20.0), accuracy = 2.0),
        )
        assertEquals(ActivityGpsSegmentDecision.CREDITABLE, assessment.decision)
        assertEquals(20.0, assessment.observedDistanceMeters!!, 0.2)
        assertEquals(16.0, assessment.creditableDistanceMeters, 0.2)
        assertEquals("fused", assessment.sourceLabel)
    }

    @Test
    fun excludesMockProviderEvidence() {
        val assessment = assess(
            fix(seconds = 0, latitude = 0.0),
            fix(seconds = 10, latitude = latitudeForMeters(30.0), mock = true),
        )
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_MOCK_LOCATION, assessment.decision)
        assertEquals(0.0, assessment.creditableDistanceMeters, 0.0)
    }

    @Test
    fun excludesMissingOrChangingSourceLabels() {
        val missing = assess(
            fix(seconds = 0, latitude = 0.0, source = " "),
            fix(seconds = 10, latitude = latitudeForMeters(30.0)),
        )
        val changed = assess(
            fix(seconds = 0, latitude = 0.0, source = "fused"),
            fix(seconds = 10, latitude = latitudeForMeters(30.0), source = "gps"),
        )
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_MISSING_SOURCE, missing.decision)
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_SOURCE_CHANGE, changed.decision)
    }

    @Test
    fun excludesInvalidCoordinatesAndAccuracy() {
        val invalid = assess(
            fix(seconds = 0, latitude = 0.0),
            fix(seconds = 10, latitude = 91.0),
        )
        val inaccurate = assess(
            fix(seconds = 0, latitude = 0.0),
            fix(seconds = 10, latitude = latitudeForMeters(30.0), accuracy = 51.0),
        )
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_INVALID_COORDINATES, invalid.decision)
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_POOR_ACCURACY, inaccurate.decision)
    }

    @Test
    fun excludesNonMonotonicElapsedRealtime() {
        val assessment = assess(
            fix(seconds = 10, latitude = 0.0),
            fix(seconds = 10, latitude = latitudeForMeters(30.0)),
        )
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_NON_MONOTONIC_TIME, assessment.decision)
    }

    @Test
    fun excludesLongGapsInsteadOfCreditingUnobservedTravel() {
        val assessment = assess(
            fix(seconds = 0, latitude = 0.0),
            fix(seconds = 121, latitude = latitudeForMeters(500.0)),
        )
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_LONG_GAP, assessment.decision)
        assertEquals(0.0, assessment.creditableDistanceMeters, 0.0)
    }

    @Test
    fun doesNotCreditStationaryGpsJitterInsideAccuracyBounds() {
        val assessment = assess(
            fix(seconds = 0, latitude = 0.0, accuracy = 3.0),
            fix(seconds = 10, latitude = latitudeForMeters(5.0), accuracy = 3.0),
        )
        assertEquals(ActivityGpsSegmentDecision.NO_MEASURABLE_MOVEMENT, assessment.decision)
        assertEquals(0.0, assessment.creditableDistanceMeters, 0.0)
    }

    @Test
    fun rejectsImpossibleWalkingJumpButAllowsSameSegmentForCycling() {
        val previous = fix(seconds = 0, latitude = 0.0, accuracy = 2.0)
        val current = fix(seconds = 2, latitude = latitudeForMeters(90.0), accuracy = 2.0)
        val walking = assess(previous, current, ActivityEvidenceSport.WALKING)
        val cycling = assess(previous, current, ActivityEvidenceSport.CYCLING)
        assertEquals(ActivityGpsSegmentDecision.EXCLUDE_IMPLAUSIBLE_SPEED, walking.decision)
        assertEquals(ActivityGpsSegmentDecision.CREDITABLE, cycling.decision)
        assertTrue(cycling.conservativeSpeedMetersPerSecond!! < 45.0)
    }

    @Test
    fun rejectsImplausibleRunSpeedWithoutRejectingCyclingSpeed() {
        val previous = fix(seconds = 0, latitude = 0.0, accuracy = 2.0)
        val current = fix(seconds = 10, latitude = latitudeForMeters(200.0), accuracy = 2.0)
        assertEquals(
            ActivityGpsSegmentDecision.EXCLUDE_IMPLAUSIBLE_SPEED,
            assess(previous, current, ActivityEvidenceSport.RUNNING).decision,
        )
        assertEquals(
            ActivityGpsSegmentDecision.CREDITABLE,
            assess(previous, current, ActivityEvidenceSport.CYCLING).decision,
        )
    }

    @Test
    fun handlesLongitudeWrapAtDateLine() {
        val assessment = assess(
            fix(seconds = 0, latitude = 0.0, longitude = 179.999, accuracy = 5.0),
            fix(seconds = 60, latitude = 0.0, longitude = -179.999, accuracy = 5.0),
        )
        assertEquals(ActivityGpsSegmentDecision.CREDITABLE, assessment.decision)
        assertTrue(assessment.observedDistanceMeters!! < 300.0)
    }

    @Test
    fun normalizesProviderLabelCaseAndWhitespaceButDoesNotAuthenticateIt() {
        val assessment = assess(
            fix(seconds = 0, latitude = 0.0, source = " Fused "),
            fix(seconds = 10, latitude = latitudeForMeters(30.0), source = "fused"),
        )
        assertEquals(ActivityGpsSegmentDecision.CREDITABLE, assessment.decision)
        assertFalse(assessment.sourceLabel!!.isBlank())
    }

    private fun assess(
        previous: ActivityGpsFix,
        current: ActivityGpsFix,
        sport: ActivityEvidenceSport = ActivityEvidenceSport.WALKING,
    ) = ActivityEvidenceAnomalyPolicy.assessSegment(sport, previous, current)

    private fun fix(
        seconds: Long,
        latitude: Double,
        longitude: Double = 0.0,
        accuracy: Double = 3.0,
        source: String? = "fused",
        mock: Boolean = false,
    ) = ActivityGpsFix(
        elapsedRealtimeNanos = seconds * 1_000_000_000L,
        latitude = latitude,
        longitude = longitude,
        horizontalAccuracyMeters = accuracy,
        sourceLabel = source,
        mockLocation = mock,
    )

    private fun latitudeForMeters(meters: Double): Double = Math.toDegrees(meters / 6_371_000.0)
}
