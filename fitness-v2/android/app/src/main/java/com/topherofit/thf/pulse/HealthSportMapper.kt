package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord

/** Maps reviewed THF sport/exercise keys to official Health Connect exercise types. */
object HealthSportMapper {
    private val genericWorkoutKeys = setOf(
        "other",
        "other_workout",
        "workout",
        "exercise",
        "fitness",
        "general",
        "general_workout",
        "home",
        "team_sports",
    )

    /**
     * Prefer a recognized exercise ID over its broader program/section label.
     *
     * A generic OTHER_WORKOUT is emitted only for an explicit generic label. Unknown or
     * missing sport and exercise IDs throw before the caller can write a synthetic session.
     */
    fun toExerciseType(rawSport: String?, rawExerciseId: String? = null): Int {
        val sport = rawSport.orEmpty().trim().lowercase()
        val exerciseId = rawExerciseId.orEmpty().trim().lowercase()

        exerciseTypeForKey(exerciseId)?.let { return it }
        exerciseTypeForKey(sport)?.let { return it }

        if (exerciseId in genericWorkoutKeys || sport in genericWorkoutKeys) {
            return ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT
        }

        throw IllegalArgumentException(
            "No reviewed Health Connect exercise mapping for sport='$sport', exerciseId='$exerciseId'",
        )
    }

    private fun exerciseTypeForKey(key: String): Int? = when (key) {
        // Catalog IDs that are more precise than their program section.
        "swim-dryland", "swim-strength" ->
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING
        "jogging-treadmill", "running-treadmill" ->
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL
        "walking-treadmill" ->
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING
        "bicycling-stationary", "recumbent-bike", "air-bike" ->
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY
        "rowing-stationary" ->
            ExerciseSessionRecord.EXERCISE_TYPE_ROWING_MACHINE
        "elliptical-trainer" ->
            ExerciseSessionRecord.EXERCISE_TYPE_ELLIPTICAL

        "strength", "strength_training", "gym", "weights", "weightlifting",
        "squat", "lunge", "pushup", "plank" ->
            ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING
        "running", "run" -> ExerciseSessionRecord.EXERCISE_TYPE_RUNNING
        "treadmill", "running_treadmill" -> ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL
        "walking", "walk" -> ExerciseSessionRecord.EXERCISE_TYPE_WALKING
        "hiking", "hike" -> ExerciseSessionRecord.EXERCISE_TYPE_HIKING
        "cycling", "biking", "bike" -> ExerciseSessionRecord.EXERCISE_TYPE_BIKING
        "stationary_bike", "stationary_biking", "spin" ->
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY
        "football", "soccer" -> ExerciseSessionRecord.EXERCISE_TYPE_SOCCER
        "swimming", "pool_swimming", "swimming_pool" ->
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL
        "open_water_swimming", "swimming_open_water" ->
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER
        "yoga" -> ExerciseSessionRecord.EXERCISE_TYPE_YOGA
        "pilates" -> ExerciseSessionRecord.EXERCISE_TYPE_PILATES
        "calisthenics" -> ExerciseSessionRecord.EXERCISE_TYPE_CALISTHENICS
        "gymnastics" -> ExerciseSessionRecord.EXERCISE_TYPE_GYMNASTICS
        "hiit", "high_intensity_interval_training" ->
            ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING
        "boxing" -> ExerciseSessionRecord.EXERCISE_TYPE_BOXING
        "martial_arts", "martialarts" -> ExerciseSessionRecord.EXERCISE_TYPE_MARTIAL_ARTS
        "rowing" -> ExerciseSessionRecord.EXERCISE_TYPE_ROWING
        "rowing_machine" -> ExerciseSessionRecord.EXERCISE_TYPE_ROWING_MACHINE
        "tennis" -> ExerciseSessionRecord.EXERCISE_TYPE_TENNIS
        "table_tennis" -> ExerciseSessionRecord.EXERCISE_TYPE_TABLE_TENNIS
        "squash" -> ExerciseSessionRecord.EXERCISE_TYPE_SQUASH
        "badminton" -> ExerciseSessionRecord.EXERCISE_TYPE_BADMINTON
        "volleyball" -> ExerciseSessionRecord.EXERCISE_TYPE_VOLLEYBALL
        "basketball" -> ExerciseSessionRecord.EXERCISE_TYPE_BASKETBALL
        "handball" -> ExerciseSessionRecord.EXERCISE_TYPE_HANDBALL
        "stretching", "mobility", "warmup", "recovery" ->
            ExerciseSessionRecord.EXERCISE_TYPE_STRETCHING
        "breathing", "guided_breathing", "recovery_breathing" ->
            ExerciseSessionRecord.EXERCISE_TYPE_GUIDED_BREATHING
        else -> null
    }
}
