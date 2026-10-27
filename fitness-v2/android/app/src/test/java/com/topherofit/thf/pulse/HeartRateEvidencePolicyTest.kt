package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class HeartRateEvidencePolicyTest {
    private fun evidence(
        bpm: Double? = 72.0,
        observedAt: Long? = 1_700_000_000_000L,
        source: String? = "com.example.watch",
        device: HeartRateDeviceType = HeartRateDeviceType.WATCH,
        origin: HeartRateOrigin = HeartRateOrigin.HEALTH_CONNECT_WEARABLE,
        method: HeartRateRecordingMethod = HeartRateRecordingMethod.AUTOMATICALLY_RECORDED,
        permission: HeartRatePermissionState = HeartRatePermissionState.GRANTED,
        sourceAvailable: Boolean = true,
        readError: Boolean = false,
    ) = HeartRateEvidence(bpm, observedAt, source, device, origin, method, permission, sourceAvailable, readError)

    @Test fun permission_denial_and_revocation_mask_sample_and_origin() {
        val denied = HeartRateEvidencePolicy.assess(evidence(permission = HeartRatePermissionState.NOT_GRANTED))
        assertEquals(HeartRateDisplayState.PERMISSION_REQUIRED, denied.state)
        assertNull(denied.beatsPerMinute)
        assertNull(denied.sourcePackage)

        val revoked = HeartRateEvidencePolicy.assess(evidence(permission = HeartRatePermissionState.REVOKED))
        assertEquals(HeartRateDisplayState.PERMISSION_REVOKED, revoked.state)
        assertNull(revoked.beatsPerMinute)
        assertNull(revoked.sourcePackage)
    }

    @Test fun unavailable_source_error_and_no_data_are_distinct_states() {
        assertEquals(
            HeartRateDisplayState.SOURCE_UNAVAILABLE,
            HeartRateEvidencePolicy.assess(evidence(sourceAvailable = false)).state,
        )
        assertEquals(
            HeartRateDisplayState.ERROR,
            HeartRateEvidencePolicy.assess(evidence(readError = true)).state,
        )
        val noData = HeartRateEvidencePolicy.assess(evidence(bpm = null, observedAt = null))
        assertEquals(HeartRateDisplayState.NO_DATA, noData.state)
        assertNull(noData.beatsPerMinute)
    }

    @Test fun automatic_watch_sample_preserves_source_and_device_but_never_verifies_sport() {
        val result = HeartRateEvidencePolicy.assess(evidence(source = "com.example.watch"))
        assertEquals(HeartRateDisplayState.AVAILABLE, result.state)
        assertEquals(72.0, result.beatsPerMinute!!, 0.0)
        assertEquals("com.example.watch", result.sourcePackage)
        assertEquals(HeartRateDeviceType.WATCH, result.deviceType)
        assertEquals(HeartRateRecordingMethod.AUTOMATICALLY_RECORDED, result.recordingMethod)
        assertEquals(HeartRateTrustTier.TRUSTED_WEARABLE, result.trustTier)
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun actively_recorded_compatible_band_can_be_displayed_as_trusted() {
        val result = HeartRateEvidencePolicy.assess(
            evidence(
                device = HeartRateDeviceType.FITNESS_BAND,
                method = HeartRateRecordingMethod.ACTIVELY_RECORDED,
            ),
        )
        assertEquals(HeartRateTrustTier.TRUSTED_WEARABLE, result.trustTier)
    }

    @Test fun manual_entry_cannot_become_trusted_by_claiming_watch_device() {
        val result = HeartRateEvidencePolicy.assess(
            evidence(method = HeartRateRecordingMethod.MANUAL_ENTRY),
        )
        assertEquals(HeartRateDisplayState.AVAILABLE, result.state)
        assertEquals(HeartRateTrustTier.IMPORTED_UNVERIFIED, result.trustTier)
        assertFalse(result.canVerifySportProgress)
    }

    @Test fun imported_phone_and_unknown_origins_are_not_trusted_wearables() {
        assertEquals(
            HeartRateTrustTier.IMPORTED_UNVERIFIED,
            HeartRateEvidencePolicy.assess(evidence(origin = HeartRateOrigin.HEALTH_CONNECT_IMPORTED)).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            HeartRateEvidencePolicy.assess(
                evidence(origin = HeartRateOrigin.PHONE_SENSOR, device = HeartRateDeviceType.PHONE),
            ).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            HeartRateEvidencePolicy.assess(
                evidence(origin = HeartRateOrigin.UNKNOWN, device = HeartRateDeviceType.UNKNOWN),
            ).trustTier,
        )
    }

    @Test fun missing_package_unknown_device_and_unknown_recording_method_fail_closed() {
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            HeartRateEvidencePolicy.assess(evidence(source = "  ")).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            HeartRateEvidencePolicy.assess(evidence(device = HeartRateDeviceType.UNKNOWN)).trustTier,
        )
        assertEquals(
            HeartRateTrustTier.UNVERIFIED,
            HeartRateEvidencePolicy.assess(evidence(method = HeartRateRecordingMethod.UNKNOWN)).trustTier,
        )
    }

    @Test fun non_finite_implausible_or_untimestamped_samples_are_rejected() {
        for (bpm in listOf(Double.NaN, Double.POSITIVE_INFINITY, 29.0, 241.0)) {
            val result = HeartRateEvidencePolicy.assess(evidence(bpm = bpm))
            assertEquals(HeartRateDisplayState.INVALID_DATA, result.state)
            assertEquals(HeartRateTrustTier.REJECTED, result.trustTier)
            assertNull(result.beatsPerMinute)
        }
        val noTimestamp = HeartRateEvidencePolicy.assess(evidence(observedAt = null))
        assertEquals(HeartRateDisplayState.INVALID_DATA, noTimestamp.state)
        assertEquals(HeartRateTrustTier.REJECTED, noTimestamp.trustTier)
    }

    @Test fun timestamp_must_be_positive_and_permission_error_precedence_is_fail_closed() {
        val invalidTime = HeartRateEvidencePolicy.assess(evidence(observedAt = 0L))
        assertEquals(HeartRateDisplayState.INVALID_DATA, invalidTime.state)

        val revokedWithError = HeartRateEvidencePolicy.assess(
            evidence(permission = HeartRatePermissionState.REVOKED, readError = true),
        )
        assertEquals(HeartRateDisplayState.PERMISSION_REVOKED, revokedWithError.state)
        assertNull(revokedWithError.sourcePackage)
    }
}
