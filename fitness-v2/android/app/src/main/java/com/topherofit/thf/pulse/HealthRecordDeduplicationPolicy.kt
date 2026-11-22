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
    /** Canonical reward-relevant payload + provenance fingerprint; null means incomparable. */
    val payloadFingerprint: String? = null,
)

internal data class HealthRecordDeduplicationResult<T>(
    val selected: List<HealthRecordVersion<T>>,
    /** Superseded versions and identical latest payloads collapsed to one record. */
    val duplicateCount: Int,
    /** Latest records sharing identity/version/time but disagreeing on payload or provenance. */
    val conflicting: List<HealthRecordVersion<T>>,
)

/**
 * Selects the newest version of each source-scoped Health Connect record.
 *
 * A missing/blank stable key is deliberately not grouped. Version and modification time
 * determine the latest revision. If two latest revisions tie on both fields, they are
 * collapsed only when the caller supplies the same non-null reward-payload fingerprint.
 * Conflicting or incomparable tied revisions are quarantined together; input/read order
 * must never decide which reward value wins.
 */
internal object HealthRecordDeduplicationPolicy {
    fun <T> selectLatest(
        candidates: List<HealthRecordVersion<T>>,
    ): HealthRecordDeduplicationResult<T> {
        val groups = linkedMapOf<String, MutableList<HealthRecordVersion<T>>>()
        val unkeyed = mutableListOf<HealthRecordVersion<T>>()

        candidates.forEach { candidate ->
            val key = candidate.stableKey?.trim()?.takeIf { it.isNotEmpty() }
            if (key == null) {
                unkeyed += candidate
            } else {
                groups.getOrPut(key) { mutableListOf() } += candidate
            }
        }

        val selectedByKey = mutableListOf<HealthRecordVersion<T>>()
        val conflicting = mutableListOf<HealthRecordVersion<T>>()
        var duplicateCount = 0

        groups.values.forEach { group ->
            val newestVersion = group.maxOf { it.clientRecordVersion }
            val newestVersionRecords = group.filter { it.clientRecordVersion == newestVersion }
            val newestModifiedTime = newestVersionRecords.maxOf { it.lastModifiedTime }
            val latestRecords = newestVersionRecords.filter {
                it.lastModifiedTime == newestModifiedTime
            }

            // Older revisions are superseded regardless of whether the latest revision
            // is safe to select. Never resurrect stale evidence when the latest revision
            // conflicts.
            duplicateCount += group.size - latestRecords.size

            if (latestRecords.size > 1) {
                val fingerprints = latestRecords.map {
                    it.payloadFingerprint?.takeIf { fingerprint -> fingerprint.isNotBlank() }
                }
                val identicalComparablePayloads =
                    fingerprints.all { it != null } && fingerprints.distinct().size == 1

                if (identicalComparablePayloads) {
                    selectedByKey += latestRecords.first()
                    duplicateCount += latestRecords.size - 1
                } else {
                    // Do not let Health Connect read order choose between same-version,
                    // same-time records with conflicting or unavailable reward evidence.
                    conflicting += latestRecords
                }
            } else {
                selectedByKey += latestRecords.single()
            }
        }

        val orderedConflicts = conflicting.sortedWith(
            compareBy<HealthRecordVersion<T>> { it.stableKey.orEmpty() }
                .thenBy { it.clientRecordVersion }
                .thenBy { it.lastModifiedTime }
                .thenBy { it.payloadFingerprint.orEmpty() },
        )
        return HealthRecordDeduplicationResult(
            selected = selectedByKey + unkeyed,
            duplicateCount = duplicateCount,
            conflicting = orderedConflicts,
        )
    }
}
