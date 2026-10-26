package com.topherofit.thf.pulse

/**
 * Truth gate between a requested activity session (ARMED) and measured movement (ACTIVE).
 * This class only decides whether sufficient measured evidence exists; callers remain responsible
 * for withholding distance/calories/pace/session steps until activation and for GPS quality gating.
 */
object ActivityActivationGate {
    private const val WALK_RUN_MIN_GPS_METRES = 3.0
    private const val CYCLE_MIN_GPS_METRES = 5.0
    private const val WALK_RUN_MIN_STEPS = 2
    private const val MIN_GPS_POINTS = 2

    fun shouldActivate(
        mode: ActivityMode,
        acceptedGpsMetres: Double,
        measuredStepDelta: Int,
        acceptedGpsPoints: Int,
    ): Boolean {
        if (!acceptedGpsMetres.isFinite() || acceptedGpsMetres < 0.0) return false
        val gpsConfirmed = acceptedGpsPoints >= MIN_GPS_POINTS && acceptedGpsMetres >= when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> WALK_RUN_MIN_GPS_METRES
            ActivityMode.CYCLE -> CYCLE_MIN_GPS_METRES
        }
        return when (mode) {
            ActivityMode.WALK, ActivityMode.RUN -> gpsConfirmed || measuredStepDelta >= WALK_RUN_MIN_STEPS
            ActivityMode.CYCLE -> gpsConfirmed
        }
    }
}
