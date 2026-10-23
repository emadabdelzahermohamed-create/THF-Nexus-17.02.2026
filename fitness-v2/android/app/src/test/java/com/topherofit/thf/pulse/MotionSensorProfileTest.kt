package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class MotionSensorProfileTest {
    @Test
    fun jumpUsesImpactSensorsWithoutStepMetrics() {
        val profile = MotionSensorProfileResolver.forExercise(movementId = "jump", category = "plyometrics")
        assertEquals(MotionSensorProfile.IMPACT_JUMP, profile)
        assertTrue(profile.accelerometer)
        assertTrue(profile.gyroscope)
        assertFalse(profile.stepCounter)
        assertFalse(profile.stepDetector)
        assertFalse(profile.showStepMetrics)
    }

    @Test
    fun staticHoldUsesStabilitySensorsWithoutStepMetrics() {
        val profile = MotionSensorProfileResolver.forExercise(movementId = "isometric", category = "strength")
        assertEquals(MotionSensorProfile.STATIC_HOLD, profile)
        assertTrue(profile.accelerometer)
        assertTrue(profile.gyroscope)
        assertFalse(profile.showStepMetrics)
    }

    @Test
    fun ordinaryStrengthMovementUsesFormSensorsWithoutStepMetrics() {
        val profile = MotionSensorProfileResolver.forExercise(movementId = "press", category = "strength")
        assertEquals(MotionSensorProfile.FORM_MOTION, profile)
        assertFalse(profile.stepCounter)
        assertFalse(profile.stepDetector)
        assertFalse(profile.showStepMetrics)
    }

    @Test
    fun explicitStepDrillMayUseStepSensors() {
        val profile = MotionSensorProfileResolver.forExercise(movementId = "step", category = "agility")
        assertEquals(MotionSensorProfile.STEP_DRILL, profile)
        assertTrue(profile.stepCounter)
        assertTrue(profile.stepDetector)
        assertTrue(profile.showStepMetrics)
    }
}
