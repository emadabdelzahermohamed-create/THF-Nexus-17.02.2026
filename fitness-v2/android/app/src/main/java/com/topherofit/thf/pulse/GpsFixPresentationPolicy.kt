package com.topherofit.thf.pulse

/**
 * Distinguishes a fresh location observation from a fix accepted for route/distance metrics.
 * A fresh fix can be rejected by movement, accuracy, mock, or jump filters without its reported
 * horizontal accuracy being intrinsically poor. The UI must not label every rejected fix "weak".
 */
object GpsFixPresentationPolicy {
    const val MAX_OBSERVED_AGE_MS = 30_000L

    fun state(
        locationPermissionGranted: Boolean,
        providerEnabled: Boolean,
        observedElapsedMs: Long?,
        acceptedElapsedMs: Long?,
        nowElapsedMs: Long,
    ): String {
        if (!locationPermissionGranted) return "permission"
        if (!providerEnabled) return "off"
        val observed = observedElapsedMs ?: return "acquiring"
        val observedAgeMs = nowElapsedMs - observed
        if (observedAgeMs < 0L || observedAgeMs > MAX_OBSERVED_AGE_MS) return "stale"
        if (acceptedElapsedMs == null || acceptedElapsedMs < observed) return "filtered"
        return "ready"
    }
}


/** Exposes current accuracy only while a fresh accepted fix is available. */
object GpsAccuracyPresentationPolicy {
    fun visibleAccuracy(gpsFixState: String, acceptedAccuracyMetres: Float?): Float? {
        if (gpsFixState != "ready") return null
        return acceptedAccuracyMetres?.takeIf { it.isFinite() && it > 0f }
    }
}
