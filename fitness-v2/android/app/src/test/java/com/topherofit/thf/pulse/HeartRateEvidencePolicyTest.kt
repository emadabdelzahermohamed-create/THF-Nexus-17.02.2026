package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Test

class HeartRateEvidencePolicyTest {
    private val referenceNowEpochMillis = 1_700_000_060_000L

    private fun assess(evidence: HeartRateEvidence) =
        HeartRateEvidencePolicy.assess(evidence, referenceNowEpochMillis)

    private fun evidence(
        bpm: Double? = 72.0,
        observedAt: Long? = 1_700_000_000_000L,
        source: String? = "com.sec.android.app.shealth",
        device: HeartRateDeviceType = HeartRateDeviceType.WATCH,
        origin: HeartRateOrigin = HeartRateOrigin.HEALTH_CONNECT_WEARABLE,
        method: HeartRateCaptureMethod = HeartRateCaptureMethod.AUTOMATICALLY_RECORDED,
        permission: HeartRatePermissionState = HeartRatePermissionState.GRANTED,
        sourceAvailable: Boolean = true,
        readError: Boolean = false,
        recordId: String? = "hr-record-001",
    ) = HeartRateEvidence(bpm, observedAt, source, device, origin, method, permission, sourceAvailable, readError, recordId)

    @Test fun permission_denial_and_revocation_mask_sample_and_origin() {
        val denied = assess(evidence(permission = HeartRatePermissionState.NOT_GRANTED))
        assertEquals(HeartRateDisplayState.PERMISSION_REQUIRED, denied.state)
        assertNull(denied.beatsPerMinute)
        assertNull(denied.sourcePackage)

        val revoked = assess(evidence(permission = HeartRatePermissionState.REVOKED))
        assertEquals(HeartRateDisplayState.PERMISSION_REVOKED, revoked.state)
        assertNull(revoked.beatsPerMinute)
        assertNull(revoked.sourcePackage)
    }

    @Test fun omitted_permission_defaults_to_denied_and_masks_sample_fields() {
        val evidenceWithoutPermission = HeartRateEvidence(
            beatsPerMinute = 98.0,
            observedAtEpochMillis = referenceNowEpochMillis,
            sourcePackage = "com.example.watch",
            deviceType = HeartRateDeviceType.WATCH,
            origin = HeartRateOrigin.HEALTH_CONNECT_WEARABLE,
            recordingMethod = HeartRateCaptureMethod.AUTOMATICALLY_RECORDED,
        )
        val result = assess(evidenceWithoutPermission)
        assertEquals(HeartRatePermissionState.NOT_GRANTED, evidenceWithoutPermission.permissionState)
        assertEquals(HeartRateDisplayState.PERMISSION_REQUIRED, result.state)
        assertNull(result.beatsPerMinute)
        assertNull(result.observedAtEpochMillis)
        assertNull(result.sourcePackage)
        assertEquals(HeartRateTrustTier.UNVERIFIED, result.trustTier)
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun unavailable_source_error_and_no_data_are_distinct_states() {
        assertEquals(
            HeartRateDisplayState.SOURCE_UNAVAILABLE,
            assess(evidence(sourceAvailable = false)).state,
        )
        assertEquals(
            HeartRateDisplayState.ERROR,
            assess(evidence(readError = true)).state,
        )
        val noData = assess(evidence(bpm = null, observedAt = null))
        assertEquals(HeartRateDisplayState.NO_DATA, noData.state)
        assertNull(noData.beatsPerMinute)
    }

    @Test fun automatic_watch_sample_preserves_source_and_device_but_never_verifies_sport() {
        val result = assess(evidence(source = "com.sec.android.app.shealth"))
        assertEquals(HeartRateDisplayState.AVAILABLE, result.state)
        assertEquals(72.0, result.beatsPerMinute!!, 0.0)
        assertEquals("com.sec.android.app.shealth", result.sourcePackage)
        assertEquals(HeartRateDeviceType.WATCH, result.deviceType)
        assertEquals(HeartRateCaptureMethod.AUTOMATICALLY_RECORDED, result.recordingMethod)
        assertEquals(HeartRateTrustTier.TRUSTED_WEARABLE, result.trustTier)
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun actively_recorded_compatible_band_can_be_displayed_as_trusted() {
        val result = assess(
            evidence(
                device = HeartRateDeviceType.FITNESS_BAND,
                method = HeartRateCaptureMethod.ACTIVELY_RECORDED,
            ),
        )
        assertEquals(HeartRateTrustTier.TRUSTED_WEARABLE, result.trustTier)
    }

    @Test fun manual_entry_cannot_become_trusted_by_claiming_watch_device() {
        val result = assess(
            evidence(method = HeartRateCaptureMethod.MANUAL_ENTRY),
        )
        assertEquals(HeartRateDisplayState.AVAILABLE, result.state)
        assertEquals(HeartRateTrustTier.IMPORTED_UNVERIFIED, result.trustTier)
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun imported_phone_and_unknown_origins_are_not_trusted_wearables() {
        assertEquals(
            HeartRateTrustTier.IMPORTED_UNVERIFIED,
            assess(evidence(origin = HeartRateOrigin.HEALTH_CONNECT_IMPORTED)).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            assess(
                evidence(origin = HeartRateOrigin.PHONE_SENSOR, device = HeartRateDeviceType.PHONE),
            ).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            assess(
                evidence(origin = HeartRateOrigin.UNKNOWN, device = HeartRateDeviceType.UNKNOWN),
            ).trustTier,
        )
    }

    @Test fun missing_package_unknown_device_and_unknown_recording_method_fail_closed() {
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            assess(evidence(source = "  ")).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            assess(evidence(device = HeartRateDeviceType.UNKNOWN)).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            assess(evidence(method = HeartRateCaptureMethod.UNKNOWN)).trustTier,
        )
    }

    @Test fun unknown_health_connect_writer_cannot_receive_trusted_wearable_tier() {
        val unknownWriter = evidence(source = "com.example.unknown")
        val result = assess(unknownWriter)
        assertEquals(HeartRateDisplayState.AVAILABLE, result.state)
        assertEquals(HeartRateTrustTier.UNVERIFIED, result.trustTier)
        // Stable identity may still support deduplication; it does not grant trust.
        assertEquals(
            HeartRateStableRecordKey("com.example.unknown", "hr-record-001"),
            HeartRateEvidencePolicy.stableRecordKey(unknownWriter),
        )
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun trusted_wearable_requires_stable_record_identity() {
        val missingId = assess(evidence(recordId = null))
        assertEquals(HeartRateDisplayState.AVAILABLE, missingId.state)
        assertEquals(HeartRateTrustTier.UNVERIFIED, missingId.trustTier)
        assertFalse(missingId.canVerifySportProgress)

        val blankId = assess(evidence(recordId = "  "))
        assertEquals(HeartRateTrustTier.UNVERIFIED, blankId.trustTier)
    }

    @Test fun stable_record_key_is_source_scoped_and_requires_health_connect_identity() {
        val key = HeartRateEvidencePolicy.stableRecordKey(
            evidence(source = " com.example.watch ", recordId = " hr-001 "),
        )
        assertEquals(HeartRateStableRecordKey("com.example.watch", "hr-001"), key)
        assertEquals(
            key,
            HeartRateEvidencePolicy.stableRecordKey(evidence(source = "com.example.watch", recordId = "hr-001")),
        )
        val otherSource = HeartRateEvidencePolicy.stableRecordKey(
            evidence(source = "com.other.watch", recordId = "hr-001"),
        )
        assertFalse(key == otherSource)
        assertNull(HeartRateEvidencePolicy.stableRecordKey(evidence(source = " ", recordId = "hr-001")))
        assertNull(HeartRateEvidencePolicy.stableRecordKey(evidence(recordId = " ")))
        assertNull(
            HeartRateEvidencePolicy.stableRecordKey(
                evidence(origin = HeartRateOrigin.PHONE_SENSOR, device = HeartRateDeviceType.PHONE),
            ),
        )
        assertNull(HeartRateEvidencePolicy.stableRecordKey(evidence(origin = HeartRateOrigin.MANUAL)))
    }

    @Test fun non_finite_implausible_or_untimestamped_samples_are_rejected() {
        for (bpm in listOf(Double.NaN, Double.POSITIVE_INFINITY, 29.0, 241.0)) {
            val result = assess(evidence(bpm = bpm))
            assertEquals(HeartRateDisplayState.INVALID_DATA, result.state)
            assertEquals(HeartRateTrustTier.REJECTED, result.trustTier)
            assertNull(result.beatsPerMinute)
        }
        val noTimestamp = assess(evidence(observedAt = null))
        assertEquals(HeartRateDisplayState.INVALID_DATA, noTimestamp.state)
        assertEquals(HeartRateTrustTier.REJECTED, noTimestamp.trustTier)
    }

    @Test fun sample_at_exact_freshness_boundary_is_current() {
        val boundary = assess(
            evidence(observedAt = referenceNowEpochMillis - HeartRateEvidencePolicy.MAX_SAMPLE_AGE_MILLIS),
        )
        assertEquals(HeartRateDisplayState.AVAILABLE, boundary.state)
        assertEquals(72.0, boundary.beatsPerMinute!!, 0.0)
    }

    @Test fun sample_older_than_freshness_window_is_stale_and_not_current() {
        val observedAt = referenceNowEpochMillis - HeartRateEvidencePolicy.MAX_SAMPLE_AGE_MILLIS - 1L
        val result = assess(evidence(observedAt = observedAt))
        assertEquals(HeartRateDisplayState.STALE_DATA, result.state)
        assertNull(result.beatsPerMinute)
        assertEquals(observedAt, result.observedAtEpochMillis)
        assertEquals("com.example.watch", result.sourcePackage)
        assertEquals(HeartRateTrustTier.UNVERIFIED, result.trustTier)
    }

    @Test fun future_timestamp_at_skew_boundary_is_allowed_but_beyond_is_rejected() {
        val boundary = assess(
            evidence(observedAt = referenceNowEpochMillis + HeartRateEvidencePolicy.MAX_FUTURE_SKEW_MILLIS),
        )
        assertEquals(HeartRateDisplayState.AVAILABLE, boundary.state)

        val beyond = assess(
            evidence(observedAt = referenceNowEpochMillis + HeartRateEvidencePolicy.MAX_FUTURE_SKEW_MILLIS + 1L),
        )
        assertEquals(HeartRateDisplayState.INVALID_DATA, beyond.state)
        assertNull(beyond.beatsPerMinute)
        assertNull(beyond.observedAtEpochMillis)
        assertEquals(HeartRateTrustTier.REJECTED, beyond.trustTier)
    }

    @Test fun non_positive_reference_clock_is_rejected() {
        val result = HeartRateEvidencePolicy.assess(evidence(), nowEpochMillis = 0L)
        assertEquals(HeartRateDisplayState.INVALID_DATA, result.state)
        assertNull(result.beatsPerMinute)
        assertEquals(HeartRateTrustTier.REJECTED, result.trustTier)
    }

    @Test fun timestamp_must_be_positive_and_permission_error_precedence_is_fail_closed() {
        val invalidTime = assess(evidence(observedAt = 0L))
        assertEquals(HeartRateDisplayState.INVALID_DATA, invalidTime.state)

        val revokedWithError = assess(
            evidence(permission = HeartRatePermissionState.REVOKED, readError = true),
        )
        assertEquals(HeartRateDisplayState.PERMISSION_REVOKED, revokedWithError.state)
        assertNull(revokedWithError.sourcePackage)
    }
}
