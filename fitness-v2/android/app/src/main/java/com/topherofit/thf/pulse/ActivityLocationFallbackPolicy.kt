package com.topherofit.thf.pulse

enum class ActivityForegroundServiceKind { LOCATION, HEALTH }

/**
 * Android 14+ requires the runtime prerequisites for the selected foreground-service type.
 * A disabled system location switch cannot start a location FGS even when app location
 * permission remains granted; step collection can continue under the health type when
 * ACTIVITY_RECOGNITION is still granted.
 */
object ActivityForegroundServiceTypePolicy {
    fun forActivity(
        locationPermissionGranted: Boolean,
        locationServicesEnabled: Boolean,
        activityRecognitionPermissionGranted: Boolean,
    ): ActivityForegroundServiceKind? = when {
        locationPermissionGranted && locationServicesEnabled -> ActivityForegroundServiceKind.LOCATION
        activityRecognitionPermissionGranted -> ActivityForegroundServiceKind.HEALTH
        else -> null
    }
}


/**
 * Identifies only operating-system denials that can be retried after the user-visible
 * activity/permission state changes. Invalid service types and programming errors must
 * still fail loudly rather than being hidden as recoverable startup failures.
 */
object ActivityForegroundServiceStartFailurePolicy {
    private const val START_NOT_ALLOWED_EXCEPTION =
        "android.app.ForegroundServiceStartNotAllowedException"

    fun isRecoverable(errorClassName: String, apiLevel: Int): Boolean =
        errorClassName == "java.lang.SecurityException" ||
            (apiLevel >= 31 && errorClassName == START_NOT_ALLOWED_EXCEPTION)
}

/**
 * Decides when to supplement a fused-location subscription with Android framework providers.
 * This is a resilience timeout, not a claim that a provider can guarantee a first fix.
 */
object ActivityLocationFallbackPolicy {
    const val FIRST_ACCEPTED_FIX_TIMEOUT_MS = 8_000L
    const val ACCEPTED_FIX_STALE_TIMEOUT_MS = 12_000L
    const val GPS_NO_FIX_FALLBACK_TIMEOUT_MS = 12_000L
    const val LEGACY_PROVIDER_RETRY_BASE_MS = 4_000L
    const val LEGACY_PROVIDER_RETRY_MAX_MS = 30_000L

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
        finePermissionGranted: Boolean,
        coarsePermissionGranted: Boolean,
        networkProviderEnabled: Boolean,
        gpsRegistrationSucceeded: Boolean,
        providerAttemptStartedElapsedMs: Long,
        lastAcceptedElapsedMs: Long?,
        nowElapsedMs: Long,
    ): Boolean {
        if (currentProvider != LegacyProvider.GPS || !coarsePermissionGranted || !networkProviderEnabled) return false
        // Android 12+ can downgrade an active grant from precise to approximate without
        // disabling the GPS provider. Do not keep a GPS subscription that is no longer
        // authorized; switch to NETWORK on the next watchdog pass instead of waiting
        // for the normal silent-provider timeout.
        if (!finePermissionGranted) return true
        if (providerAttemptStartedElapsedMs <= 0L || nowElapsedMs < providerAttemptStartedElapsedMs) return false
        if (!gpsRegistrationSucceeded) return true
        if (nowElapsedMs - providerAttemptStartedElapsedMs < GPS_NO_FIX_FALLBACK_TIMEOUT_MS) return false

        val lastAccepted = lastAcceptedElapsedMs ?: return true
        if (lastAccepted > nowElapsedMs) return false
        return lastAccepted < providerAttemptStartedElapsedMs ||
            nowElapsedMs - lastAccepted >= ACCEPTED_FIX_STALE_TIMEOUT_MS
    }

    /** Bounded exponential backoff for repeated framework-provider registration failures. */
    fun legacyProviderRetryDelayMs(failureCount: Int): Long {
        if (failureCount <= 0) return 0L
        var delayMs = LEGACY_PROVIDER_RETRY_BASE_MS
        repeat((failureCount - 1).coerceAtMost(3)) {
            delayMs = (delayMs * 2L).coerceAtMost(LEGACY_PROVIDER_RETRY_MAX_MS)
        }
        return delayMs.coerceAtMost(LEGACY_PROVIDER_RETRY_MAX_MS)
    }

    /**
     * Rejects queued callbacks from a framework provider that has already been replaced.
     * LocationManager.removeUpdates() does not make an already queued callback safe to consume;
     * the listener generation and provider identity must both still match.
     */
    fun shouldAcceptLegacyProviderCallback(
        expectedProvider: LegacyProvider?,
        callbackProvider: String?,
        registrationGenerationMatches: Boolean,
    ): Boolean {
        if (!registrationGenerationMatches) return false
        val expectedLabel = when (expectedProvider) {
            LegacyProvider.GPS -> "gps"
            LegacyProvider.NETWORK -> "network"
            null -> return false
        }
        return callbackProvider?.trim()?.equals(expectedLabel, ignoreCase = true) == true
    }


    /**
     * Fused remains the primary source while the framework provider is a bounded fallback.
     * When both subscriptions overlap, only a fresh accepted Fused fix that is at least as
     * accurate as the current framework fix may take ownership. This prevents alternating
     * provider callbacks from repeatedly resetting the distance accumulator.
     */
    fun shouldPromoteFusedLocation(
        sessionModeMatches: Boolean,
        paused: Boolean,
        legacyProviderActive: Boolean,
        fusedFixAccuracyMetres: Double?,
        fusedFixElapsedMs: Long?,
        currentAcceptedAccuracyMetres: Double?,
        currentAcceptedElapsedMs: Long?,
        currentAcceptedFixFresh: Boolean,
    ): Boolean {
        if (!sessionModeMatches || paused || !legacyProviderActive) return false
        val fusedAccuracy = fusedFixAccuracyMetres?.takeIf { it.isFinite() && it > 0.0 } ?: return false
        val fusedElapsed = fusedFixElapsedMs?.takeIf { it > 0L } ?: return false
        if (currentAcceptedFixFresh) {
            val currentElapsed = currentAcceptedElapsedMs?.takeIf { it > 0L } ?: return false
            // Equal timestamps cannot establish that Fused is newer; keep the current source.
            if (fusedElapsed <= currentElapsed) return false
        }
        val currentAccuracy = currentAcceptedAccuracyMetres?.takeIf { it.isFinite() && it > 0.0 }
        if (!currentAcceptedFixFresh || currentAccuracy == null) return true
        return fusedAccuracy <= currentAccuracy
    }

    /**
     * A permission revocation must tear down every active location subscription and live fix,
     * including an FLP callback that has not delivered its first result yet.
     */
    fun shouldSuspendLocationSources(
        hasLocationPermission: Boolean,
        fusedCallbackRegistered: Boolean,
        legacyProviderRegistered: Boolean,
        hasLiveLocationState: Boolean,
    ): Boolean = !hasLocationPermission &&
        (fusedCallbackRegistered || legacyProviderRegistered || hasLiveLocationState)

    /**
     * Resume location collection only after permission returns to the same live, unpaused session.
     */
    fun shouldResumeLocationSources(
        permissionWasBlocked: Boolean,
        hasLocationPermission: Boolean,
        sessionModeMatches: Boolean,
        paused: Boolean,
    ): Boolean = permissionWasBlocked && hasLocationPermission && sessionModeMatches && !paused

    enum class LegacyProvider { GPS, NETWORK }

    /**
     * A framework subscription must be removed as soon as its permission is no longer granted.
     * Android can leave a provider enabled after the user downgrades Precise to Approximate.
     */
    fun isLegacyProviderAuthorized(
        provider: LegacyProvider?,
        finePermissionGranted: Boolean,
        coarsePermissionGranted: Boolean,
    ): Boolean = when (provider) {
        LegacyProvider.GPS -> finePermissionGranted
        LegacyProvider.NETWORK -> coarsePermissionGranted
        null -> false
    }

    /**
     * Selects only a provider allowed by the user's granted location precision.
     * Approximate-only permission must never attempt GPS_PROVIDER.
     */
    fun selectLegacyProvider(
        finePermissionGranted: Boolean,
        coarsePermissionGranted: Boolean,
        gpsProviderEnabled: Boolean,
        networkProviderEnabled: Boolean,
        preferredProvider: LegacyProvider? = null,
    ): LegacyProvider? {
        if (!finePermissionGranted && !coarsePermissionGranted) return null
        return when {
            preferredProvider == LegacyProvider.GPS && finePermissionGranted && gpsProviderEnabled -> LegacyProvider.GPS
            preferredProvider == LegacyProvider.NETWORK && coarsePermissionGranted && networkProviderEnabled -> LegacyProvider.NETWORK
            finePermissionGranted && gpsProviderEnabled -> LegacyProvider.GPS
            coarsePermissionGranted && networkProviderEnabled -> LegacyProvider.NETWORK
            else -> null
        }
    }

}
