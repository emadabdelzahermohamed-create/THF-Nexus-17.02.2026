package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import androidx.health.connect.client.records.metadata.Metadata
import java.time.Instant
import java.util.Locale
import kotlin.math.abs

internal enum class HealthActivitySessionKind {
    WALKING,
    RUNNING,
    CYCLING,
    SWIMMING_POOL,
    SWIMMING_OPEN_WATER,
}

internal data class HealthExerciseSessionCandidate<T>(
    val originalIndex: Int,
    val sourcePackage: String,
    val recordId: String,
    val activityKind: HealthActivitySessionKind,
    val startTime: Instant,
    val endTime: Instant,
    val observedAt: Instant?,
    val deviceType: Int?,
    val recordingMethod: Int,
    val verifiedForRewards: Boolean,
    val lastModifiedTime: Instant,
    val value: T,
)

internal data class HealthExerciseSessionRejection<T>(
    val originalIndex: Int,
    val reason: String,
    val value: T,
)

internal data class HealthExerciseSessionReconciliationResult<T>(
    val accepted: List<HealthExerciseSessionCandidate<T>>,
    val duplicates: List<HealthExerciseSessionCandidate<T>>,
    val ambiguous: List<HealthExerciseSessionCandidate<T>>,
    val invalid: List<HealthExerciseSessionRejection<T>>,
) {
    val duplicateCount: Int
        get() = duplicates.size
}

/**
 * Reconciles reviewed Health Connect walking, running, cycling and eligible wearable
 * swimming sessions.
 *
 * The provider/type/record-ID version selector runs first. This second layer catches
 * separate provider records that describe the same session. A single sport label is
 * deduplicated deterministically; conflicting labels are all excluded rather than
 * guessing which activity label was correct. Swimming candidates receive an additional
 * provider, watch/band and active/automatic recording-method check at this boundary.
 *
 * Unverified records never poison verified records. This is metadata reconciliation,
 * not device attestation or proof that a physical activity occurred.
 */
internal object HealthExerciseSessionReconciliationPolicy {
    const val SESSION_ENDPOINT_TOLERANCE_MILLIS: Long = 120_000L

    fun kindForExerciseType(exerciseType: Int): HealthActivitySessionKind? = when (exerciseType) {
        ExerciseSessionRecord.EXERCISE_TYPE_WALKING -> HealthActivitySessionKind.WALKING
        ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
        ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL -> HealthActivitySessionKind.RUNNING
        ExerciseSessionRecord.EXERCISE_TYPE_BIKING,
        ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY -> HealthActivitySessionKind.CYCLING
        ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL -> HealthActivitySessionKind.SWIMMING_POOL
        ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER -> HealthActivitySessionKind.SWIMMING_OPEN_WATER
        else -> null
    }

    fun <T> reconcile(
        candidates: List<HealthExerciseSessionCandidate<T>>,
    ): HealthExerciseSessionReconciliationResult<T> {
        val accepted = mutableListOf<HealthExerciseSessionCandidate<T>>()
        val validVerified = mutableListOf<HealthExerciseSessionCandidate<T>>()
        val invalid = mutableListOf<HealthExerciseSessionRejection<T>>()

        candidates.forEach { candidate ->
            if (!candidate.verifiedForRewards) {
                // Preserve upstream manual/unknown/anomaly provenance without allowing it
                // to downgrade or otherwise poison a verified record.
                accepted += candidate
                return@forEach
            }

            val reason = when {
                candidate.sourcePackage.isBlank() -> "MISSING_SOURCE_PACKAGE"
                candidate.recordId.isBlank() -> "MISSING_RECORD_ID"
                candidate.startTime.isBefore(Instant.EPOCH) ||
                    !candidate.endTime.isAfter(candidate.startTime) -> "INVALID_ACTIVITY_SESSION_TIME"
                candidate.observedAt == null -> "MISSING_OBSERVATION_TIME"
                candidate.endTime.isAfter(candidate.observedAt) -> "FUTURE_ACTIVITY_SESSION"
                candidate.activityKind.isSwimming() &&
                    !HealthSourceTrustPolicy.isApprovedHealthConnectProvider(candidate.sourcePackage) ->
                    "UNTRUSTED_SWIMMING_PROVIDER"
                candidate.activityKind.isSwimming() &&
                    candidate.deviceType != Device.TYPE_WATCH &&
                    candidate.deviceType != Device.TYPE_FITNESS_BAND ->
                    "INCOMPATIBLE_SWIMMING_DEVICE"
                candidate.activityKind.isSwimming() &&
                    candidate.recordingMethod != Metadata.RECORDING_METHOD_ACTIVELY_RECORDED &&
                    candidate.recordingMethod != Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED ->
                    "UNSUPPORTED_SWIMMING_RECORDING_METHOD"
                else -> null
            }
            if (reason != null) {
                invalid += HealthExerciseSessionRejection(
                    originalIndex = candidate.originalIndex,
                    reason = reason,
                    value = candidate.value,
                )
            } else {
                validVerified += candidate
            }
        }

        val parents = IntArray(validVerified.size) { it }

        fun find(index: Int): Int {
            if (parents[index] != index) parents[index] = find(parents[index])
            return parents[index]
        }

        fun union(left: Int, right: Int) {
            val leftRoot = find(left)
            val rightRoot = find(right)
            if (leftRoot != rightRoot) {
                // Stable root selection keeps component construction deterministic.
                if (leftRoot < rightRoot) parents[rightRoot] = leftRoot else parents[leftRoot] = rightRoot
            }
        }

        for (leftIndex in validVerified.indices) {
            val left = validVerified[leftIndex]
            for (rightIndex in leftIndex + 1 until validVerified.size) {
                val right = validVerified[rightIndex]
                if (sameSessionWindow(left, right)) union(leftIndex, rightIndex)
            }
        }

        val duplicates = mutableListOf<HealthExerciseSessionCandidate<T>>()
        val ambiguous = mutableListOf<HealthExerciseSessionCandidate<T>>()
        val components = validVerified.indices.groupBy { find(it) }.values
        components.forEach { componentIndexes ->
            val component = componentIndexes.map { validVerified[it] }
            if (component.size == 1) {
                accepted += component.single()
            } else if (component.map { it.activityKind }.distinct().size > 1) {
                // Do not choose a sport when reviewed sources disagree about the same session.
                ambiguous += component
            } else {
                val winner = component.maxWithOrNull(
                    compareBy<HealthExerciseSessionCandidate<T>> { devicePriority(it.deviceType) }
                        .thenBy { it.lastModifiedTime }
                        .thenBy { it.sourcePackage.trim().lowercase(Locale.ROOT) }
                        .thenBy { it.recordId.trim() }
                        .thenBy { it.originalIndex },
                ) ?: error("A non-empty activity-session component must have a winner")
                accepted += winner
                duplicates += component.filter { it.originalIndex != winner.originalIndex }
            }
        }

        return HealthExerciseSessionReconciliationResult(
            accepted = accepted.sortedBy { it.originalIndex },
            duplicates = duplicates.sortedBy { it.originalIndex },
            ambiguous = ambiguous.sortedBy { it.originalIndex },
            invalid = invalid.sortedBy { it.originalIndex },
        )
    }

    private fun HealthActivitySessionKind.isSwimming(): Boolean =
        this == HealthActivitySessionKind.SWIMMING_POOL ||
            this == HealthActivitySessionKind.SWIMMING_OPEN_WATER

    private fun <T> sameSessionWindow(
        left: HealthExerciseSessionCandidate<T>,
        right: HealthExerciseSessionCandidate<T>,
    ): Boolean =
        withinEndpointTolerance(left.startTime, right.startTime) &&
            withinEndpointTolerance(left.endTime, right.endTime)

    private fun withinEndpointTolerance(left: Instant, right: Instant): Boolean =
        abs(left.toEpochMilli() - right.toEpochMilli()) <= SESSION_ENDPOINT_TOLERANCE_MILLIS

    private fun devicePriority(deviceType: Int?): Int = when (deviceType) {
        Device.TYPE_WATCH, Device.TYPE_FITNESS_BAND -> 3
        Device.TYPE_CHEST_STRAP, Device.TYPE_RING -> 2
        Device.TYPE_PHONE -> 1
        else -> 0
    }
}
