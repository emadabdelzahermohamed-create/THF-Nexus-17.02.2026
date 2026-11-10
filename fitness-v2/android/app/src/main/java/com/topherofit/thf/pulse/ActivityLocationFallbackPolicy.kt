package com.topherofit.thf.pulse

/**
 * Rejects delayed fused-location failure callbacks after the activity registration that created
 * them has been paused, stopped, or replaced by another session.
 */
internal object ActivityLocationFallbackPolicy {
    fun shouldRegister(
        requestedMode: ActivityMode,
        activeMode: ActivityMode?,
        paused: Boolean,
        requestGeneration: Long,
        currentGeneration: Long,
    ): Boolean =
        activeMode == requestedMode &&
            !paused &&
            requestGeneration == currentGeneration
}
