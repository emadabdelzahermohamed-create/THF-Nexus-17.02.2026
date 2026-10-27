package com.topherofit.thf.pulse

import kotlin.math.max

/**
 * Conservative GPS-only movement confirmation. A single accurate-looking fix or a long sequence
 * of small stationary drifts is insufficient: activation needs sustained, plausible net movement
 * that exceeds the reported uncertainty of the endpoint fixes.
 */
object ActivityGpsMotionGate {
    private const val MIN_WALK_RUN_DISPLACEMENT_METRES = 8.0
    private const val MIN_CYCLE_DISPLACEMENT_METRES = 18.0
    private const val ACCURACY_MULTIPLIER = 2.5
    private const val MIN_ACCEPTED_POINTS = 3
    private const val MIN_DURATION_MS = 5_000L
    private const val MIN_SPEED_KPH = 1.5

    fun confirmsMovement(
        mode: ActivityMode,
        displacementMetres: Double,
        acceptedPointCount: Int,
        durationMs: Long,
        worstAccuracyMetres: Double,
    ): Boolean {
        if (!displacementMetres.isFinite() || displacementMetres < 0.0) return false
        if (acceptedPointCount < MIN_ACCEPTED_POINTS || durationMs < MIN_DURATION_MS) return false
        if (!worstAccuracyMetres.isFinite() || worstAccuracyMetres <= 0.0) return false

        val maxAccuracyMetres = when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> 25.0
            ActivityMode.CYCLE -> 40.0
        }
        if (worstAccuracyMetres > maxAccuracyMetres) return false

        val baseDisplacement = when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> MIN_WALK_RUN_DISPLACEMENT_METRES
            ActivityMode.CYCLE -> MIN_CYCLE_DISPLACEMENT_METRES
        }
        val requiredDisplacementMetres = max(baseDisplacement, worstAccuracyMetres * ACCURACY_MULTIPLIER)
        if (displacementMetres < requiredDisplacementMetres) return false

        val impliedSpeedKph = ActivityMetrics.averageSpeedKph(displacementMetres, durationMs)
        val maxSpeedKph = when (mode) {
            ActivityMode.WALK -> 13.0
            ActivityMode.RUN -> 32.0
            ActivityMode.CYCLE -> 85.0
        }
        return impliedSpeedKph.isFinite() && impliedSpeedKph >= MIN_SPEED_KPH && impliedSpeedKph <= maxSpeedKph
    }
}
