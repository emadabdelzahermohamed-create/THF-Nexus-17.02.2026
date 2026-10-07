package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord

/** Maps THF's stable sport keys to official Health Connect exercise types. */
object HealthSportMapper {
    fun toExerciseType(rawSport: String?, rawExerciseId: String? = null): Int {
        val sport = rawSport.orEmpty().trim().lowercase()
        val exerciseId = rawExerciseId.orEmpty().trim().lowercase()
        val key = if (sport.isNotBlank()) sport else exerciseId

        return when (key) {
            "strength", "strength_training", "gym", "weights", "weightlifting",
            "squat", "lunge", "pushup", "plank" -> ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING
            "running", "run" -> ExerciseSessionRecord.EXERCISE_TYPE_RUNNING
            "treadmill", "running_treadmill" -> ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL
            "walking", "walk" -> ExerciseSessionRecord.EXERCISE_TYPE_WALKING
            "hiking", "hike" -> ExerciseSessionRecord.EXERCISE_TYPE_HIKING
            "cycling", "biking", "bike" -> ExerciseSessionRecord.EXERCISE_TYPE_BIKING
            "stationary_bike", "stationary_biking", "spin" -> ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY
            "football", "soccer" -> ExerciseSessionRecord.EXERCISE_TYPE_SOCCER
            "swimming", "pool_swimming", "swimming_pool" -> ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL
            "open_water_swimming", "swimming_open_water" -> ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER
            "yoga" -> ExerciseSessionRecord.EXERCISE_TYPE_YOGA
            "pilates" -> ExerciseSessionRecord.EXERCISE_TYPE_PILATES
            "calisthenics" -> ExerciseSessionRecord.EXERCISE_TYPE_CALISTHENICS
            "gymnastics" -> ExerciseSessionRecord.EXERCISE_TYPE_GYMNASTICS
            "hiit", "high_intensity_interval_training" -> ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING
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
            "stretching", "mobility", "warmup" -> ExerciseSessionRecord.EXERCISE_TYPE_STRETCHING
            "breathing", "guided_breathing", "recovery_breathing" -> ExerciseSessionRecord.EXERCISE_TYPE_GUIDED_BREATHING
            else -> ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT
        }
    }
}
