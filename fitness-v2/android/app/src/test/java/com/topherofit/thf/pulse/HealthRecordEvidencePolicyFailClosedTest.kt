package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthRecordEvidencePolicyFailClosedTest {
    private fun assess(
        recordType: String,
        isExerciseSession: Boolean = false,
        exerciseType: Int? = null,
    ) = HealthRecordEvidencePolicy.assess(
        appPackageName = "com.topherofit.thf.pulse",
        dataOrigin = "com.sec.android.app.shealth",
        recordType = recordType,
        recordId = "record-12345678",
        trustedRecordingMethod = true,
        deviceType = Device.TYPE_PHONE,
        exerciseType = exerciseType,
        startEpochMillis = if (isExerciseSession) 1_000L else null,
        endEpochMillis = if (isExerciseSession) 2_000L else null,
        isExerciseSession = isExerciseSession,
    )

    @Test
    fun unknownNonSessionRecordTypeStaysSupportedButNeverRewardVerified() {
        val result = assess(recordType = "FutureRecordFromNewSdk")

        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("UNSUPPORTED_RECORD_TYPE", result.reason)
    }

    @Test
    fun metricTypeCannotBeReclassifiedAsAnExerciseSession() {
        val result = assess(
            recordType = HealthRecordType.STEPS.stableId,
            isExerciseSession = true,
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
        )

        assertEquals(IntegrityClass.SUPPORTED, result.integrityClass)
        assertFalse(result.verifiedForRewards)
        assertEquals("RECORD_TYPE_MISMATCH", result.reason)
    }

    @Test
    fun knownMetricRecordTypesKeepTheirExistingReviewedWriterPath() {
        val result = assess(recordType = HealthRecordType.STEPS.stableId)

        assertEquals(IntegrityClass.VERIFIED, result.integrityClass)
        assertTrue(result.verifiedForRewards)
        assertEquals("APPROVED_PROVIDER_WITH_DEVICE_METADATA", result.reason)
    }

    @Test
    fun typedExerciseSessionRemainsRecognizedWhenRuntimeTypeLabelIsMinified() {
        val result = assess(
            recordType = "a",
            isExerciseSession = true,
            exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
        )

        assertEquals(IntegrityClass.VERIFIED, result.integrityClass)
        assertTrue(result.verifiedForRewards)
    }
}
