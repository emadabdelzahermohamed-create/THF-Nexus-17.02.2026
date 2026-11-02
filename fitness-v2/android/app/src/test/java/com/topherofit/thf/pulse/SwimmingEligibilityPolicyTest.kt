package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SwimmingEligibilityPolicyTest {
    private fun evidence(
        sport: SportKind = SportKind.SWIMMING_POOL,
        origin: EvidenceOrigin = EvidenceOrigin.HEALTH_WEARABLE,
        source: String? = "com.example.health",
        device: String? = "watch",
        recordId: String? = "health-record-1",
        kind: SwimmingRecordKind = SwimmingRecordKind.EXERCISE_SESSION,
        method: SwimmingRecordingMethod = SwimmingRecordingMethod.AUTOMATIC,
        start: Long = 1_000_000L,
        end: Long = 1_600_000L,
        anomalyRejected: Boolean = false,
    ) = SwimmingEvidence(
        sport = sport,
        origin = origin,
        sourcePackage = source,
        deviceType = device,
        recordId = recordId,
        recordKind = kind,
        recordingMethod = method,
        startEpochMillis = start,
        endEpochMillis = end,
        anomalyRejected = anomalyRejected,
    )

    @Test
    fun compatible_wearable_exercise_records_are_eligible() {
        val pool = SwimmingEligibilityPolicy.evaluate(evidence())
        val openWater = SwimmingEligibilityPolicy.evaluate(
            evidence(
                sport = SportKind.SWIMMING_OPEN_WATER,
                device = "fitness_tracker",
                method = SwimmingRecordingMethod.ACTIVE,
            ),
        )

        assertTrue(pool.eligibleForVerifiedSwimmingProgress)
        assertEquals(SwimmingEligibilityReason.ELIGIBLE, pool.reason)
        assertTrue(openWater.eligibleForVerifiedSwimmingProgress)
        assertEquals(SwimmingEligibilityReason.ELIGIBLE, openWater.reason)
    }

    @Test
    fun phone_imported_manual_and_unknown_origins_are_rejected() {
        listOf(
            EvidenceOrigin.PHONE_MEASURED,
            EvidenceOrigin.HEALTH_IMPORTED,
            EvidenceOrigin.MANUAL,
            EvidenceOrigin.UNKNOWN,
        ).forEach { origin ->
            val result = SwimmingEligibilityPolicy.evaluate(evidence(origin = origin))
            assertFalse(result.eligibleForVerifiedSwimmingProgress)
            assertEquals(SwimmingEligibilityReason.NON_WEARABLE_ORIGIN, result.reason)
        }
    }

    @Test
    fun source_identity_and_compatible_device_are_required() {
        val missingSource = SwimmingEligibilityPolicy.evaluate(evidence(source = " "))
        val missingRecordId = SwimmingEligibilityPolicy.evaluate(evidence(recordId = null))
        val phone = SwimmingEligibilityPolicy.evaluate(evidence(device = "phone"))
        val genericWearable = SwimmingEligibilityPolicy.evaluate(evidence(device = "wearable"))

        assertEquals(SwimmingEligibilityReason.MISSING_SOURCE_PACKAGE, missingSource.reason)
        assertEquals(SwimmingEligibilityReason.MISSING_RECORD_ID, missingRecordId.reason)
        assertEquals(SwimmingEligibilityReason.INCOMPATIBLE_DEVICE, phone.reason)
        assertEquals(SwimmingEligibilityReason.INCOMPATIBLE_DEVICE, genericWearable.reason)
        assertFalse(missingSource.eligibleForVerifiedSwimmingProgress)
        assertFalse(missingRecordId.eligibleForVerifiedSwimmingProgress)
        assertFalse(phone.eligibleForVerifiedSwimmingProgress)
        assertFalse(genericWearable.eligibleForVerifiedSwimmingProgress)
    }

    @Test
    fun only_exercise_sessions_with_active_or_automatic_recording_are_eligible() {
        val otherRecord = SwimmingEligibilityPolicy.evaluate(evidence(kind = SwimmingRecordKind.OTHER))
        val manual = SwimmingEligibilityPolicy.evaluate(evidence(method = SwimmingRecordingMethod.MANUAL))
        val unknown = SwimmingEligibilityPolicy.evaluate(evidence(method = SwimmingRecordingMethod.UNKNOWN))

        assertEquals(SwimmingEligibilityReason.NOT_EXERCISE_SESSION, otherRecord.reason)
        assertEquals(SwimmingEligibilityReason.UNSUPPORTED_RECORDING_METHOD, manual.reason)
        assertEquals(SwimmingEligibilityReason.UNSUPPORTED_RECORDING_METHOD, unknown.reason)
    }

    @Test
    fun invalid_time_ranges_and_anomaly_flags_fail_closed() {
        val zeroDuration = SwimmingEligibilityPolicy.evaluate(evidence(end = 1_000_000L))
        val negativeStart = SwimmingEligibilityPolicy.evaluate(evidence(start = -1L))
        val anomaly = SwimmingEligibilityPolicy.evaluate(evidence(anomalyRejected = true))

        assertEquals(SwimmingEligibilityReason.INVALID_TIME_RANGE, zeroDuration.reason)
        assertEquals(SwimmingEligibilityReason.INVALID_TIME_RANGE, negativeStart.reason)
        assertEquals(SwimmingEligibilityReason.ANOMALY_REJECTED, anomaly.reason)
    }

    @Test
    fun non_swimming_records_cannot_enter_swimming_eligibility() {
        val result = SwimmingEligibilityPolicy.evaluate(evidence(sport = SportKind.RUNNING))

        assertFalse(result.eligibleForVerifiedSwimmingProgress)
        assertEquals(SwimmingEligibilityReason.NOT_SWIMMING, result.reason)
    }
}
