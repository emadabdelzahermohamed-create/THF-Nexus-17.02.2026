package com.topherofit.thf.pulse

/**
 * Decides when to supplement a fused-location subscription with Android framework providers.
 * This is a resilience timeout, not a claim that a provider can guarantee a first fix.
 */
object ActivityLocationFallbackPolicy {
    const val FIRST_ACCEPTED_FIX_TIMEOUT_MS = 8_000L
    const val ACCEPTED_FIX_STALE_TIMEOUT_MS = 12_000L

    fun shouldRegisterLegacyProviders(
        requestStartedElapsedMs: Long,
        lastAcceptedElapsedMs: Long?,
        nowElapsedMs: Long,
    ): Boolean {
        if (requestStartedElapsedMs <= 0L || nowElapsedMs < requestStartedElapsedMs) return false
        val lastAccepted = lastAcceptedElapsedMs
        if (lastAccepted == null || lastAccepted < requestStartedElapsedMs) {
            return nowElapsedMs - requestStartedElapsedMs >= FIRST_ACCEPTED_FIX_TIMEOUT_MS
        }
        if (lastAccepted > nowElapsedMs) return false
        return nowElapsedMs - lastAccepted >= ACCEPTED_FIX_STALE_TIMEOUT_MS
    }
    /**
     * Keeps an asynchronous Fused Location Provider registration only for the session
     * generation that requested it. A completion after pause, stop, or replacement must
     * remove its own callback instead of leaving background location updates running.
     */
    fun shouldKeepFusedLocationRegistration(
        sessionModeMatches: Boolean,
        paused: Boolean,
        generationMatches: Boolean,
    ): Boolean = sessionModeMatches && !paused && generationMatches

    /** Prevents an asynchronous failure/watchdog from starting framework updates after pause/stop. */
    fun shouldRegisterLegacyLocationProvider(
        sessionModeMatches: Boolean,
        paused: Boolean,
        alreadyRegistered: Boolean,
    ): Boolean = sessionModeMatches && !paused && !alreadyRegistered

    enum class LegacyProvider { GPS, NETWORK }

    /**
     * Selects only a provider allowed by the user's granted location precision.
     * Approximate-only permission must never attempt GPS_PROVIDER.
     */
    fun selectLegacyProvider(
        finePermissionGranted: Boolean,
        coarsePermissionGranted: Boolean,
        gpsProviderEnabled: Boolean,
        networkProviderEnabled: Boolean,
    ): LegacyProvider? {
        if (!finePermissionGranted && !coarsePermissionGranted) return null
        return when {
            finePermissionGranted && gpsProviderEnabled -> LegacyProvider.GPS
            networkProviderEnabled -> LegacyProvider.NETWORK
            else -> null
        }
    }

}
