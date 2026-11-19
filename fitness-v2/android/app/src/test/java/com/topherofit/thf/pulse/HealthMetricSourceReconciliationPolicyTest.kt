package com.topherofit.thf.pulse

import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthMetricSourceReconciliationPolicyTest {
    private val base = Instant.parse("2026-11-19T10:00:00Z")

    private fun candidate(
        index: Int,
        source: String = "com.samsung.android.wear.shealth",
        metric: String = HealthRecordType.STEPS.stableId,
        start: Long = 0L,
        end: Long = 60L,
        value: String = "100",
        verified: Boolean = true,
        modified: Long = index.toLong(),
        label: String = "record-$index",
    ) = HealthMetricSourceCandidate(
        originalIndex = index,
        sourcePackage = source,
        metricType = metric,
        startTime = base.plusSeconds(start),
        endTime = base.plusSeconds(end),
        valueFingerprint = value,
        verifiedForRewards = verified,
        lastModifiedTime = base.plusSeconds(modified),
        value = label,
    )

    @Test
    fun exactMirrorPrefersVerifiedEvidenceEvenWhenOtherSourceIsNewer() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(
                    index = 0,
                    source = "com.google.android.apps.fitness",
                    verified = false,
                    modified = 50L,
                ),
                candidate(
                    index = 1,
                    source = "com.samsung.android.wear.shealth",
                    verified = true,
                    modified = 10L,
                ),
            ),
        )

        assertEquals(listOf("record-1"), result.accepted.map { it.value })
        assertEquals(listOf("record-0"), result.duplicates.map { it.value })
        assertTrue(result.ambiguous.isEmpty())
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun exactMirrorUsesNewestModificationWhenBothSourcesAreVerified() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.google.android.apps.fitness", modified = 10L),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", modified = 20L),
            ),
        )

        assertEquals(listOf("record-1"), result.accepted.map { it.value })
        assertEquals(listOf("record-0"), result.duplicates.map { it.value })
    }

    @Test
    fun exactDuplicatesFromOneProviderWithDifferentRecordIdsAreCollapsed() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, modified = 10L),
                candidate(index = 1, modified = 20L),
            ),
        )

        assertEquals(listOf("record-1"), result.accepted.map { it.value })
        assertEquals(listOf("record-0"), result.duplicates.map { it.value })
    }

    @Test
    fun partiallyOverlappingVerifiedIntervalsFromDifferentProvidersAreAmbiguous() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.google.android.apps.fitness", start = 0L, end = 60L),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", start = 30L, end = 90L),
            ),
        )

        assertTrue(result.accepted.isEmpty())
        assertEquals(listOf("record-0", "record-1"), result.ambiguous.map { it.value })
        assertTrue(result.duplicates.isEmpty())
    }

    @Test
    fun sameIntervalWithDifferentValuesAcrossProvidersIsAmbiguous() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.google.android.apps.fitness", value = "100"),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", value = "101"),
            ),
        )

        assertTrue(result.accepted.isEmpty())
        assertEquals(2, result.ambiguous.size)
    }

    @Test
    fun unverifiedOverlappingProviderDoesNotPoisonVerifiedMetric() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.samsung.android.wear.shealth", verified = true),
                candidate(
                    index = 1,
                    source = "com.google.android.apps.fitness",
                    start = 30L,
                    end = 90L,
                    verified = false,
                ),
            ),
        )

        assertEquals(2, result.accepted.size)
        assertTrue(result.accepted.single { it.originalIndex == 0 }.verifiedForRewards)
        assertFalse(result.accepted.single { it.originalIndex == 1 }.verifiedForRewards)
        assertTrue(result.ambiguous.isEmpty())
    }

    @Test
    fun overlappingIntervalsFromSameProviderAreAlsoAmbiguous() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.samsung.android.wear.shealth", start = 0L, end = 60L),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", start = 30L, end = 90L),
            ),
        )

        assertTrue(result.accepted.isEmpty())
        assertEquals(2, result.ambiguous.size)
    }

    @Test
    fun differentMetricFamiliesDoNotConflictForTheSameInterval() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, metric = HealthRecordType.STEPS.stableId),
                candidate(
                    index = 1,
                    source = "com.google.android.apps.fitness",
                    metric = HealthRecordType.DISTANCE.stableId,
                ),
            ),
        )

        assertEquals(2, result.accepted.size)
        assertTrue(result.ambiguous.isEmpty())
    }

    @Test
    fun adjacentIntervalsFromDifferentProvidersDoNotOverlap() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.google.android.apps.fitness", start = 0L, end = 60L),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", start = 60L, end = 120L),
            ),
        )

        assertEquals(2, result.accepted.size)
        assertTrue(result.ambiguous.isEmpty())
    }

    @Test
    fun zeroValueMirrorsDeduplicateWithoutChangingTheZeroValue() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "com.google.android.apps.fitness", value = "0"),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", value = "0"),
            ),
        )

        assertEquals(1, result.accepted.size)
        assertEquals("0", result.accepted.single().valueFingerprint)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun malformedOrUnlabelledCandidatesRemainVisibleAndUngrouped() {
        val result = HealthMetricSourceReconciliationPolicy.reconcile(
            listOf(
                candidate(index = 0, source = "", start = 0L, end = 60L),
                candidate(index = 1, source = "com.samsung.android.wear.shealth", start = 60L, end = 60L),
            ),
        )

        assertEquals(2, result.accepted.size)
        assertTrue(result.duplicates.isEmpty())
        assertTrue(result.ambiguous.isEmpty())
    }
}
