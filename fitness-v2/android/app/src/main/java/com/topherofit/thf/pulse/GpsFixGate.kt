package com.topherofit.thf.pulse

data class GpsFix(
    val latitude: Double,
    val longitude: Double,
    val accuracyMetres: Double,
    val elapsedMs: Long,
    val mock: Boolean,
    val speedMps: Double?,
)

object GpsFixGate {
    fun accepts(fix: GpsFix, previous: GpsFix?, mode: ActivityMode, sessionStartedMs: Long, nowMs: Long): Boolean {
        if (fix.mock || !fix.accuracyMetres.isFinite() || fix.accuracyMetres <= 0.0 || fix.accuracyMetres > 80.0) return false
        if (!fix.latitude.isFinite() || fix.latitude !in -90.0..90.0 ||
            !fix.longitude.isFinite() || fix.longitude !in -180.0..180.0) return false
        if (fix.elapsedMs < sessionStartedMs || fix.elapsedMs > nowMs || nowMs - fix.elapsedMs > 30_000L) return false
        val maxKph = when (mode) {
            ActivityMode.WALK -> 13.0
            ActivityMode.RUN -> 32.0
            ActivityMode.CYCLE -> 85.0
        }
        fix.speedMps?.let { if (!it.isFinite() || it < 0.0 || it * 3.6 > maxKph) return false }
        if (previous != null) {
            if (fix.elapsedMs <= previous.elapsedMs) return false
            val distance = ActivityMetrics.distanceMetres(previous.latitude, previous.longitude, fix.latitude, fix.longitude)
            if (ActivityMetrics.averageSpeedKph(distance, fix.elapsedMs - previous.elapsedMs) > maxKph) return false
        }
        return true
    }
}
