package com.topherofit.thf.pulse

import kotlin.math.max

data class ActivityGpsActivationWindow(
    val firstPoint: ActivityRoutePoint,
    val lastPoint: ActivityRoutePoint,
    val displacementMetres: Double,
    val durationMs: Long,
    val worstAccuracyMetres: Double,
    val pointCount: Int,
)

/**
 * Finds the shortest recent, quality-qualified movement window.
 *
 * Earlier ARMED fixes are warm-up evidence, not workout time. Choosing the newest qualifying
 * suffix prevents a long stationary warm-up from dragging the activation timestamp backwards.
 * Accuracy is evaluated across every fix in the candidate window, not just its endpoints.
 */
object ActivityGpsActivationWindowPolicy {
    fun select(
        points: List<ActivityRoutePoint>,
        mode: ActivityMode,
    ): ActivityGpsActivationWindow? {
        if (points.size < 3) return null
        if (points.any { point ->
                !point.latitude.isFinite() || point.latitude !in -90.0..90.0 ||
                    !point.longitude.isFinite() || point.longitude !in -180.0..180.0 ||
                    !point.accuracyMetres.isFinite() || point.accuracyMetres <= 0f ||
                    point.elapsedMs < 0L
            }
        ) return null

        for (index in 1 until points.size) {
            if (points[index].elapsedMs <= points[index - 1].elapsedMs) return null
        }

        val lastIndex = points.lastIndex
        val last = points[lastIndex]
        var worstAccuracyMetres = last.accuracyMetres.toDouble()

        // Walk backwards so the first accepted candidate is the shortest recent window.
        for (startIndex in (lastIndex - 1) downTo 0) {
            val first = points[startIndex]
            worstAccuracyMetres = max(worstAccuracyMetres, first.accuracyMetres.toDouble())
            val pointCount = lastIndex - startIndex + 1
            if (pointCount < 3) continue

            val durationMs = last.elapsedMs - first.elapsedMs
            val displacementMetres = ActivityMetrics.distanceMetres(
                first.latitude,
                first.longitude,
                last.latitude,
                last.longitude,
            )
            if (ActivityGpsMotionGate.confirmsMovement(
                    mode = mode,
                    displacementMetres = displacementMetres,
                    acceptedPointCount = pointCount,
                    durationMs = durationMs,
                    worstAccuracyMetres = worstAccuracyMetres,
                )
            ) {
                return ActivityGpsActivationWindow(
                    firstPoint = first,
                    lastPoint = last,
                    displacementMetres = displacementMetres,
                    durationMs = durationMs,
                    worstAccuracyMetres = worstAccuracyMetres,
                    pointCount = pointCount,
                )
            }
        }
        return null
    }
}
