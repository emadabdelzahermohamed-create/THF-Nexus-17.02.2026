package com.topherofit.thf.pulse

object ActivityStepActivationPolicy {
    const val MIN_STEP_DELTA = 4
    const val MIN_WINDOW_MS = 5_000L
    const val MAX_WINDOW_MS = 15_000L
    private const val MAX_CADENCE_SPM = 240.0

    fun confirmedSteps(stepDeltaInWindow: Int, windowDurationMs: Long): Int? {
        if (stepDeltaInWindow < MIN_STEP_DELTA) return null
        if (windowDurationMs !in MIN_WINDOW_MS..MAX_WINDOW_MS) return null
        val cadenceSpm = stepDeltaInWindow.toDouble() * 60_000.0 / windowDurationMs.toDouble()
        if (!cadenceSpm.isFinite() || cadenceSpm > MAX_CADENCE_SPM) return null
        return stepDeltaInWindow
    }
}

object ActivityActivationGate {
    fun shouldActivate(
        mode: ActivityMode,
        gpsDisplacementMetres: Double,
        stepEvidenceDelta: Int,
        stepEvidenceDurationMs: Long,
        acceptedGpsPoints: Int,
        gpsDurationMs: Long,
        worstGpsAccuracyMetres: Double,
    ): Boolean {
        if (!gpsDisplacementMetres.isFinite() || gpsDisplacementMetres < 0.0 ||
            stepEvidenceDelta < 0 || stepEvidenceDurationMs < 0L
        ) return false
        val gpsConfirmed = ActivityGpsMotionGate.confirmsMovement(
            mode = mode,
            displacementMetres = gpsDisplacementMetres,
            acceptedPointCount = acceptedGpsPoints,
            durationMs = gpsDurationMs,
            worstAccuracyMetres = worstGpsAccuracyMetres,
        )
        val stepsConfirmed = ActivityStepActivationPolicy.confirmedSteps(
            stepEvidenceDelta,
            stepEvidenceDurationMs,
        ) != null
        return when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> gpsConfirmed || stepsConfirmed
            ActivityMode.CYCLE -> gpsConfirmed
        }
    }
}
