package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class WorkoutIdentityTest {
    @Test
    fun preservesValidSuppliedIdForRetryDeduplication() {
        val id = "thf-workout-12345678"
        assertEquals(id, WorkoutIdentity.stableClientRecordId(id, 1_700_000_000_000L, "squat"))
    }

    @Test
    fun fallbackIdIsDeterministicAndExerciseScoped() {
        val first = WorkoutIdentity.stableClientRecordId("", 1_700_000_000_000L, "squat")
        val retry = WorkoutIdentity.stableClientRecordId(null, 1_700_000_000_000L, "squat")
        val other = WorkoutIdentity.stableClientRecordId(null, 1_700_000_000_000L, "run")
        assertEquals(first, retry)
        assertNotEquals(first, other)
        assertTrue(first.startsWith("thf-workout-"))
    }

    @Test
    fun newSessionIdsAreNonceBackedAndUniqueEvenAtSameTimestamp() {
        val first = WorkoutIdentity.newSessionId(1_700_000_000_000L)
        val second = WorkoutIdentity.newSessionId(1_700_000_000_000L)
        assertNotEquals(first, second)
        assertTrue(first.matches(Regex("thf-workout-1700000000000-[0-9a-f]{32}")))
        assertTrue(second.matches(Regex("thf-workout-1700000000000-[0-9a-f]{32}")))
    }
}
