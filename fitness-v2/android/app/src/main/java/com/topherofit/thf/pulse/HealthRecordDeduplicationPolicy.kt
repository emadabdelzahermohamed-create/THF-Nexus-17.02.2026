package com.topherofit.thf.pulse

import java.time.Instant

/** Stable Health Connect type labels; never derive identity from minifiable class names. */
internal enum class HealthRecordType(val stableId: String) {
    STEPS("StepsRecord"),
    DISTANCE("DistanceRecord"),
    ACTIVE_CALORIES("ActiveCaloriesBurnedRecord"),
    EXERCISE_SESSION("ExerciseSessionRecord"),
}

internal data class HealthRecordVersion<T>(
    val stableKey: String?,
    val clientRecordVersion: Long,
    val lastModifiedTime: Instant,
    val value: T,
)

internal data class HealthRecordDeduplicationResult<T>(
    val selected: List<HealthRecordVersion<T>>,
    val duplicateCount: Int,
)

/**
 * Selects the newest version of each source-scoped Health Connect record.
 *
 * A missing/blank stable key is deliberately not grouped: malformed identities must not
 * cause unrelated records to collapse into one synthetic duplicate. The selected value,
 * version and provenance stay together so metric totals cannot accidentally use an older
 * record after the trust assessment selected a newer version.
 */
internal object HealthRecordDeduplicationPolicy {
    fun <T> selectLatest(
        candidates: List<HealthRecordVersion<T>>,
    ): HealthRecordDeduplicationResult<T> {
        val selectedByKey = linkedMapOf<String, HealthRecordVersion<T>>()
        val unkeyed = mutableListOf<HealthRecordVersion<T>>()

        candidates.forEach { candidate ->
            val key = candidate.stableKey?.trim()?.takeIf { it.isNotEmpty() }
            if (key == null) {
                unkeyed += candidate
            } else {
                val current = selectedByKey[key]
                if (current == null || isNewer(candidate, current)) {
                    selectedByKey[key] = candidate
                }
            }
        }

        val selected = selectedByKey.values.toList() + unkeyed
        return HealthRecordDeduplicationResult(
            selected = selected,
            duplicateCount = candidates.size - selected.size,
        )
    }

    private fun <T> isNewer(
        candidate: HealthRecordVersion<T>,
        current: HealthRecordVersion<T>,
    ): Boolean = when {
        candidate.clientRecordVersion != current.clientRecordVersion ->
            candidate.clientRecordVersion > current.clientRecordVersion
        else -> candidate.lastModifiedTime.isAfter(current.lastModifiedTime)
    }
}
