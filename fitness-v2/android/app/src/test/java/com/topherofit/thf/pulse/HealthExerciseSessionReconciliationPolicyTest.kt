package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Instant

class HealthExerciseSessionReconciliationPolicyTest {
    private fun candidate(
        index: Int,
        kind: HealthActivitySessionKind = HealthActivitySessionKind.RUNNING,
        source: String = "com.google.android.apps.fitness",
        recordId: String = "record-$index",
        start: Long = 1_000_000L,
        end: Long = 1_600_000L,
        observedAt: Long? = 3_000_000L,
        deviceType: Int? = Device.TYPE_PHONE,
        verified: Boolean = true,
        modified: Long = 2_000_000L,
    ) = HealthExerciseSessionCandidate(
        originalIndex = index,
        sourcePackage = source,
        recordId = recordId,
        activityKind = kind,
        startTime = Instant.ofEpochMilli(start),
        endTime = Instant.ofEpochMilli(end),
        observedAt = observedAt?.let(Instant::ofEpochMilli),
        deviceType = deviceType,
        verifiedForRewards = verified,
        lastModifiedTime = Instant.ofEpochMilli(modified),
        value = "record-$index",
    )

    @Test
    fun maps_only_walking_running_and_cycling_families() {
        assertEquals(
            HealthActivitySessionKind.WALKING,
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_WALKING,
            ),
        )
        assertEquals(
            HealthActivitySessionKind.RUNNING,
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
            ),
        )
        assertEquals(
            HealthActivitySessionKind.RUNNING,
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL,
            ),
        )
        assertEquals(
            HealthActivitySessionKind.CYCLING,
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_BIKING,
            ),
        )
        assertEquals(
            HealthActivitySessionKind.CYCLING,
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY,
            ),
        )
        assertNull(
            HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING,
            ),
        )
    }

    @Test
    fun compatible_watch_record_wins_a_mirrored_phone_session() {
        val phone = candidate(index = 0, source = "com.google.android.apps.fitness", deviceType = Device.TYPE_PHONE)
        val watch = candidate(
            index = 1,
            source = "com.sec.android.app.shealth",
            deviceType = Device.TYPE_WATCH,
            modified = 1_900_000L,
        )

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(phone, watch))

        assertEquals(listOf(1), result.accepted.map { it.originalIndex })
        assertEquals(listOf(0), result.duplicates.map { it.originalIndex })
        assertTrue(result.ambiguous.isEmpty())
        assertTrue(result.invalid.isEmpty())
    }

    @Test
    fun latest_record_breaks_ties_when_device_classes_match() {
        val older = candidate(index = 0, source = "com.google.android.apps.fitness", modified = 1_800_000L)
        val newer = candidate(index = 1, source = "com.sec.android.app.shealth", modified = 2_100_000L)

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(older, newer))

        assertEquals(listOf(1), result.accepted.map { it.originalIndex })
        assertEquals(listOf(0), result.duplicates.map { it.originalIndex })
    }

    @Test
    fun same_provider_records_with_distinct_ids_are_not_double_counted() {
        val first = candidate(index = 0, source = "com.sec.android.app.shealth", recordId = "first")
        val second = candidate(index = 1, source = "com.sec.android.app.shealth", recordId = "second")

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(first, second))

        assertEquals(1, result.accepted.size)
        assertEquals(1, result.duplicateCount)
    }

    @Test
    fun walking_running_disagreement_excludes_both_sessions() {
        val walking = candidate(index = 0, kind = HealthActivitySessionKind.WALKING)
        val running = candidate(index = 1, kind = HealthActivitySessionKind.RUNNING, source = "com.sec.android.app.shealth")

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(walking, running))

        assertTrue(result.accepted.isEmpty())
        assertTrue(result.duplicates.isEmpty())
        assertEquals(listOf(0, 1), result.ambiguous.map { it.originalIndex })
    }

    @Test
    fun running_cycling_disagreement_excludes_both_sessions() {
        val running = candidate(index = 0, kind = HealthActivitySessionKind.RUNNING)
        val cycling = candidate(index = 1, kind = HealthActivitySessionKind.CYCLING, source = "com.sec.android.app.shealth")

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(running, cycling))

        assertTrue(result.accepted.isEmpty())
        assertEquals(2, result.ambiguous.size)
    }

    @Test
    fun transitive_conflict_marks_the_entire_near_session_component_ambiguous() {
        val first = candidate(index = 0, kind = HealthActivitySessionKind.WALKING, start = 1_000_000L, end = 1_600_000L)
        val bridge = candidate(index = 1, kind = HealthActivitySessionKind.WALKING, source = "com.sec.android.app.shealth", start = 1_100_000L, end = 1_700_000L)
        val conflict = candidate(index = 2, kind = HealthActivitySessionKind.RUNNING, source = "com.samsung.android.wear.shealth", start = 1_200_000L, end = 1_800_000L)

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(first, bridge, conflict))

        assertTrue(result.accepted.isEmpty())
        assertEquals(listOf(0, 1, 2), result.ambiguous.map { it.originalIndex })
    }

    @Test
    fun distinct_or_only_partially_aligned_sessions_remain_separate() {
        val first = candidate(index = 0)
        val later = candidate(index = 1, source = "com.sec.android.app.shealth", start = 2_000_000L, end = 2_600_000L)
        val partial = candidate(index = 2, source = "com.samsung.android.wear.shealth", start = 1_000_000L, end = 1_900_000L)

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(first, later, partial))

        assertEquals(3, result.accepted.size)
        assertTrue(result.duplicates.isEmpty())
        assertTrue(result.ambiguous.isEmpty())
    }

    @Test
    fun unverified_records_do_not_poison_a_verified_session() {
        val verified = candidate(index = 0, kind = HealthActivitySessionKind.RUNNING)
        val unverified = candidate(
            index = 1,
            kind = HealthActivitySessionKind.WALKING,
            source = "com.example.unreviewed.health",
            verified = false,
        )

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(verified, unverified))

        assertEquals(listOf(0, 1), result.accepted.map { it.originalIndex })
        assertTrue(result.ambiguous.isEmpty())
        assertTrue(result.duplicates.isEmpty())
    }

    @Test
    fun malformed_verified_sessions_fail_closed_without_erasing_provenance() {
        val missingSource = candidate(index = 0, source = " ")
        val missingId = candidate(index = 1, recordId = " ")
        val invalidTime = candidate(index = 2, start = 1_600_000L, end = 1_000_000L)
        val missingObservation = candidate(index = 3, observedAt = null)
        val futureSession = candidate(index = 4, end = 4_000_000L, observedAt = 3_000_000L)

        val result = HealthExerciseSessionReconciliationPolicy.reconcile(
            listOf(missingSource, missingId, invalidTime, missingObservation, futureSession),
        )

        assertTrue(result.accepted.isEmpty())
        assertEquals(
            listOf(
                "MISSING_SOURCE_PACKAGE",
                "MISSING_RECORD_ID",
                "INVALID_ACTIVITY_SESSION_TIME",
                "MISSING_OBSERVATION_TIME",
                "FUTURE_ACTIVITY_SESSION",
            ),
            result.invalid.map { it.reason },
        )
    }

    @Test
    fun duplicate_winner_is_deterministic_for_equal_source_metadata() {
        val first = candidate(index = 0, source = "com.google.android.apps.fitness", recordId = "a")
        val second = candidate(index = 1, source = "com.google.android.apps.fitness", recordId = "b")

        val firstResult = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(first, second))
        val secondResult = HealthExerciseSessionReconciliationPolicy.reconcile(listOf(second, first))

        assertEquals(firstResult.accepted.single().recordId, secondResult.accepted.single().recordId)
        assertFalse(firstResult.accepted.isEmpty())
    }
}
