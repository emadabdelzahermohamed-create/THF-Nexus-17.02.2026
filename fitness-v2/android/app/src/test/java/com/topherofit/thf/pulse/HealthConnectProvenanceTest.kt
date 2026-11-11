package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import androidx.health.connect.client.records.metadata.Metadata
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

    @Test fun reviewedWriterAllowlistIsExplicitAndNormalized() {
        assertTrue(HealthSourceTrustPolicy.isApprovedHealthConnectProvider("com.google.android.apps.fitness"))
        assertTrue(HealthSourceTrustPolicy.isApprovedHealthConnectProvider(" COM.SEC.ANDROID.APP.SHEALTH "))
        assertTrue(HealthSourceTrustPolicy.isApprovedHealthConnectProvider("com.samsung.android.wear.shealth"))
        assertFalse(HealthSourceTrustPolicy.isApprovedHealthConnectProvider("com.example.unreviewed.health"))
        assertFalse(HealthSourceTrustPolicy.isApprovedHealthConnectProvider(" "))
    }

    @Test fun onlyActivityCompatibleDeviceClassesAreAccepted() {
        listOf(
            Device.TYPE_PHONE,
            Device.TYPE_WATCH,
            Device.TYPE_FITNESS_BAND,
            Device.TYPE_CHEST_STRAP,
            Device.TYPE_RING,
        ).forEach { deviceType ->
            assertTrue(HealthSourceTrustPolicy.isCompatibleActivityDeviceType(deviceType))
        }
        assertFalse(HealthSourceTrustPolicy.isCompatibleActivityDeviceType(Device.TYPE_SCALE))
        assertFalse(HealthSourceTrustPolicy.isCompatibleActivityDeviceType(null))
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
    private fun assessSession(
        exerciseType: Int,
        deviceType: Int?,
        dataOrigin: String = "com.samsung.android.wear.shealth",
        recordingMethod: Int = Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED,
        recordId: String = "swimming-session-1",
        startEpochMillis: Long = 1_000L,
        endEpochMillis: Long = 2_000L,
    ): HealthRecordEvidenceAssessment {
        val trustedMethod = recordingMethod == Metadata.RECORDING_METHOD_ACTIVELY_RECORDED ||
            recordingMethod == Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED
        return HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = dataOrigin,
            recordType = "ExerciseSessionRecord",
            recordId = recordId,
            trustedRecordingMethod = trustedMethod,
            deviceType = deviceType,
            recordingMethod = recordingMethod,
            exerciseType = exerciseType,
            startEpochMillis = startEpochMillis,
            endEpochMillis = endEpochMillis,
            isExerciseSession = true,
        )
    }

    @Test fun swimming_phone_only_session_is_not_reward_verified() {
        val result = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            deviceType = Device.TYPE_PHONE,
        )
        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("SWIMMING_INELIGIBLE_NON_WEARABLE_ORIGIN", result.reason)
    }

    @Test fun swimming_requires_a_reviewed_compatible_wearable_class() {
        val watch = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            deviceType = Device.TYPE_WATCH,
        )
        val band = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER,
            deviceType = Device.TYPE_FITNESS_BAND,
        )
        assertEquals(IntegrityClass.VERIFIED, watch.integrityClass)
        assertTrue(watch.verifiedForRewards)
        assertEquals("APPROVED_PROVIDER_WITH_COMPATIBLE_SWIMMING_WEARABLE_METADATA", watch.reason)
        assertEquals(IntegrityClass.VERIFIED, band.integrityClass)
        assertTrue(band.verifiedForRewards)
    }

    @Test fun ring_and_chest_strap_metadata_do_not_qualify_for_swimming() {
        for (deviceType in listOf(Device.TYPE_RING, Device.TYPE_CHEST_STRAP)) {
            val result = assessSession(
                exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
                deviceType = deviceType,
            )
            assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
            assertFalse(result.verifiedForRewards)
            assertEquals("SWIMMING_INELIGIBLE_NON_WEARABLE_ORIGIN", result.reason)
        }
    }

    @Test fun non_swimming_phone_sessions_keep_the_existing_reviewed_provider_path() {
        val result = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
            deviceType = Device.TYPE_PHONE,
        )
        assertEquals(IntegrityClass.VERIFIED, result.integrityClass)
        assertTrue(result.verifiedForRewards)
        assertEquals("APPROVED_PROVIDER_WITH_DEVICE_METADATA", result.reason)
    }

    @Test fun swimming_requires_valid_session_time_and_explicit_exercise_type() {
        val invalidTime = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            deviceType = Device.TYPE_WATCH,
            startEpochMillis = 2_000L,
            endEpochMillis = 1_000L,
        )
        assertEquals(IntegrityClass.SUPPORTED, invalidTime.integrityClass)
        assertFalse(invalidTime.verifiedForRewards)
        assertEquals("INVALID_EXERCISE_SESSION_TIME", invalidTime.reason)

        val missingType = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "ExerciseSessionRecord",
            recordId = "swimming-session-1",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_WATCH,
            recordingMethod = Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED,
            startEpochMillis = 1_000L,
            endEpochMillis = 2_000L,
            isExerciseSession = true,
        )
        assertEquals(IntegrityClass.SUPPORTED, missingType.integrityClass)
        assertFalse(missingType.verifiedForRewards)
        assertEquals("MISSING_EXERCISE_TYPE", missingType.reason)
    }

    @Test fun swimming_manual_or_unreviewed_records_never_become_reward_verified() {
        val manual = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            deviceType = Device.TYPE_WATCH,
            recordingMethod = 0,
        )
        val unreviewed = assessSession(
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            deviceType = Device.TYPE_WATCH,
            dataOrigin = "com.example.unreviewed.health",
        )
        assertEquals(IntegrityClass.MANUAL, manual.integrityClass)
        assertFalse(manual.verifiedForRewards)
        assertEquals(IntegrityClass.SUPPORTED, unreviewed.integrityClass)
        assertFalse(unreviewed.verifiedForRewards)
        assertEquals("UNTRUSTED_PROVIDER", unreviewed.reason)
    }

    @Test fun swimming_gate_does_not_depend_on_runtime_class_name() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = "a",
            recordId = "swimming-session-1",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_PHONE,
            recordingMethod = Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED,
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            startEpochMillis = 1_000L,
            endEpochMillis = 2_000L,
            isExerciseSession = true,
        )
        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("SWIMMING_INELIGIBLE_NON_WEARABLE_ORIGIN", result.reason)
    }


    @Test fun stableExerciseSessionTypeIdIsRecognizedWithoutTypedFlag() {
        val result = HealthRecordEvidencePolicy.assess(
            appPackageName = "com.topherofit.thf.pulse",
            dataOrigin = "com.samsung.android.wear.shealth",
            recordType = HealthRecordType.EXERCISE_SESSION.stableId,
            recordId = "swimming-session-stable-type",
            trustedRecordingMethod = true,
            deviceType = Device.TYPE_PHONE,
            recordingMethod = Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED,
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL,
            startEpochMillis = 1_000L,
            endEpochMillis = 2_000L,
        )
        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("SWIMMING_INELIGIBLE_NON_WEARABLE_ORIGIN", result.reason)
    }
}