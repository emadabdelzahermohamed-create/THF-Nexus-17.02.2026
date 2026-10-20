package com.topherofit.thf.pulse

sealed interface HealthSyncDecision {
    data object Started : HealthSyncDecision
    data class Wait(val retryAfterMs: Long) : HealthSyncDecision
}

/**
 * Serializes Health Connect summary reads and applies a small client-side cooldown.
 * Health Connect enforces its own quotas; this gate prevents accidental request bursts
 * from repeated taps while preserving a longer backoff after a provider rate-limit.
 */
class HealthSyncGate(
    private val normalCooldownMs: Long = 5_000L,
    private val rateLimitCooldownMs: Long = 60_000L,
) {
    private var running = false
    private var nextAllowedAtMs = 0L

    @Synchronized
    fun tryStart(nowMs: Long = System.currentTimeMillis()): HealthSyncDecision {
        if (running) return HealthSyncDecision.Wait(1_000L)
        if (nowMs < nextAllowedAtMs) return HealthSyncDecision.Wait(nextAllowedAtMs - nowMs)
        running = true
        return HealthSyncDecision.Started
    }

    @Synchronized
    fun finish(nowMs: Long = System.currentTimeMillis(), rateLimited: Boolean) {
        running = false
        val cooldown = if (rateLimited) rateLimitCooldownMs else normalCooldownMs
        nextAllowedAtMs = maxOf(nextAllowedAtMs, nowMs + cooldown)
    }
}
