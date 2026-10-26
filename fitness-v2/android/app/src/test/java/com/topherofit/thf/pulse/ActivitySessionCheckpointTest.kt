package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivitySessionCheckpointTest {
    private fun checkpoint() = ActivitySessionCheckpoint(
        mode = ActivityMode.RUN,
        weightKg = 72.5,
        startedAtWallMs = 1_700_000_000_000L,
        startedAtElapsedMs = 50_000L,
        distanceMetres = 1_234.5,
        stepBaseline = 4_000f,
        stepDelta = 321,
        lastAccuracyMetres = 4.5f,
        route = listOf(
            ActivityRoutePoint(30.0444, 31.2357, 22.0, 4.5f, 5_000L),
            ActivityRoutePoint(30.0450, 31.2361, null, 5.0f, 10_000L),
        ),
    )

    @Test
    fun checkpointRoundTripsWithoutLosingMeasuredSessionState() {
        val original = checkpoint()
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(original)))

        assertEquals(original, decoded)
        assertTrue(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 70_000L))
    }

    @Test
    fun rebootLikeElapsedRealtimeResetFailsClosed() {
        val original = checkpoint()

        assertFalse(ActivitySessionCheckpointCodec.canRestore(original, nowElapsedMs = 40_000L))
    }

    @Test
    fun impossibleOrCorruptStateIsRejected() {
        assertNull(ActivitySessionCheckpointCodec.decode(""))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|NaN|1|1|0||0|\n"))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|70|1|1|-2||0|\n"))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|70|1|1|0||0|\n95,31,,5,0"))
    }
}
