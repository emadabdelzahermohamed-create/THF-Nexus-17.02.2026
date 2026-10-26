package com.topherofit.thf.pulse

import org.junit.Assert.*
import org.junit.Test

class ActivityActivationGateTest {
    @Test fun staysArmedWithoutMeasuredMovement() {
        assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.WALK, acceptedGpsMetres = 0.0, measuredStepDelta = 0, acceptedGpsPoints = 1))
        assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.RUN, acceptedGpsMetres = 1.9, measuredStepDelta = 0, acceptedGpsPoints = 2))
        assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.CYCLE, acceptedGpsMetres = 4.9, measuredStepDelta = 0, acceptedGpsPoints = 2))
    }

    @Test fun walkingAndRunningActivateFromMeasuredStepsOrValidatedGpsMovement() {
        assertTrue(ActivityActivationGate.shouldActivate(ActivityMode.WALK, acceptedGpsMetres = 0.0, measuredStepDelta = 2, acceptedGpsPoints = 0))
        assertTrue(ActivityActivationGate.shouldActivate(ActivityMode.RUN, acceptedGpsMetres = 3.0, measuredStepDelta = 0, acceptedGpsPoints = 2))
    }

    @Test fun cyclingRequiresValidatedGpsMovement() {
        assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.CYCLE, acceptedGpsMetres = 0.0, measuredStepDelta = 20, acceptedGpsPoints = 0))
        assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.CYCLE, acceptedGpsMetres = 5.0, measuredStepDelta = 0, acceptedGpsPoints = 1))
        assertTrue(ActivityActivationGate.shouldActivate(ActivityMode.CYCLE, acceptedGpsMetres = 5.0, measuredStepDelta = 0, acceptedGpsPoints = 2))
    }

    @Test fun rejectsNonFiniteOrNegativeDistanceEvidence() {
        for (distance in listOf(-1.0, Double.NaN, Double.POSITIVE_INFINITY)) {
            assertFalse(ActivityActivationGate.shouldActivate(ActivityMode.WALK, distance, 0, 2))
        }
    }
}
