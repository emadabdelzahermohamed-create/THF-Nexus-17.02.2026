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
    fun specificCatalogExercisesOverrideBroadSectionSport() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING,
            HealthSportMapper.toExerciseType("running", "walking-treadmill"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL,
            HealthSportMapper.toExerciseType("running", "jogging-treadmill"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL,
            HealthSportMapper.toExerciseType("running", "running-treadmill"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY,
            HealthSportMapper.toExerciseType("cycling", "bicycling-stationary"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY,
            HealthSportMapper.toExerciseType("cycling", "recumbent-bike"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY,
            HealthSportMapper.toExerciseType("home", "air-bike"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_ROWING_MACHINE,
            HealthSportMapper.toExerciseType("hiit", "rowing-stationary"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_ELLIPTICAL,
            HealthSportMapper.toExerciseType("hiit", "elliptical-trainer"),
        )
    }

    @Test
    fun drylandSwimmingProgramsAreNotWrittenAsSwimmingSessions() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING,
            HealthSportMapper.toExerciseType("swimming", "swim-dryland"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING,
            HealthSportMapper.toExerciseType("swimming", "swim-strength"),
        )
    }

    @Test
    fun unknownSportFailsClosedToOtherWorkout() {
        assertEquals(ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT, HealthSportMapper.toExerciseType("unknown-sport"))
    }
}
