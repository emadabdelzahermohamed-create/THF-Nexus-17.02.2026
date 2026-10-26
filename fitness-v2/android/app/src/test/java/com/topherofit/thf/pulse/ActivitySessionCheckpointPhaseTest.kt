package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ActivitySessionCheckpointPhaseTest {
    @Test
    fun armedCheckpointRoundTripsWithoutInventingActivation() {
        val checkpoint = ActivitySessionCheckpoint(
            mode = ActivityMode.WALK,
            weightKg = 70.0,
            startedAtWallMs = 1_000L,
            startedAtElapsedMs = 10_000L,
            savedAtElapsedMs = 12_000L,
            distanceMetres = 4.0,
            stepBaseline = 100f,
            stepDelta = 1,
            lastAccuracyMetres = 7f,
            route = listOf(ActivityRoutePoint(30.0, 31.0, null, 7f, 1_000L)),
            phase = ActivitySessionPhase.ARMED,
            activatedAtWallMs = null,
            activatedAtElapsedMs = null,
        )

        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(ActivitySessionCheckpointCodec.encode(checkpoint)))
        assertEquals(ActivitySessionPhase.ARMED, decoded.phase)
        assertNull(decoded.activatedAtWallMs)
        assertNull(decoded.activatedAtElapsedMs)
    }

    @Test
    fun activeCheckpointAdjustsActivationClockByRestartDowntime() {
        val checkpoint = ActivitySessionCheckpoint(
            mode = ActivityMode.RUN,
            weightKg = 70.0,
            startedAtWallMs = 1_000L,
            startedAtElapsedMs = 10_000L,
            savedAtElapsedMs = 20_000L,
            distanceMetres = 100.0,
            stepBaseline = 100f,
            stepDelta = 20,
            lastAccuracyMetres = 5f,
            route = emptyList(),
            phase = ActivitySessionPhase.ACTIVE,
            activatedAtWallMs = 2_000L,
            activatedAtElapsedMs = 12_000L,
        )

        assertEquals(17_000L, ActivitySessionCheckpointCodec.adjustedActivatedAtElapsedMs(checkpoint, 25_000L))
    }

    @Test
    fun legacyV1CheckpointRestoresAsActiveForInPlaceUpdateCompatibility() {
        val legacy = "1|run|70.0|1000|10000|20000|100.0|100.0|20|5.0\n"
        val decoded = requireNotNull(ActivitySessionCheckpointCodec.decode(legacy))

        assertEquals(ActivitySessionPhase.ACTIVE, decoded.phase)
        assertEquals(decoded.startedAtWallMs, decoded.activatedAtWallMs)
        assertEquals(decoded.startedAtElapsedMs, decoded.activatedAtElapsedMs)
    }
}
