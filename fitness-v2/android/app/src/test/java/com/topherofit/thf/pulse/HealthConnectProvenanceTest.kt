package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthConnectProvenanceTest {
    @Test fun canonicalKeyIsStableForSameProviderRecord() {
        val first = WorkoutIdentity.stableHealthRecordKey(
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "StepsRecord",
            recordId = "record-12345678",
        )
        val retry = WorkoutIdentity.stableHealthRecordKey(
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "StepsRecord",
            recordId = "record-12345678",
        )
        assertEquals(first, retry)
        assertTrue(first.startsWith("thf-health-"))
    }

    @Test fun unrelatedProviderRecordsStaySeparate() {
        val first = WorkoutIdentity.stableHealthRecordKey(
            "com.samsung.android.wear.shealth", "StepsRecord", "record-12345678",
        )
        val otherRecord = WorkoutIdentity.stableHealthRecordKey(
            "com.samsung.android.wear.shealth", "StepsRecord", "record-87654321",
        )
        val otherProvider = WorkoutIdentity.stableHealthRecordKey(
            "com.google.android.apps.fitness", "StepsRecord", "record-12345678",
        )
        assertNotEquals(first, otherRecord)
        assertNotEquals(first, otherProvider)
    }

    @Test fun trustedExternalHealthRecordWithDeviceMetadataIsRewardVerified() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "StepsRecord",
            recordId = "record-12345678",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_WATCH,
        )
        assertEquals(IntegrityClass.VERIFIED, result.integrityClass)
        assertTrue(result.verifiedForRewards)
        assertEquals("APPROVED_PROVIDER_WITH_DEVICE_METADATA", result.reason)
    }

    @Test fun googleFitPhoneRecordCanBeSupportedAsAReviewedProvider() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.google.android.apps.fitness",
            recordType = "StepsRecord",
            recordId = "fit-record-12345678",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_PHONE,
        )
        assertEquals(IntegrityClass.VERIFIED, result.integrityClass)
        assertTrue(result.verifiedForRewards)
    }

    @Test fun unknownExternalProviderIsSupportedButNotRewardVerified() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.example.unreviewed.health",
            recordType = "StepsRecord",
            recordId = "record-12345678",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_WATCH,
        )
        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("UNTRUSTED_PROVIDER", result.reason)
    }

    @Test fun missingUnknownOrIncompatibleDeviceClassIsNotRewardVerified() {
        val assessments = listOf(null, Device.TYPE_UNKNOWN, Device.TYPE_SCALE).map { deviceType ->
            HealthRecordEvidencePolicy.assess(
                appPackageName = "com.topherofit.thf.pulse",
                dataOrigin = "com.samsung.android.wear.shealth",
                recordType = "StepsRecord",
                recordId = "record-12345678",
                trustedRecordingMethod = true,
                deviceType = deviceType,
            )
        }
        assessments.forEach { result ->
            assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
            assertFalse(result.verifiedForRewards)
            assertEquals("INCOMPATIBLE_OR_UNKNOWN_DEVICE_CLASS", result.reason)
        }
    }

    @Test fun selfAuthoredHealthRecordIsNeverRewardVerified() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.topherofit.thf.pulse",
            recordType = "ExerciseSessionRecord",
            recordId = "record-12345678",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_PHONE,
        )
        assertEquals(IntegrityClass.REJECTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("SELF_AUTHORED", result.reason)
    }

    @Test fun manualOrUnknownHealthRecordIsNotRewardVerified() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "StepsRecord",
            recordId = "record-12345678",
            trustedRecordingMethod = false,
            deviceType = Device.TYPE_WATCH,
        )
        assertEquals(IntegrityClass.MANUAL, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("MANUAL_OR_UNKNOWN_METHOD", result.reason)
    }
}
