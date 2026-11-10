package com.topherofit.thf.pulse

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityLocationFallbackPolicyTest {
    @Test
    fun currentActiveRegistrationMayUseLegacyFallback() {
        assertTrue(
            ActivityLocationFallbackPolicy.shouldRegister(
                requestedMode = ActivityMode.WALK,
                activeMode = ActivityMode.WALK,
                paused = false,
                requestGeneration = 7L,
                currentGeneration = 7L,
            ),
        )
    }

    @Test
    fun pausedSessionRejectsDelayedFallback() {
        assertFalse(
            ActivityLocationFallbackPolicy.shouldRegister(
                requestedMode = ActivityMode.WALK,
                activeMode = ActivityMode.WALK,
                paused = true,
                requestGeneration = 7L,
                currentGeneration = 7L,
            ),
        )
    }

    @Test
    fun stoppedOrReplacedSessionRejectsDelayedFallback() {
        assertFalse(
            ActivityLocationFallbackPolicy.shouldRegister(
                requestedMode = ActivityMode.WALK,
                activeMode = null,
                paused = false,
                requestGeneration = 7L,
                currentGeneration = 8L,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldRegister(
                requestedMode = ActivityMode.WALK,
                activeMode = ActivityMode.RUN,
                paused = false,
                requestGeneration = 7L,
                currentGeneration = 8L,
            ),
        )
    }

    @Test
    fun staleGenerationCannotRearmSameModeSession() {
        assertFalse(
            ActivityLocationFallbackPolicy.shouldRegister(
                requestedMode = ActivityMode.WALK,
                activeMode = ActivityMode.WALK,
                paused = false,
                requestGeneration = 6L,
                currentGeneration = 7L,
            ),
        )
    }
}
