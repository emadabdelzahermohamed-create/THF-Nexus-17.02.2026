package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import org.junit.Assert.assertEquals
import org.junit.Test

class HealthSportMapperTest {
    @Test
    fun mapsCanonicalSportsToOfficialTypes() {
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING, HealthSportMapper.toExerciseType("strength_training"))
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_RUNNING, HealthSportMapper.toExerciseType("running"))
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_SOCCER, HealthSportMapper.toExerciseType("football"))
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER, HealthSportMapper.toExerciseType("open_water_swimming"))
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING, HealthSportMapper.toExerciseType("hiit"))
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_GUIDED_BREATHING, HealthSportMapper.toExerciseType("guided_breathing"))
    }

    @Test
    fun unknownSportFailsClosedToOtherWorkout() {
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT, HealthSportMapper.toExerciseType("unknown-sport"))
    }
}
