package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityRestoreDispatchTest {
    @Test
    fun synchronousStartFailureIsRejectedWithoutPublishingPendingState() {
        var starts = 0
        var accepted = 0
        var rejected = 0

        val result = ActivityRestoreDispatch.attempt(
            start = {
                starts += 1
                throw IllegalStateException("foreground service start denied")
            },
            onAccepted = { accepted += 1 },
            onRejected = { rejected += 1 },
        )

        assertFalse(result)
        assertEquals(1, starts)
        assertEquals(0, accepted)
        assertEquals(1, rejected)
    }

    @Test
    fun acceptedStartPublishesPendingStateExactlyOnce() {
        var starts = 0
        var accepted = 0
        var rejected = 0

        val result = ActivityRestoreDispatch.attempt(
            start = { starts += 1 },
            onAccepted = { accepted += 1 },
            onRejected = { rejected += 1 },
        )

        assertTrue(result)
        assertEquals(1, starts)
        assertEquals(1, accepted)
        assertEquals(0, rejected)
    }
}
