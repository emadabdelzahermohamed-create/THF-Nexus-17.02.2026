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
    fun recognizedExerciseIdOverridesAnyBroaderProgramSport() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_YOGA,
            HealthSportMapper.toExerciseType("home", "yoga"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_PILATES,
            HealthSportMapper.toExerciseType("strength_training", "pilates"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
            HealthSportMapper.toExerciseType("home", "running"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING,
            HealthSportMapper.toExerciseType("swimming", "swim-dryland"),
        )
    }

    @Test
    fun knownSportRemainsFallbackWhenExerciseIdIsNotMapped() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
            HealthSportMapper.toExerciseType("running", "program-5k-beginner"),
        )
    }

    @Test
    fun currentCatalogRecoveryAndTeamSportSectionsHaveExplicitMappings() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_STRETCHING,
            HealthSportMapper.toExerciseType("recovery", "calves-smr"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT,
            HealthSportMapper.toExerciseType("team_sports", "team-speed"),
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
    fun explicitGenericLabelsMapToOtherWorkout() {
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT,
            HealthSportMapper.toExerciseType("other"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT,
            HealthSportMapper.toExerciseType("home", "unmapped-home-exercise"),
        )
        assertEquals(
            ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT,
            HealthSportMapper.toExerciseType("running", "other"),
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun unknownSportAndExerciseIdAreRejectedInsteadOfInventingOtherWorkout() {
        HealthSportMapper.toExerciseType("unknown-sport", "unknown-exercise")
    }

    @Test(expected = IllegalArgumentException::class)
    fun missingSportAndExerciseIdAreRejected() {
        HealthSportMapper.toExerciseType(null, null)
    }
}
