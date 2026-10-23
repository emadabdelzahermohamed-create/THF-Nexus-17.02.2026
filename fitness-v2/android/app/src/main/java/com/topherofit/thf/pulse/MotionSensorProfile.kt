package com.topherofit.thf.pulse

enum class MotionSensorProfile(
    val wireName: String,
    val stepCounter: Boolean,
    val stepDetector: Boolean,
    val accelerometer: Boolean,
    val gyroscope: Boolean,
    val showStepMetrics: Boolean,
) {
    FORM_MOTION("form_motion", false, false, true, true, false),
    IMPACT_JUMP("impact_jump", false, false, true, true, false),
    STATIC_HOLD("static_hold", false, false, true, true, false),
    STEP_DRILL("step_drill", true, true, true, true, true);

    companion object {
        fun fromWire(value: String?): MotionSensorProfile = entries.firstOrNull {
            it.wireName.equals(value?.trim(), ignoreCase = true)
        } ?: FORM_MOTION
    }
}

object MotionSensorProfileResolver {
    fun forExercise(movementId: String?, category: String?): MotionSensorProfile {
        val movement = movementId.orEmpty().trim().lowercase()
        val family = category.orEmpty().trim().lowercase()
        if (movement.contains("jump") || movement.contains("hop") || family.contains("plyometric")) {
            return MotionSensorProfile.IMPACT_JUMP
        }
        if (movement.contains("isometric") || movement.contains("hold") || movement.contains("plank")) {
            return MotionSensorProfile.STATIC_HOLD
        }
        if (movement == "step" || movement.contains("step-up") || movement.contains("step drill") || family.contains("agility-step")) {
            return MotionSensorProfile.STEP_DRILL
        }
        return MotionSensorProfile.FORM_MOTION
    }
}
