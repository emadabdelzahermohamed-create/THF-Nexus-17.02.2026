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
    ) = HealthRecordVersion(
        stableKey = key,
        clientRecordVersion = version,
        lastModifiedTime = Instant.parse(modified),
        value = Sample(label, trusted),
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
