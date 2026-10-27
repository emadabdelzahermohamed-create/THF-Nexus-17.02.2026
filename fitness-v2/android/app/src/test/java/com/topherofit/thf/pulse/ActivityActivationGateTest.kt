package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class ActivityActivationGateTest {
    private fun activates(
        mode: ActivityMode,
        displacement: Double,
        steps: Int = 0,
        points: Int = 3,
        durationMs: Long = 5_000L,
        accuracy: Double = 5.0,
    ) = ActivityActivationGate.shouldActivate(
        mode = mode,
        gpsDisplacementMetres = displacement,
        measuredStepDelta = steps,
        acceptedGpsPoints = points,
        gpsDurationMs = durationMs,
        worstGpsAccuracyMetres = accuracy,
    )

    @Test fun staysArmedForStationaryOrUncertainGps() {
        assertFalse(activates(ActivityMode.WALK, displacement = 4.0, points = 12, durationMs = 30_000L))
        assertFalse(activates(ActivityMode.RUN, displacement = 7.0, points = 12, durationMs = 30_000L))
        assertFalse(activates(ActivityMode.CYCLE, displacement = 17.99))
    }

    @Test fun walkingAndRunningActivateFromMeasuredStepsOrValidatedGpsMotion() {
        assertTrue(activates(ActivityMode.WALK, displacement = 0.0, steps = 2, points = 0, durationMs = 0L, accuracy = Double.NaN))
        assertTrue(activates(ActivityMode.WALK, displacement = 12.5))
        assertTrue(activates(ActivityMode.RUN, displacement = 20.0))
        assertFalse(activates(ActivityMode.RUN, displacement = 20.0, points = 2))
    }

    @Test fun cyclingRequiresValidatedGpsMovementAndNeverStepsAlone() {
        assertFalse(activates(ActivityMode.CYCLE, displacement = 0.0, steps = 20, points = 0, durationMs = 0L, accuracy = Double.NaN))
        assertFalse(activates(ActivityMode.CYCLE, displacement = 18.0, points = 2))
        assertTrue(activates(ActivityMode.CYCLE, displacement = 18.0))
    }

    @Test fun rejectsNonFiniteOrNegativeDistanceEvidence() {
        for (distance in listOf(-1.0, Double.NaN, Double.POSITIVE_INFINITY)) {
            assertFalse(activates(ActivityMode.WALK, displacement = distance, steps = 0))
        }
        assertFalse(activates(ActivityMode.WALK, displacement = 0.0, steps = -1))
    }
}
