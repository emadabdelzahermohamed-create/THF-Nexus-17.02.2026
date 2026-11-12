package com.topherofit.thf.pulse

/**
 * Decides when to supplement a fused-location subscription with Android framework providers.
 * This is a resilience timeout, not a claim that a provider can guarantee a first fix.
 */
object ActivityLocationFallbackPolicy {
    const val FIRST_ACCEPTED_FIX_TIMEOUT_MS = 8_000L
    const val ACCEPTED_FIX_STALE_TIMEOUT_MS = 12_000L
    const val GPS_NO_FIX_FALLBACK_TIMEOUT_MS = 12_000L

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
        allowProviderSwitch: Boolean = false,
    ): Boolean = sessionModeMatches && !paused && (!alreadyRegistered || allowProviderSwitch)

    /**
     * Moves from a silent GPS framework provider to NETWORK_PROVIDER only when coarse
     * permission and the network provider are both available. A successful GPS subscription
     * gets a bounded chance to produce a fresh accepted fix; a failed registration switches
     * immediately. Only one framework provider is active at a time to avoid mixing source
     * streams in the distance accumulator.
     */
    fun shouldFallbackFromGpsToNetwork(
        currentProvider: LegacyProvider?,
        coarsePermissionGranted: Boolean,
        networkProviderEnabled: Boolean,
        gpsRegistrationSucceeded: Boolean,
        providerAttemptStartedElapsedMs: Long,
        lastAcceptedElapsedMs: Long?,
        nowElapsedMs: Long,
    ): Boolean {
        if (currentProvider != LegacyProvider.GPS || !coarsePermissionGranted || !networkProviderEnabled) return false
        if (providerAttemptStartedElapsedMs <= 0L || nowElapsedMs < providerAttemptStartedElapsedMs) return false
        if (!gpsRegistrationSucceeded) return true
        if (nowElapsedMs - providerAttemptStartedElapsedMs < GPS_NO_FIX_FALLBACK_TIMEOUT_MS) return false

        val lastAccepted = lastAcceptedElapsedMs ?: return true
        if (lastAccepted > nowElapsedMs) return false
        return lastAccepted < providerAttemptStartedElapsedMs ||
            nowElapsedMs - lastAccepted >= ACCEPTED_FIX_STALE_TIMEOUT_MS
    }

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
            coarsePermissionGranted && networkProviderEnabled -> LegacyProvider.NETWORK
            else -> null
        }
    }

}
