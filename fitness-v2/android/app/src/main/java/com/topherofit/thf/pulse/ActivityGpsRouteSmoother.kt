package com.topherofit.thf.pulse

import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * Bounded display-only smoothing for already quality-gated GPS route points.
 *
 * This helper never adds/removes points or changes timestamps, accuracy, or altitude. Do not use
 * its output to accumulate distance, speed, pace, calories, or activation evidence; those metrics
 * must continue to use the accepted raw fixes. Endpoints and corners are deliberately preserved.
 */
object ActivityGpsRouteSmoother {
    private const val EARTH_RADIUS_METRES = 6_371_000.0
    private const val MAX_NEIGHBOUR_GAP_MS = 10_000L
    private const val MAX_SHIFT_METRES = 3.0
    private const val MIN_SHIFT_METRES = 0.05
    private const val MIN_COS_LATITUDE = 1e-6

    fun smoothForDisplay(points: List<ActivityRoutePoint>, mode: ActivityMode): List<ActivityRoutePoint> {
        if (points.size < 3) return points.toList()

        val maximumAccuracyMetres = when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> 25.0
            ActivityMode.CYCLE -> 40.0
        }
        val result = points.toMutableList()

        for (index in 1 until points.lastIndex) {
            val previous = points[index - 1]
            val current = points[index]
            val next = points[index + 1]
            if (!isUsable(previous, maximumAccuracyMetres) ||
                !isUsable(current, maximumAccuracyMetres) ||
                !isUsable(next, maximumAccuracyMetres)
            ) continue

            val previousGapMs = current.elapsedMs - previous.elapsedMs
            val nextGapMs = next.elapsedMs - current.elapsedMs
            val totalGapMs = next.elapsedMs - previous.elapsedMs
            if (previousGapMs <= 0L || nextGapMs <= 0L ||
                previousGapMs > MAX_NEIGHBOUR_GAP_MS ||
                nextGapMs > MAX_NEIGHBOUR_GAP_MS ||
                totalGapMs > MAX_NEIGHBOUR_GAP_MS
            ) continue

            val latitudeRadians = Math.toRadians(current.latitude)
            val cosLatitude = cos(latitudeRadians)
            if (!cosLatitude.isFinite() || abs(cosLatitude) < MIN_COS_LATITUDE) continue

            // Predict the point at its actual monotonic timestamp, in a local tangent plane.
            // This avoids bias when GPS callback intervals are uneven.
            val fraction = previousGapMs.toDouble() / totalGapMs.toDouble()
            val previousOffset = offsetMetres(current, previous, cosLatitude)
            val nextOffset = offsetMetres(current, next, cosLatitude)
            val expectedEast = previousOffset.first + (nextOffset.first - previousOffset.first) * fraction
            val expectedNorth = previousOffset.second + (nextOffset.second - previousOffset.second) * fraction
            val deviationMetres = hypot(expectedEast, expectedNorth)

            val previousSigma = max(previous.accuracyMetres.toDouble(), 1.0)
            val currentSigma = max(current.accuracyMetres.toDouble(), 1.0)
            val nextSigma = max(next.accuracyMetres.toDouble(), 1.0)
            val expectedSigma = sqrt(
                (1.0 - fraction) * (1.0 - fraction) * previousSigma * previousSigma +
                    fraction * fraction * nextSigma * nextSigma,
            )

            // A large departure is more likely a real corner or discontinuity than small jitter.
            // Bound the corner test and the actual correction independently.
            val cornerThresholdMetres = max(4.0, min(8.0, 1.5 * (currentSigma + expectedSigma)))
            if (!deviationMetres.isFinite() || deviationMetres > cornerThresholdMetres) continue

            val currentVariance = currentSigma * currentSigma
            val expectedVariance = expectedSigma * expectedSigma
            val confidenceFraction = currentVariance / (currentVariance + expectedVariance)
            var correctionEast = expectedEast * confidenceFraction
            var correctionNorth = expectedNorth * confidenceFraction
            val correctionMetres = hypot(correctionEast, correctionNorth)
            val maximumShift = min(MAX_SHIFT_METRES, currentSigma * 0.5)
            if (!correctionMetres.isFinite() || correctionMetres < MIN_SHIFT_METRES) continue
            if (correctionMetres > maximumShift) {
                val scale = maximumShift / correctionMetres
                correctionEast *= scale
                correctionNorth *= scale
            }

            val latitude = current.latitude + Math.toDegrees(correctionNorth / EARTH_RADIUS_METRES)
            val longitudeDelta = Math.toDegrees(correctionEast / (EARTH_RADIUS_METRES * cosLatitude))
            val longitude = normalizeLongitude(current.longitude + longitudeDelta)
            if (latitude.isFinite() && latitude in -90.0..90.0 && longitude.isFinite()) {
                result[index] = current.copy(latitude = latitude, longitude = longitude)
            }
        }

        return result.toList()
    }

    private fun isUsable(point: ActivityRoutePoint, maximumAccuracyMetres: Double): Boolean =
        point.latitude.isFinite() && point.latitude in -90.0..90.0 &&
            point.longitude.isFinite() && point.longitude in -180.0..180.0 &&
            point.accuracyMetres.isFinite() && point.accuracyMetres > 0f &&
            point.accuracyMetres <= maximumAccuracyMetres &&
            point.elapsedMs >= 0L

    /** Returns east/north metres from origin to target, with longitude wrap at the date line. */
    private fun offsetMetres(
        origin: ActivityRoutePoint,
        target: ActivityRoutePoint,
        cosOriginLatitude: Double,
    ): Pair<Double, Double> {
        val longitudeDelta = normalizeLongitudeDelta(target.longitude - origin.longitude)
        val east = Math.toRadians(longitudeDelta) * EARTH_RADIUS_METRES * cosOriginLatitude
        val north = Math.toRadians(target.latitude - origin.latitude) * EARTH_RADIUS_METRES
        return east to north
    }

    private fun normalizeLongitudeDelta(delta: Double): Double {
        var normalized = delta
        if (normalized > 180.0) normalized -= 360.0
        if (normalized < -180.0) normalized += 360.0
        return normalized
    }

    private fun normalizeLongitude(longitude: Double): Double {
        var normalized = (longitude + 180.0) % 360.0
        if (normalized < 0.0) normalized += 360.0
        return normalized - 180.0
    }
}
