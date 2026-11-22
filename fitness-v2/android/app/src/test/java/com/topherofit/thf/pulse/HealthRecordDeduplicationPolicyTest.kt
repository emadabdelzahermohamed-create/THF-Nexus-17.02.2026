package com.topherofit.thf.pulse

import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthRecordDeduplicationPolicyTest {
    private data class Sample(val label: String, val trusted: Boolean)

    private fun candidate(
        key: String?,
        version: Long,
        modified: String,
        label: String,
        trusted: Boolean = true,
        payloadFingerprint: String? = label,
    ) = HealthRecordVersion(
        stableKey = key,
        clientRecordVersion = version,
        lastModifiedTime = Instant.parse(modified),
        value = Sample(label, trusted),
        payloadFingerprint = payloadFingerprint,
    )

    @Test
    fun newestClientRecordVersionWinsEvenWhenItArrivesLater() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 1, "2026-11-01T10:00:00Z", "old"),
                candidate("provider:type:id", 2, "2026-11-01T09:00:00Z", "new"),
            ),
        )

        assertEquals(1, result.selected.size)
        assertEquals("new", result.selected.single().value.label)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun lastModifiedTimeBreaksEqualVersionTies() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "earlier"),
                candidate("provider:type:id", 4, "2026-11-01T10:01:00Z", "later"),
            ),
        )

        assertEquals("later", result.selected.single().value.label)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun equal_version_and_modified_time_with_conflicting_payloads_are_quarantined() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "steps-100", payloadFingerprint = "steps=100"),
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "steps-900", payloadFingerprint = "steps=900"),
            ),
        )

        assertTrue(result.selected.isEmpty())
        assertEquals(2, result.conflicting.size)
        assertEquals(0, result.duplicateCount)
    }

    @Test
    fun identical_latest_payloads_are_deduplicated_safely() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "first", payloadFingerprint = "steps=100"),
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "second", payloadFingerprint = "steps=100"),
            ),
        )

        assertEquals(1, result.selected.size)
        assertEquals(1, result.duplicateCount)
        assertTrue(result.conflicting.isEmpty())
    }

    @Test
    fun missing_payload_fingerprint_on_a_tied_revision_fails_closed() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "first", payloadFingerprint = null),
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "second", payloadFingerprint = null),
            ),
        )

        assertTrue(result.selected.isEmpty())
        assertEquals(2, result.conflicting.size)
    }

    @Test
    fun conflicting_latest_revision_does_not_resurrect_an_older_version() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 3, "2026-11-01T09:00:00Z", "old", payloadFingerprint = "steps=50"),
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "latest-a", payloadFingerprint = "steps=100"),
                candidate("provider:type:id", 4, "2026-11-01T10:00:00Z", "latest-b", payloadFingerprint = "steps=900"),
            ),
        )

        assertTrue(result.selected.isEmpty())
        assertEquals(2, result.conflicting.size)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun latestUntrustedVersionSupersedesOlderTrustedVersion() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate("provider:type:id", 1, "2026-11-01T10:00:00Z", "trusted-old", true),
                candidate("provider:type:id", 2, "2026-11-01T10:01:00Z", "untrusted-new", false),
            ),
        )

        val selected = result.selected.single().value
        assertEquals("untrusted-new", selected.label)
        assertFalse(selected.trusted)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun differentProviderKeysRemainSeparate() {
        val first = WorkoutIdentity.stableHealthRecordKey(
            "com.samsung.android.wear.shealth", HealthRecordType.STEPS.stableId, "same-id",
        )
        val second = WorkoutIdentity.stableHealthRecordKey(
            "com.google.android.apps.fitness", HealthRecordType.STEPS.stableId, "same-id",
        )
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate(first, 1, "2026-11-01T10:00:00Z", "samsung"),
                candidate(second, 1, "2026-11-01T10:00:00Z", "google"),
            ),
        )

        assertEquals(2, result.selected.size)
        assertEquals(0, result.duplicateCount)
    }

    @Test
    fun blankOrMissingIdentityNeverCollapsesUnrelatedRecords() {
        val result = HealthRecordDeduplicationPolicy.selectLatest(
            listOf(
                candidate(null, 0, "2026-11-01T10:00:00Z", "missing-a", false),
                candidate("   ", 0, "2026-11-01T10:00:01Z", "missing-b", false),
                candidate("stable-key", 1, "2026-11-01T10:00:02Z", "stable-a"),
                candidate("stable-key", 1, "2026-11-01T10:00:03Z", "stable-b"),
            ),
        )

        assertEquals(3, result.selected.size)
        assertEquals(1, result.duplicateCount)
        assertTrue(result.selected.any { it.value.label == "missing-a" })
        assertTrue(result.selected.any { it.value.label == "missing-b" })
    }

    @Test
    fun stableRecordTypeIdsAreExplicitAndUnique() {
        val ids = HealthRecordType.values().map { it.stableId }
        assertEquals(
            setOf("StepsRecord", "DistanceRecord", "ActiveCaloriesBurnedRecord", "ExerciseSessionRecord"),
            ids.toSet(),
        )
        assertEquals(ids.size, ids.toSet().size)
    }
}
