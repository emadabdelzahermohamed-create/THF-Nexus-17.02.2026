package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivitySnapshotPolicyTest {
    private val route = listOf(
        ActivityRoutePoint(30.0444, 31.2357, null, 8f, 1_000L),
        ActivityRoutePoint(30.0445, 31.2358, null, 7f, 2_000L),
    )

    @Test
    fun armedSessionHidesMovementMetricsUntilMeasuredActivation() {
        val snapshot = ActivitySnapshotPolicy.build(
            sessionActive = true,
            phase = ActivitySessionPhase.ARMED,
            mode = ActivityMode.WALK,
            armedStartedAtWallMs = 1_000L,
            activatedAtWallMs = null,
            activatedAtElapsedMs = null,
            nowElapsedMs = 20_000L,
            measuredDistanceMetres = 8.0,
            measuredStepDelta = 1,
            currentSpeedKph = 4.5,
            weightKg = 70.0,
            acceptedRoute = route,
            lastAccuracyMetres = 7f,
        )

        assertTrue(snapshot.active)
        assertEquals(ActivitySessionPhase.ARMED, snapshot.phase)
        assertEquals(0L, snapshot.elapsedMs)
        assertEquals(0.0, snapshot.distanceMetres, 0.0)
        assertEquals(0, snapshot.stepDelta)
        assertEquals(0.0, snapshot.currentSpeedKph, 0.0)
        assertEquals(0.0, snapshot.averageSpeedKph, 0.0)
        assertNull(snapshot.paceMinutesPerKm)
        assertEquals(0.0, snapshot.estimatedCaloriesKcal, 0.0)
        assertEquals(0, snapshot.gpsPointCount)
        assertEquals(7f, snapshot.lastAccuracyMetres)
        assertTrue(snapshot.route.isEmpty())
    }

    @Test
    fun activeSessionExposesOnlyMeasuredMetricsFromActivationTime() {
        val snapshot = ActivitySnapshotPolicy.build(
            sessionActive = true,
            phase = ActivitySessionPhase.ACTIVE,
            mode = ActivityMode.RUN,
            armedStartedAtWallMs = 1_000L,
            activatedAtWallMs = 2_000L,
            activatedAtElapsedMs = 5_000L,
            nowElapsedMs = 65_000L,
            measuredDistanceMetres = 1_000.0,
            measuredStepDelta = 120,
            currentSpeedKph = 10.0,
            weightKg = 70.0,
            acceptedRoute = route,
            lastAccuracyMetres = 7f,
        )

        assertTrue(snapshot.active)
        assertEquals(ActivitySessionPhase.ACTIVE, snapshot.phase)
        assertEquals(2_000L, snapshot.startedAtWallMs)
        assertEquals(60_000L, snapshot.elapsedMs)
        assertEquals(1_000.0, snapshot.distanceMetres, 0.0)
        assertEquals(120, snapshot.stepDelta)
        assertEquals(10.0, snapshot.currentSpeedKph, 0.0)
        assertTrue(snapshot.averageSpeedKph > 0.0)
        assertTrue(snapshot.estimatedCaloriesKcal > 0.0)
        assertEquals(route, snapshot.route)
    }

    @Test
    fun inconsistentActivePhaseFailsClosedAsArmedPresentation() {
        val snapshot = ActivitySnapshotPolicy.build(
            sessionActive = true,
            phase = ActivitySessionPhase.ACTIVE,
            mode = ActivityMode.CYCLE,
            armedStartedAtWallMs = 1_000L,
            activatedAtWallMs = null,
            activatedAtElapsedMs = null,
            nowElapsedMs = 65_000L,
            measuredDistanceMetres = 50.0,
            measuredStepDelta = 0,
            currentSpeedKph = 12.0,
            weightKg = 70.0,
            acceptedRoute = route,
            lastAccuracyMetres = 7f,
        )

        assertEquals(ActivitySessionPhase.ARMED, snapshot.phase)
        assertEquals(0L, snapshot.elapsedMs)
        assertEquals(0.0, snapshot.distanceMetres, 0.0)
        assertFalse(snapshot.route.isNotEmpty())
    }
}
