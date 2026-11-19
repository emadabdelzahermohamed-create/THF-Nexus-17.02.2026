package com.topherofit.thf.pulse

import java.time.Instant
import java.util.Locale

/**
 * A metric interval after provider/version selection.
 *
 * The value fingerprint is metric-specific and exact: this policy never estimates or
 * interpolates missing portions of partially overlapping records.
 */
internal data class HealthMetricSourceCandidate<T>(
    val originalIndex: Int,
    val sourcePackage: String,
    val metricType: String,
    val startTime: Instant,
    val endTime: Instant,
    val valueFingerprint: String,
    val verifiedForRewards: Boolean,
    val lastModifiedTime: Instant,
    val value: T,
)

internal data class HealthMetricSourceReconciliationResult<T>(
    /** Records safe to retain as independent metric intervals. */
    val accepted: List<HealthMetricSourceCandidate<T>>,
    /** Exact interval/value mirrors; one deterministic winner is retained. */
    val duplicates: List<HealthMetricSourceCandidate<T>>,
    /** Overlapping verified intervals from different providers; none may affect totals. */
    val ambiguous: List<HealthMetricSourceCandidate<T>>,
) {
    val duplicateCount: Int
        get() = duplicates.size
}

/**
 * Prevents cross-provider Health Connect double counting without guessing how to split
 * partially overlapping intervals.
 *
 * Exact matches are deduplicated by metric type, interval and value. The winner prefers
 * reward-verified evidence, then the newest provider modification, then a stable source/index
 * tie-break. Partial overlaps between different verified providers are retained as
 * source-labelled, non-reward-verified evidence by the caller.
 *
 * Unverified records never poison an otherwise verified source through overlap rejection.
 * Same-source partial intervals remain independent because this policy cannot infer whether
 * that provider intentionally emitted separate samples.
 */
internal object HealthMetricSourceReconciliationPolicy {
    private data class ExactMetricKey(
        val metricType: String,
        val startTime: Instant,
        val endTime: Instant,
        val valueFingerprint: String,
    )

    fun <T> reconcile(
        candidates: List<HealthMetricSourceCandidate<T>>,
    ): HealthMetricSourceReconciliationResult<T> {
        val groupable = mutableListOf<HealthMetricSourceCandidate<T>>()
        val ungrouped = mutableListOf<HealthMetricSourceCandidate<T>>()
        candidates.forEach { candidate ->
            if (
                candidate.sourcePackage.isNotBlank() &&
                candidate.metricType.isNotBlank() &&
                candidate.endTime.isAfter(candidate.startTime)
            ) {
                groupable += candidate
            } else {
                ungrouped += candidate
            }
        }

        val winners = mutableListOf<HealthMetricSourceCandidate<T>>()
        val duplicates = mutableListOf<HealthMetricSourceCandidate<T>>()
        groupable.groupBy { candidate ->
            ExactMetricKey(
                metricType = candidate.metricType,
                startTime = candidate.startTime,
                endTime = candidate.endTime,
                valueFingerprint = candidate.valueFingerprint,
            )
        }.values.forEach { group ->
            if (group.size == 1) {
                winners += group.single()
            } else {
                val winner = group.maxWithOrNull(
                    compareBy<HealthMetricSourceCandidate<T>> { it.verifiedForRewards }
                        .thenBy { it.lastModifiedTime }
                        .thenBy { it.sourcePackage.trim().lowercase(Locale.ROOT) }
                        .thenBy { it.originalIndex },
                ) ?: error("A non-empty metric group must have a winner")
                winners += winner
                duplicates += group.filter { it.originalIndex != winner.originalIndex }
            }
        }

        val ambiguousIndexes = mutableSetOf<Int>()
        val verified = winners.filter { it.verifiedForRewards }
        for (leftIndex in verified.indices) {
            val left = verified[leftIndex]
            for (rightIndex in leftIndex + 1 until verified.size) {
                val right = verified[rightIndex]
                if (
                    left.metricType == right.metricType &&
                    !left.sourcePackage.equals(right.sourcePackage, ignoreCase = true) &&
                    left.startTime.isBefore(right.endTime) &&
                    right.startTime.isBefore(left.endTime)
                ) {
                    ambiguousIndexes += left.originalIndex
                    ambiguousIndexes += right.originalIndex
                }
            }
        }

        val ambiguous = winners.filter { it.originalIndex in ambiguousIndexes }
        val accepted = winners.filter { it.originalIndex !in ambiguousIndexes } + ungrouped
        return HealthMetricSourceReconciliationResult(
            accepted = accepted.sortedBy { it.originalIndex },
            duplicates = duplicates.sortedBy { it.originalIndex },
            ambiguous = ambiguous.sortedBy { it.originalIndex },
        )
    }
}
