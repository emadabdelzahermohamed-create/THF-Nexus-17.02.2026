package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivitySessionCheckpointTest {
    private fun checkpoint(bootCount: Int? = 7) = ActivitySessionCheckpoint(
        mode = ActivityMode.RUN,
        weightKg = 72.5,
        startedAtWallMs = 1_700_000_000_000L,
        startedAtElapsedMs = 50_000L,
        savedAtElapsedMs = 65_000L,
        distanceMetres = 1_234.5,
        stepBaseline = 4_000f,
        stepDelta = 321,
        lastAccuracyMetres = 4.5f,
        route = listOf(
            ActivityRoutePoint(30.0444, 31.2357, 22.0, 4.5f, 5_000L),
            ActivityRoutePoint(30.0450, 31.2361, null, 5.0f, 10_000L),
        ),
        bootCount = bootCount,
    )

    @Test
    fun checkpointRoundTripsWithoutLosingMeasuredSessionState() {
        val original = checkpoint()
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(original)))

        assertEquals(original, decoded)
        assertTrue(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 70_000L, currentBootCount = 7))
        assertEquals(55_000L, ActivitySessionCheckpointCodec.adjustedStartedAtElapsedMs(decoded, 70_000L))
    }

    @Test
    fun processDeathAfterSeveralMinutesRestoresOnSameBoot() {
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(checkpoint())))

        assertTrue(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 500_000L, currentBootCount = 7))
        assertEquals(485_000L, ActivitySessionCheckpointCodec.adjustedStartedAtElapsedMs(decoded, 500_000L))
    }

    @Test
    fun sameBootRecoveryExpiresAfterTwentyFourHours() {
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(checkpoint())))
        val expiredAt = 65_000L + 24L * 60L * 60L * 1_000L + 1L

        assertFalse(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = expiredAt, currentBootCount = 7))
    }

    @Test
    fun changedBootCountRejectsCheckpointEvenWhenElapsedClockIsHigher() {
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(checkpoint())))

        assertFalse(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 70_000L, currentBootCount = 8))
    }

    @Test
    fun legacyV2CheckpointUsesConservativeRestoreWindow() {
        val legacyV2 = "2|run|72.5|1700000000000|50000|65000|1234.5|4000.0|321|4.5|active|1700000001000|51000\n" +
            "30.0444,31.2357,22.0,4.5,5000;30.0450,31.2361,,5.0,10000"
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(legacyV2))

        assertNull(decoded.bootCount)
        assertTrue(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 70_000L, currentBootCount = 7))
        assertFalse(ActivitySessionCheckpointCodec.canRestore(decoded, nowElapsedMs = 185_001L, currentBootCount = 7))
    }

    @Test
    fun rebootLikeElapsedRealtimeResetFailsClosed() {
        val original = checkpoint()

        assertFalse(ActivitySessionCheckpointCodec.canRestore(original, nowElapsedMs = 40_000L, currentBootCount = 7))
    }

    @Test
    fun impossibleOrCorruptStateIsRejected() {
        assertNull(ActivitySessionCheckpointCodec.decode(""))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|NaN|1|1|1|0||0|\n"))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|70|1|1|1|-2||0|\n"))
        assertNull(ActivitySessionCheckpointCodec.decode("1|run|70|1|1|1|0||0|\n95,31,,5,0"))
    }
}
