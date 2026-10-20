package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthSyncGateTest {
    @Test
    fun rejectsConcurrentAndCooldownRequests() {
        val gate = HealthSyncGate(normalCooldownMs = 5_000L, rateLimitCooldownMs = 60_000L)

        assertEquals(HealthSyncDecision.Started, gate.tryStart(1_000L))
        assertTrue(gate.tryStart(1_001L) is HealthSyncDecision.Wait)

        gate.finish(2_000L, rateLimited = false)
        val normalWait = gate.tryStart(6_999L) as HealthSyncDecision.Wait
        assertEquals(1L, normalWait.retryAfterMs)
        assertEquals(HealthSyncDecision.Started, gate.tryStart(7_000L))
    }

    @Test
    fun rateLimitFailureAppliesLongerBackoff() {
        val gate = HealthSyncGate(normalCooldownMs = 5_000L, rateLimitCooldownMs = 60_000L)

        assertEquals(HealthSyncDecision.Started, gate.tryStart(10_000L))
        gate.finish(11_000L, rateLimited = true)

        val wait = gate.tryStart(40_000L) as HealthSyncDecision.Wait
        assertEquals(31_000L, wait.retryAfterMs)
        assertEquals(HealthSyncDecision.Started, gate.tryStart(71_000L))
    }
}
