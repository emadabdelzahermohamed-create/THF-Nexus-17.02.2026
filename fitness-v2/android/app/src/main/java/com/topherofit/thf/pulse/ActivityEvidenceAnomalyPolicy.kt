package com.topherofit.thf.pulse

import java.util.Locale
import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.sin
import kotlin.math.sqrt

/** Sports whose GPS segments can contribute to an outdoor activity record. */
enum class ActivityEvidenceSport { WALKING, RUNNING, CYCLING }

enum class ActivityGpsSegmentDecision {
    CREDITABLE,
    NO_MEASURABLE_MOVEMENT,
    EXCLUDE_MOCK_LOCATION,
    EXCLUDE_MISSING_SOURCE,
    EXCLUDE_SOURCE_CHANGE,
    EXCLUDE_INVALID_COORDINATES,
    EXCLUDE_NON_MONOTONIC_TIME,
    EXCLUDE_LONG_GAP,
    EXCLUDE_POOR_ACCURACY,
    EXCLUDE_IMPLAUSIBLE_SPEED,
}

/** A raw provider fix. Use elapsed-realtime time and preserve the actual provider label. */
data class ActivityGpsFix(
    val elapsedRealtimeNanos: Long,
    val latitude: Double,
    val longitude: Double,
    val horizontalAccuracyMeters: Double,
    val sourceLabel: String?,
    val mockLocation: Boolean = false,
)

data class ActivityGpsSegmentAssessment(
    val decision: ActivityGpsSegmentDecision,
    val sourceLabel: String?,
    val observedDistanceMeters: Double? = null,
    val uncertaintyAdjustedDistanceMeters: Double? = null,
    val conservativeSpeedMetersPerSecond: Double? = null,
) {
    /** Distance eligible for downstream totals; excluded or unmeasurable segments contribute zero. */
    val creditableDistanceMeters: Double
        get() = if (decision == ActivityGpsSegmentDecision.CREDITABLE) {
            uncertaintyAdjustedDistanceMeters ?: 0.0
        } else {
            0.0
        }
}

/**
 * Conservative, deterministic anomaly gate for a pair of raw GPS fixes.
 *
 * The caller must supply actual provider metadata, coordinates, horizontal accuracy, the OS mock
 * location signal, and monotonic elapsed-realtime timestamps. This policy does not create sensor
 * evidence, authenticate a provider, or prove that an activity is genuine. A passing segment is
 * only plausible enough for downstream reconciliation; excluded segments are not accusations.
 * Never pass display-smoothed points here. Do not credit excluded segments to distance, pace, or
 * competition progress.
 */
object ActivityEvidenceAnomalyPolicy {
    const val MAX_FIX_GAP_NANOS = 120_000_000_000L
    const val MAX_HORIZONTAL_ACCURACY_METERS = 50.0
    const val MIN_CREDITABLE_DISTANCE_METERS = 3.0
    private const val EARTH_RADIUS_METERS = 6_371_000.0

    fun assessSegment(
        sport: ActivityEvidenceSport,
        previous: ActivityGpsFix,
        current: ActivityGpsFix,
    ): ActivityGpsSegmentAssessment {
        val currentSource = current.sourceLabel?.trim()?.takeIf { it.isNotEmpty() }
        fun result(
            decision: ActivityGpsSegmentDecision,
            observedDistanceMeters: Double? = null,
            adjustedDistanceMeters: Double? = null,
            speedMetersPerSecond: Double? = null,
        ) = ActivityGpsSegmentAssessment(
            decision = decision,
            sourceLabel = currentSource,
            observedDistanceMeters = observedDistanceMeters,
            uncertaintyAdjustedDistanceMeters = adjustedDistanceMeters,
            conservativeSpeedMetersPerSecond = speedMetersPerSecond,
        )

        if (previous.mockLocation || current.mockLocation) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_MOCK_LOCATION)
        }
        val previousSource = previous.sourceLabel?.trim()?.takeIf { it.isNotEmpty() }
        if (previousSource == null || currentSource == null) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_MISSING_SOURCE)
        }
        if (previousSource.lowercase(Locale.ROOT) != currentSource.lowercase(Locale.ROOT)) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_SOURCE_CHANGE)
        }
        if (!isValidCoordinate(previous.latitude, previous.longitude) ||
            !isValidCoordinate(current.latitude, current.longitude)
        ) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_INVALID_COORDINATES)
        }
        if (previous.elapsedRealtimeNanos < 0L || current.elapsedRealtimeNanos <= previous.elapsedRealtimeNanos) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_NON_MONOTONIC_TIME)
        }
        val gapNanos = current.elapsedRealtimeNanos - previous.elapsedRealtimeNanos
        if (gapNanos > MAX_FIX_GAP_NANOS) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_LONG_GAP)
        }
        if (!isValidAccuracy(previous.horizontalAccuracyMeters) ||
            !isValidAccuracy(current.horizontalAccuracyMeters)
        ) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_POOR_ACCURACY)
        }

        val observedDistance = haversineMeters(previous, current)
        if (!observedDistance.isFinite()) {
            return result(ActivityGpsSegmentDecision.EXCLUDE_INVALID_COORDINATES)
        }
        val uncertaintyRadius = previous.horizontalAccuracyMeters + current.horizontalAccuracyMeters
        val adjustedDistance = max(0.0, observedDistance - uncertaintyRadius)
        val gapSeconds = gapNanos / 1_000_000_000.0
        val conservativeSpeed = adjustedDistance / gapSeconds
        if (!conservativeSpeed.isFinite() || conservativeSpeed > maxPlausibleSpeedMetersPerSecond(sport)) {
            return result(
                ActivityGpsSegmentDecision.EXCLUDE_IMPLAUSIBLE_SPEED,
                observedDistance,
                adjustedDistance,
                conservativeSpeed,
            )
        }
        if (adjustedDistance < MIN_CREDITABLE_DISTANCE_METERS) {
            return result(
                ActivityGpsSegmentDecision.NO_MEASURABLE_MOVEMENT,
                observedDistance,
                adjustedDistance,
                conservativeSpeed,
            )
        }
        return result(
            ActivityGpsSegmentDecision.CREDITABLE,
            observedDistance,
            adjustedDistance,
            conservativeSpeed,
        )
    }

    private fun isValidCoordinate(latitude: Double, longitude: Double): Boolean =
        latitude.isFinite() && latitude in -90.0..90.0 &&
            longitude.isFinite() && longitude in -180.0..180.0

    private fun isValidAccuracy(accuracyMeters: Double): Boolean =
        accuracyMeters.isFinite() && accuracyMeters > 0.0 &&
            accuracyMeters <= MAX_HORIZONTAL_ACCURACY_METERS

    private fun maxPlausibleSpeedMetersPerSecond(sport: ActivityEvidenceSport): Double = when (sport) {
        ActivityEvidenceSport.WALKING -> 4.5
        ActivityEvidenceSport.RUNNING -> 12.5
        ActivityEvidenceSport.CYCLING -> 45.0
    }

    private fun haversineMeters(a: ActivityGpsFix, b: ActivityGpsFix): Double {
        val latitudeA = Math.toRadians(a.latitude)
        val latitudeB = Math.toRadians(b.latitude)
        val latitudeDelta = latitudeB - latitudeA
        val longitudeDelta = Math.toRadians(normalizeLongitudeDelta(b.longitude - a.longitude))
        val sinLatitude = sin(latitudeDelta / 2.0)
        val sinLongitude = sin(longitudeDelta / 2.0)
        val haversine = (sinLatitude * sinLatitude +
            cos(latitudeA) * cos(latitudeB) * sinLongitude * sinLongitude).coerceIn(0.0, 1.0)
        return 2.0 * EARTH_RADIUS_METERS * asin(sqrt(haversine))
    }

    private fun normalizeLongitudeDelta(delta: Double): Double = when {
        delta > 180.0 -> delta - 360.0
        delta < -180.0 -> delta + 360.0
        else -> delta
    }
}
