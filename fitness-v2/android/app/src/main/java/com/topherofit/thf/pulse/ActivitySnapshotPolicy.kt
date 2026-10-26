package com.topherofit.thf.pulse

import kotlin.math.max

enum class ActivitySessionPhase(val wireName: String) {
    ARMED("armed"),
    ACTIVE("active"),
}

object ActivitySnapshotPolicy {
    fun build(
        sessionActive: Boolean,
        phase: ActivitySessionPhase,
        mode: ActivityMode,
        armedStartedAtWallMs: Long,
        activatedAtWallMs: Long?,
        activatedAtElapsedMs: Long?,
        nowElapsedMs: Long,
        measuredDistanceMetres: Double,
        measuredStepDelta: Int,
        currentSpeedKph: Double,
        weightKg: Double,
        acceptedRoute: List<ActivityRoutePoint>,
        lastAccuracyMetres: Float?,
    ): ActivitySnapshot {
        val activated = phase == ActivitySessionPhase.ACTIVE &&
            activatedAtWallMs != null && activatedAtWallMs > 0L &&
            activatedAtElapsedMs != null && activatedAtElapsedMs > 0L &&
            nowElapsedMs >= activatedAtElapsedMs
        val effectivePhase = if (activated) ActivitySessionPhase.ACTIVE else ActivitySessionPhase.ARMED
        if (!activated) {
            return ActivitySnapshot(
                active = sessionActive,
                phase = effectivePhase,
                mode = mode,
                startedAtWallMs = armedStartedAtWallMs,
                elapsedMs = 0L,
                distanceMetres = 0.0,
                stepDelta = 0,
                currentSpeedKph = 0.0,
                averageSpeedKph = 0.0,
                paceMinutesPerKm = null,
                estimatedCaloriesKcal = 0.0,
                gpsPointCount = acceptedRoute.size,
                lastAccuracyMetres = lastAccuracyMetres,
                route = emptyList(),
            )
        }

        val activationWallMs = requireNotNull(activatedAtWallMs)
        val activationElapsedMs = requireNotNull(activatedAtElapsedMs)
        val elapsedMs = max(0L, nowElapsedMs - activationElapsedMs)
        val safeDistance = measuredDistanceMetres.takeIf { it.isFinite() && it >= 0.0 } ?: 0.0
        val safeSteps = max(0, measuredStepDelta)
        val safeCurrentSpeed = currentSpeedKph.takeIf { it.isFinite() && it >= 0.0 } ?: 0.0
        return ActivitySnapshot(
            active = sessionActive,
            phase = ActivitySessionPhase.ACTIVE,
            mode = mode,
            startedAtWallMs = activationWallMs,
            elapsedMs = elapsedMs,
            distanceMetres = safeDistance,
            stepDelta = if (mode.usesSteps) safeSteps else 0,
            currentSpeedKph = safeCurrentSpeed,
            averageSpeedKph = ActivityMetrics.averageSpeedKph(safeDistance, elapsedMs),
            paceMinutesPerKm = if (mode == ActivityMode.CYCLE) null else ActivityMetrics.paceMinutesPerKm(safeDistance, elapsedMs),
            estimatedCaloriesKcal = ActivityMetrics.estimatedCalories(mode, weightKg, elapsedMs),
            gpsPointCount = acceptedRoute.size,
            lastAccuracyMetres = lastAccuracyMetres,
            route = acceptedRoute,
        )
    }
}
