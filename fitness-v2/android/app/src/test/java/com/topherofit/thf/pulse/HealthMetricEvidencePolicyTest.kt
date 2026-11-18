package com.topherofit.thf.pulse

import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class HealthMetricEvidencePolicyTest {
    private val start = Instant.parse("2026-11-18T10:00:00Z")

    private fun end(seconds: Long) = start.plusSeconds(seconds)

    @Test
    fun plausibleStepsRateIsAccepted() {
        assertNull(
            HealthMetricEvidencePolicy.assessSteps(
                count = 9_000L,
                start = start,
                end = end(1_800L),
                observedAt = end(1_800L),
            ),
        )
    }

    @Test
    fun genuineZeroStepsRemainAValidZero() {
        assertNull(
            HealthMetricEvidencePolicy.assessSteps(
                count = 0L,
                start = start,
                end = end(3_600L),
                observedAt = end(3_600L),
            ),
        )
    }

    @Test
    fun negativeStepsAreRejected() {
        assertEquals(
            "NEGATIVE_STEPS",
            HealthMetricEvidencePolicy.assessSteps(-1L, start, end(60L), end(60L)),
        )
    }

    @Test
    fun implausibleStepBurstIsRejected() {
        assertEquals(
            "IMPLAUSIBLE_STEPS_RATE",
            HealthMetricEvidencePolicy.assessSteps(601L, start, end(100L), end(100L)),
        )
    }

    @Test
    fun futureDatedStepsAreRejected() {
        assertEquals(
            "FUTURE_METRIC_RECORD",
            HealthMetricEvidencePolicy.assessSteps(100L, start, end(60L), end(59L)),
        )
    }

    @Test
    fun invalidMetricIntervalIsRejected() {
        assertEquals(
            "INVALID_METRIC_INTERVAL",
            HealthMetricEvidencePolicy.assessSteps(100L, end(60L), start, end(120L)),
        )
    }

    @Test
    fun plausibleDistanceRateIsAccepted() {
        assertNull(
            HealthMetricEvidencePolicy.assessDistance(
                meters = 18_000.0,
                start = start,
                end = end(3_600L),
                observedAt = end(3_600L),
            ),
        )
    }

    @Test
    fun negativeAndNonFiniteDistanceAreRejected() {
        assertEquals(
            "INVALID_DISTANCE_VALUE",
            HealthMetricEvidencePolicy.assessDistance(-0.1, start, end(60L), end(60L)),
        )
        assertEquals(
            "INVALID_DISTANCE_VALUE",
            HealthMetricEvidencePolicy.assessDistance(Double.NaN, start, end(60L), end(60L)),
        )
        assertEquals(
            "INVALID_DISTANCE_VALUE",
            HealthMetricEvidencePolicy.assessDistance(Double.POSITIVE_INFINITY, start, end(60L), end(60L)),
        )
    }

    @Test
    fun implausibleDistanceRateIsRejected() {
        assertEquals(
            "IMPLAUSIBLE_DISTANCE_RATE",
            HealthMetricEvidencePolicy.assessDistance(501.0, start, end(10L), end(10L)),
        )
    }

    @Test
    fun futureDatedDistanceIsRejected() {
        assertEquals(
            "FUTURE_METRIC_RECORD",
            HealthMetricEvidencePolicy.assessDistance(100.0, start, end(60L), end(59L)),
        )
    }

    @Test
    fun plausibleActiveCaloriesRateIsAccepted() {
        assertNull(
            HealthMetricEvidencePolicy.assessActiveCalories(
                kilocalories = 1_800.0,
                start = start,
                end = end(3_600L),
                observedAt = end(3_600L),
            ),
        )
    }

    @Test
    fun negativeAndNonFiniteActiveCaloriesAreRejected() {
        assertEquals(
            "INVALID_ACTIVE_CALORIES_VALUE",
            HealthMetricEvidencePolicy.assessActiveCalories(-1.0, start, end(60L), end(60L)),
        )
        assertEquals(
            "INVALID_ACTIVE_CALORIES_VALUE",
            HealthMetricEvidencePolicy.assessActiveCalories(Double.NaN, start, end(60L), end(60L)),
        )
        assertEquals(
            "INVALID_ACTIVE_CALORIES_VALUE",
            HealthMetricEvidencePolicy.assessActiveCalories(Double.POSITIVE_INFINITY, start, end(60L), end(60L)),
        )
    }

    @Test
    fun implausibleActiveCaloriesRateIsRejected() {
        assertEquals(
            "IMPLAUSIBLE_ACTIVE_CALORIES_RATE",
            HealthMetricEvidencePolicy.assessActiveCalories(101.0, start, end(60L), end(60L)),
        )
    }

    @Test
    fun futureDatedActiveCaloriesAreRejected() {
        assertEquals(
            "FUTURE_METRIC_RECORD",
            HealthMetricEvidencePolicy.assessActiveCalories(100.0, start, end(60L), end(59L)),
        )
    }
}
