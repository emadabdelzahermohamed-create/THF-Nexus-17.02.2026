package com.topherofit.thf.pulse

object ActivityActivationGate {
    fun shouldActivate(
        mode: ActivityMode,
        gpsDisplacementMetres: Double,
        measuredStepDelta: Int,
        acceptedGpsPoints: Int,
        gpsDurationMs: Long,
        worstGpsAccuracyMetres: Double,
    ): Boolean {
        if (!gpsDisplacementMetres.isFinite() || gpsDisplacementMetres < 0.0 || measuredStepDelta < 0) return false
        val gpsConfirmed = ActivityGpsMotionGate.confirmsMovement(
            mode = mode,
            displacementMetres = gpsDisplacementMetres,
            acceptedPointCount = acceptedGpsPoints,
            durationMs = gpsDurationMs,
            worstAccuracyMetres = worstGpsAccuracyMetres,
        )
        return when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> gpsConfirmed || measuredStepDelta >= 2
            ActivityMode.CYCLE -> gpsConfirmed
        }
    }
}
