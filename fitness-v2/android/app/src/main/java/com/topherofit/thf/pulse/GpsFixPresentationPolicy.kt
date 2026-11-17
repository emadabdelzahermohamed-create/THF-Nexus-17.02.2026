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
        locationServicesEnabled: Boolean,
        observedElapsedMs: Long?,
        acceptedElapsedMs: Long?,
        nowElapsedMs: Long,
    ): String {
        if (!locationPermissionGranted) return "permission"
        if (!locationServicesEnabled) return "off"
        val observed = observedElapsedMs ?: return "acquiring"
        val observedAgeMs = nowElapsedMs - observed
        if (observedAgeMs < 0L || observedAgeMs > MAX_OBSERVED_AGE_MS) return "stale"
        if (acceptedElapsedMs == null || acceptedElapsedMs < observed) return "filtered"
        return "ready"
    }

    /** Describes the raw Android location source without calling every fix "GPS". */
    fun sourceLabel(provider: String?): String = when {
        provider.equals("gps", ignoreCase = true) -> "GPS"
        provider.equals("network", ignoreCase = true) -> "الشبكة"
        provider.equals("fused", ignoreCase = true) -> "الموقع المدمج"
        else -> "الموقع"
    }
}

/** Exposes current accuracy only while a fresh accepted fix is available. */
object GpsAccuracyPresentationPolicy {
    fun visibleAccuracy(gpsFixState: String, acceptedAccuracyMetres: Float?): Float? {
        if (gpsFixState != "ready") return null
        return acceptedAccuracyMetres?.takeIf { it.isFinite() && it > 0f }
    }

    fun formatAccuracyMetres(accuracyMetres: Float?): String {
        val accuracy = accuracyMetres?.takeIf { it.isFinite() && it > 0f } ?: return "غير متاحة"
        return if (accuracy < 1f) "±<1 م" else "±${kotlin.math.ceil(accuracy.toDouble()).toInt()} م"
    }
}
