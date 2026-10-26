package com.topherofit.thf.pulse

import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt

enum class ActivityMode(val wireName: String, val usesSteps: Boolean, val met: Double) {
    WALK("walk", true, 3.5),
    RUN("run", true, 7.9),
    CYCLE("cycle", false, 6.8);

    companion object {
        fun fromWire(value: String?): ActivityMode? = entries.firstOrNull {
            it.wireName.equals(value?.trim(), ignoreCase = true)
        }
    }
}

data class ActivityRoutePoint(
    val latitude: Double,
    val longitude: Double,
    val altitudeMetres: Double?,
    val accuracyMetres: Float,
    val elapsedMs: Long,
)

data class ActivitySnapshot(
    val active: Boolean,
    val mode: ActivityMode?,
    val startedAtWallMs: Long,
    val elapsedMs: Long,
    val distanceMetres: Double,
    val stepDelta: Int,
    val currentSpeedKph: Double,
    val averageSpeedKph: Double,
    val paceMinutesPerKm: Double?,
    val estimatedCaloriesKcal: Double,
    val gpsPointCount: Int,
    val lastAccuracyMetres: Float?,
    val route: List<ActivityRoutePoint>,
    val phase: ActivitySessionPhase = ActivitySessionPhase.ARMED,
    val gpsFixState: String = "acquiring",
    val observedAccuracyMetres: Float? = null,
)

object ActivityMetrics {
    private const val EARTH_RADIUS_M = 6_371_000.0

    fun distanceMetres(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        if (!validCoordinate(lat1, lon1) || !validCoordinate(lat2, lon2)) return 0.0
        val p1 = Math.toRadians(lat1)
        val p2 = Math.toRadians(lat2)
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val a = sin(dLat / 2).pow(2.0) + cos(p1) * cos(p2) * sin(dLon / 2).pow(2.0)
        return 2.0 * EARTH_RADIUS_M * asin(min(1.0, sqrt(max(0.0, a))))
    }

    fun averageSpeedKph(distanceMetres: Double, durationMs: Long): Double {
        if (!distanceMetres.isFinite() || durationMs <= 0L || distanceMetres <= 0.0) return 0.0
        return (distanceMetres / 1000.0) / (durationMs / 3_600_000.0)
    }

    fun paceMinutesPerKm(distanceMetres: Double, durationMs: Long): Double? {
        if (!distanceMetres.isFinite() || distanceMetres < 10.0 || durationMs <= 0L) return null
        return (durationMs / 60_000.0) / (distanceMetres / 1000.0)
    }

    fun estimatedCalories(mode: ActivityMode, weightKg: Double, durationMs: Long): Double {
        // Calories are an estimate only when the inputs are real and usable. In particular,
        // never turn a missing/invalid weight (NaN/Infinity) into a fabricated calorie value.
        if (!weightKg.isFinite() || durationMs <= 0L) return 0.0
        val safeWeight = weightKg.coerceIn(30.0, 250.0)
        val minutes = durationMs / 60_000.0
        return mode.met * 3.5 * safeWeight / 200.0 * minutes
    }

    private fun validCoordinate(latitude: Double, longitude: Double): Boolean =
        latitude.isFinite() && longitude.isFinite() && latitude in -90.0..90.0 && longitude in -180.0..180.0
}
