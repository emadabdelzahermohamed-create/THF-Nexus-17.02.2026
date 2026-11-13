package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device
import androidx.health.connect.client.records.metadata.Metadata
import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthRecordProvenancePresentationPolicyTest {
    private fun evidence(
        source: String = "com.samsung.android.wear.shealth",
        type: String = "StepsRecord",
        id: String = "provider-record-private-123",
        canonicalKey: String? = null,
        method: Int = Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED,
        device: Int? = Device.TYPE_WATCH,
        integrity: IntegrityClass = IntegrityClass.VERIFIED,
        verified: Boolean = true,
        reason: String = "APPROVED_PROVIDER_WITH_DEVICE_METADATA",
    ) = HealthRecordEvidence(
        recordId = id,
        canonicalKey = canonicalKey ?: WorkoutIdentity.stableHealthRecordKey(source, type, id),
        clientRecordId = "private-client-record-id",
        clientRecordVersion = 7L,
        lastModifiedTime = Instant.parse("2026-11-13T10:00:00Z"),
        recordType = type,
        dataOrigin = source,
        recordingMethod = method,
        deviceType = device,
        deviceManufacturer = "Private Manufacturer",
        deviceModel = "Private Model",
        integrityClass = integrity,
        verifiedForRewards = verified,
        verificationReason = reason,
    )

    @Test
    fun verifiedRecordProducesStablePseudonymousSourceLabelledSummary() {
        val record = evidence()
        val first = HealthRecordProvenancePresentationPolicy.summarize(record)
        val second = HealthRecordProvenancePresentationPolicy.summarize(record)

        assertEquals(first, second)
        assertEquals("com.samsung.android.wear.shealth", first.sourcePackage)
        assertEquals("StepsRecord", first.recordType)
        assertEquals("automatically_recorded", first.recordingMethod)
        assertEquals("watch", first.deviceClass)
        assertEquals("VERIFIED", first.integrityClass)
        assertEquals("APPROVED_PROVIDER_WITH_DEVICE_METADATA", first.verificationReason)
        assertTrue(first.rewardEligible)
        assertNotNull(first.recordKey)
        assertTrue(first.recordKey!!.matches(Regex("^thf-health-[0-9a-f]{40}$")))
    }

    @Test
    fun rawProviderAndClientRecordIdsNeverAppearInTheSummary() {
        val record = evidence()
        val summary = HealthRecordProvenancePresentationPolicy.summarize(record)

        assertFalse(summary.toString().contains(record.recordId))
        assertFalse(summary.toString().contains(requireNotNull(record.clientRecordId)))
        assertFalse(summary.toString().contains(requireNotNull(record.deviceManufacturer)))
        assertFalse(summary.toString().contains(requireNotNull(record.deviceModel)))
        assertNotEquals(record.recordId, summary.recordKey)
    }

    @Test
    fun providerAndRecordTypeArePartOfThePseudonymousIdentity() {
        val samsung = HealthRecordProvenancePresentationPolicy.summarize(evidence())
        val google = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(source = "com.google.android.apps.fitness"),
        )
        val distance = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(type = "DistanceRecord"),
        )

        assertNotEquals(samsung.recordKey, google.recordKey)
        assertNotEquals(samsung.recordKey, distance.recordKey)
    }

    @Test
    fun incompleteOrMismatchedIdentityHasNoStableKeyAndCannotQualify() {
        val missingId = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(id = " "),
        )
        val mismatchedKey = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(canonicalKey = "thf-health-0000000000000000000000000000000000000000"),
        )

        assertNull(missingId.recordKey)
        assertFalse(missingId.rewardEligible)
        assertNull(mismatchedKey.recordKey)
        assertFalse(mismatchedKey.rewardEligible)
    }

    @Test
    fun malformedSourcePackageIsNotExposedOrRewardEligible() {
        val summary = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(source = "com.example\n<script>"),
        )

        assertNull(summary.sourcePackage)
        assertNull(summary.recordKey)
        assertFalse(summary.rewardEligible)
    }

    @Test
    fun unknownRecordTypesRemainVisibleAsUnknownButNeverQualify() {
        val summary = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(type = "FutureSensitiveRecord"),
        )

        assertEquals("unknown", summary.recordType)
        assertNull(summary.recordKey)
        assertFalse(summary.rewardEligible)
    }

    @Test
    fun presentationCannotUpgradeSupportedEvidenceToRewardEligible() {
        val summary = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(integrity = IntegrityClass.SUPPORTED, verified = true),
        )

        assertEquals("SUPPORTED", summary.integrityClass)
        assertFalse(summary.rewardEligible)
    }

    @Test
    fun manualAndUnknownRecordingMethodsAreLabelledAndIneligible() {
        val manual = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(method = Metadata.RECORDING_METHOD_MANUAL_ENTRY),
        )
        val unknown = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(method = Metadata.RECORDING_METHOD_UNKNOWN),
        )

        assertEquals("manual_entry", manual.recordingMethod)
        assertFalse(manual.rewardEligible)
        assertEquals("unknown", unknown.recordingMethod)
        assertFalse(unknown.rewardEligible)
    }

    @Test
    fun incompatibleDeviceClassCannotBePresentedAsRewardEligible() {
        val scale = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(device = Device.TYPE_SCALE),
        )
        val missing = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(device = null),
        )

        assertEquals("scale", scale.deviceClass)
        assertFalse(scale.rewardEligible)
        assertEquals("unknown", missing.deviceClass)
        assertFalse(missing.rewardEligible)
    }

    @Test
    fun sourcePackageNormalizationIsDeterministicAndReasonIsConstrained() {
        val summary = HealthRecordProvenancePresentationPolicy.summarize(
            evidence(
                source = "  COM.SAMSUNG.ANDROID.WEAR.SHEALTH  ",
                reason = "approved provider\n<script>",
            ),
        )

        assertEquals("com.samsung.android.wear.shealth", summary.sourcePackage)
        assertEquals("UNSPECIFIED", summary.verificationReason)
        assertFalse(summary.toString().contains("<script>"))
    }
}
