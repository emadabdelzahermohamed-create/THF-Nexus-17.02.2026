package com.topherofit.thf.pulse

import kotlin.math.max
import kotlin.math.min

/**
 * A local-day bucket derived from observed step-counter deltas.
 *
 * Sensor-counter days are partial by definition: a process may not observe the entire local day,
 * and a counter delta spanning midnight cannot be assigned truthfully to either day.
 */
data class DailyStepDay(
    val epochDay: Long,
    val steps: Long,
    val firstObservedAtWallMs: Long,
    val lastObservedAtWallMs: Long,
    val isPartial: Boolean = true,
)

data class DailyStepLedgerState(
    val lastCounterValue: Long? = null,
    val lastEpochDay: Long? = null,
    val lastElapsedRealtimeMs: Long? = null,
    val lastObservedAtWallMs: Long? = null,
    val lastBootCount: Int? = null,
    val days: List<DailyStepDay> = emptyList(),
)

enum class DailyStepRecordStatus {
    BASELINE_ESTABLISHED,
    COUNTED,
    NO_CHANGE,
    DAY_BOUNDARY_REBASE,
    BOOT_REBASE,
    COUNTER_RESET_REBASE,
    IMPLAUSIBLE_DELTA_REBASE,
    REJECTED_INVALID,
    REJECTED_OUT_OF_ORDER,
}

data class DailyStepLedgerUpdate(
    val state: DailyStepLedgerState,
    val status: DailyStepRecordStatus,
    val delta: Long,
)

data class DailyStepSummary(
    val totalSteps: Long,
    val observedDayCount: Int,
    val partialDayCount: Int,
    val completeDayCount: Int,
    /** Mean over stored days only; missing dates are never inserted as zero-step days. */
    val averageStepsPerObservedDay: Double?,
    /** Null when no explicitly complete day exists. */
    val completeDayAverage: Double?,
    val includesPartialDays: Boolean,
)

/**
 * Pure, persistence-ready policy for TYPE_STEP_COUNTER observations.
 *
 * The first reading is a baseline, not today's step count: the hardware counter may include
 * steps from before the app began observing. Counter deltas are attributed only when both
 * observations are on the same local day and same boot. A delta crossing midnight or reboot is
 * intentionally discarded because its day/source attribution is unknowable.
 */
object DailyStepLedger {
    private const val CODEC_VERSION = "D1"
    private const val MAX_PLAUSIBLE_STEPS_PER_SECOND = 5L
    private const val COUNTER_JUMP_ALLOWANCE = 20L
    private const val MAX_SINGLE_DELTA = 100_000L

    fun recordCounterReading(
        state: DailyStepLedgerState,
        epochDay: Long,
        observedAtWallMs: Long,
        elapsedRealtimeMs: Long,
        bootCount: Int?,
        cumulativeSteps: Long,
    ): DailyStepLedgerUpdate {
        if (!isWellFormed(state) ||
            epochDay < 0L ||
            observedAtWallMs <= 0L ||
            elapsedRealtimeMs < 0L ||
            bootCount != null && bootCount < 0 ||
            cumulativeSteps < 0L
        ) {
            return DailyStepLedgerUpdate(state, DailyStepRecordStatus.REJECTED_INVALID, 0L)
        }

        val previousDay = state.lastEpochDay
        val previousCounter = state.lastCounterValue
        val previousElapsed = state.lastElapsedRealtimeMs
        val previousBoot = state.lastBootCount

        // Local calendar dates can move backward when the user changes time zone. Only permit
        // that day-key rollback when the monotonic clock proves a newer sample from the same boot;
        // then the ordinary day-boundary path rebases and discards the ambiguous delta.
        if (previousDay != null && epochDay < previousDay) {
            val elapsedAdvanced = previousElapsed != null && elapsedRealtimeMs > previousElapsed
            val sameBootEvidence = when {
                previousBoot != null && bootCount != null -> previousBoot == bootCount
                previousBoot == null && bootCount == null -> elapsedAdvanced
                else -> false
            }
            if (!sameBootEvidence || !elapsedAdvanced) {
                return DailyStepLedgerUpdate(state, DailyStepRecordStatus.REJECTED_OUT_OF_ORDER, 0L)
            }
        }
        val hasBaseline = previousCounter != null &&
            previousDay != null &&
            previousElapsed != null &&
            state.lastObservedAtWallMs != null

        if (!hasBaseline) {
            return rebase(state, epochDay, observedAtWallMs, elapsedRealtimeMs, bootCount, cumulativeSteps,
                DailyStepRecordStatus.BASELINE_ESTABLISHED)
        }

        val bootIdentityChanged = when {
            previousBoot != null && bootCount != null -> previousBoot != bootCount
            previousBoot == null && bootCount == null -> elapsedRealtimeMs <= previousElapsed!!
            else -> true
        }
        if (bootIdentityChanged) {
            return rebase(state, epochDay, observedAtWallMs, elapsedRealtimeMs, bootCount, cumulativeSteps,
                DailyStepRecordStatus.BOOT_REBASE)
        }

        if (elapsedRealtimeMs <= previousElapsed!!) {
            return DailyStepLedgerUpdate(state, DailyStepRecordStatus.REJECTED_OUT_OF_ORDER, 0L)
        }

        if (epochDay != previousDay) {
            return rebase(state, epochDay, observedAtWallMs, elapsedRealtimeMs, bootCount, cumulativeSteps,
                DailyStepRecordStatus.DAY_BOUNDARY_REBASE)
        }

        if (cumulativeSteps < previousCounter!!) {
            return rebase(state, epochDay, observedAtWallMs, elapsedRealtimeMs, bootCount, cumulativeSteps,
                DailyStepRecordStatus.COUNTER_RESET_REBASE)
        }

        val delta = cumulativeSteps - previousCounter
        val elapsedDeltaMs = elapsedRealtimeMs - previousElapsed
        if (delta > maxPlausibleDelta(elapsedDeltaMs)) {
            return rebase(state, epochDay, observedAtWallMs, elapsedRealtimeMs, bootCount, cumulativeSteps,
                DailyStepRecordStatus.IMPLAUSIBLE_DELTA_REBASE)
        }

        val nextStatus = if (delta == 0L) DailyStepRecordStatus.NO_CHANGE else DailyStepRecordStatus.COUNTED
        val nextState = stateWithReading(
            state = state,
            epochDay = epochDay,
            observedAtWallMs = observedAtWallMs,
            elapsedRealtimeMs = elapsedRealtimeMs,
            bootCount = bootCount,
            cumulativeSteps = cumulativeSteps,
            delta = delta,
        ) ?: return DailyStepLedgerUpdate(state, DailyStepRecordStatus.REJECTED_INVALID, 0L)

        return DailyStepLedgerUpdate(nextState, nextStatus, delta)
    }

    fun summarize(
        state: DailyStepLedgerState,
        fromEpochDay: Long,
        throughEpochDay: Long,
    ): DailyStepSummary {
        if (!isWellFormed(state) || fromEpochDay > throughEpochDay) return emptySummary()
        val days = state.days.filter { it.epochDay in fromEpochDay..throughEpochDay }
        val total = days.fold(0L) { sum, day -> sum + day.steps }
        val completeDays = days.filterNot { it.isPartial }
        val completeTotal = completeDays.fold(0L) { sum, day -> sum + day.steps }
        return DailyStepSummary(
            totalSteps = total,
            observedDayCount = days.size,
            partialDayCount = days.count { it.isPartial },
            completeDayCount = completeDays.size,
            averageStepsPerObservedDay = days.takeIf { it.isNotEmpty() }?.let { total.toDouble() / it.size },
            completeDayAverage = completeDays.takeIf { it.isNotEmpty() }?.let { completeTotal.toDouble() / it.size },
            includesPartialDays = days.any { it.isPartial },
        )
    }

    fun encode(state: DailyStepLedgerState): String {
        require(isWellFormed(state)) { "Invalid daily step ledger state" }
        val header = listOf(
            CODEC_VERSION,
            state.lastCounterValue?.toString().orEmpty(),
            state.lastEpochDay?.toString().orEmpty(),
            state.lastElapsedRealtimeMs?.toString().orEmpty(),
            state.lastObservedAtWallMs?.toString().orEmpty(),
            state.lastBootCount?.toString().orEmpty(),
        ).joinToString("|")
        val rows = state.days.sortedBy { it.epochDay }.joinToString("\n") { day ->
            listOf(
                day.epochDay.toString(),
                day.steps.toString(),
                day.firstObservedAtWallMs.toString(),
                day.lastObservedAtWallMs.toString(),
                if (day.isPartial) "1" else "0",
            ).joinToString("|")
        }
        return if (rows.isEmpty()) "$header\n" else "$header\n$rows"
    }

    fun decode(raw: String?): DailyStepLedgerState? {
        if (raw.isNullOrBlank()) return null
        return runCatching {
            val lines = raw.split('\n')
            val header = lines.firstOrNull()?.removeSuffix("\r")?.split('|') ?: return null
            if (header.size != 6 || header[0] != CODEC_VERSION) return null

            fun optionalLong(value: String): Long? {
                if (value.isEmpty()) return null
                return value.toLongOrNull() ?: throw IllegalArgumentException("Invalid optional long")
            }
            fun optionalInt(value: String): Int? {
                if (value.isEmpty()) return null
                return value.toIntOrNull() ?: throw IllegalArgumentException("Invalid optional int")
            }

            val days = mutableListOf<DailyStepDay>()
            val seenDays = mutableSetOf<Long>()
            for (rawLine in lines.drop(1)) {
                val line = rawLine.removeSuffix("\r")
                if (line.isEmpty()) continue
                val fields = line.split('|')
                if (fields.size != 5) return null
                val epochDay = fields[0].toLongOrNull() ?: return null
                val steps = fields[1].toLongOrNull() ?: return null
                val firstObserved = fields[2].toLongOrNull() ?: return null
                val lastObserved = fields[3].toLongOrNull() ?: return null
                val isPartial = when (fields[4]) {
                    "1" -> true
                    "0" -> false
                    else -> return null
                }
                if (!seenDays.add(epochDay)) return null
                days += DailyStepDay(epochDay, steps, firstObserved, lastObserved, isPartial)
            }

            val state = DailyStepLedgerState(
                lastCounterValue = optionalLong(header[1]),
                lastEpochDay = optionalLong(header[2]),
                lastElapsedRealtimeMs = optionalLong(header[3]),
                lastObservedAtWallMs = optionalLong(header[4]),
                lastBootCount = optionalInt(header[5]),
                days = days.sortedBy { it.epochDay },
            )
            if (isWellFormed(state)) state else null
        }.getOrNull()
    }

    private fun rebase(
        state: DailyStepLedgerState,
        epochDay: Long,
        observedAtWallMs: Long,
        elapsedRealtimeMs: Long,
        bootCount: Int?,
        cumulativeSteps: Long,
        status: DailyStepRecordStatus,
    ): DailyStepLedgerUpdate {
        val nextState = stateWithReading(
            state = state,
            epochDay = epochDay,
            observedAtWallMs = observedAtWallMs,
            elapsedRealtimeMs = elapsedRealtimeMs,
            bootCount = bootCount,
            cumulativeSteps = cumulativeSteps,
            delta = 0L,
        ) ?: return DailyStepLedgerUpdate(state, DailyStepRecordStatus.REJECTED_INVALID, 0L)
        return DailyStepLedgerUpdate(nextState, status, 0L)
    }

    private fun stateWithReading(
        state: DailyStepLedgerState,
        epochDay: Long,
        observedAtWallMs: Long,
        elapsedRealtimeMs: Long,
        bootCount: Int?,
        cumulativeSteps: Long,
        delta: Long,
    ): DailyStepLedgerState? {
        val existing = state.days.firstOrNull { it.epochDay == epochDay }
        val priorSteps = existing?.steps ?: 0L
        if (Long.MAX_VALUE - priorSteps < delta) return null
        val day = DailyStepDay(
            epochDay = epochDay,
            steps = priorSteps + delta,
            firstObservedAtWallMs = existing?.firstObservedAtWallMs?.let { min(it, observedAtWallMs) } ?: observedAtWallMs,
            lastObservedAtWallMs = existing?.lastObservedAtWallMs?.let { max(it, observedAtWallMs) } ?: observedAtWallMs,
            isPartial = existing?.isPartial ?: true,
        )
        return state.copy(
            lastCounterValue = cumulativeSteps,
            lastEpochDay = epochDay,
            lastElapsedRealtimeMs = elapsedRealtimeMs,
            lastObservedAtWallMs = observedAtWallMs,
            lastBootCount = bootCount,
            days = (state.days.filterNot { it.epochDay == epochDay } + day).sortedBy { it.epochDay },
        )
    }

    private fun maxPlausibleDelta(elapsedDeltaMs: Long): Long {
        val seconds = elapsedDeltaMs / 1_000L
        val rateBound = if (seconds > (MAX_SINGLE_DELTA - COUNTER_JUMP_ALLOWANCE) / MAX_PLAUSIBLE_STEPS_PER_SECOND) {
            MAX_SINGLE_DELTA
        } else {
            seconds * MAX_PLAUSIBLE_STEPS_PER_SECOND + COUNTER_JUMP_ALLOWANCE
        }
        return min(MAX_SINGLE_DELTA, max(COUNTER_JUMP_ALLOWANCE, rateBound))
    }

    private fun isWellFormed(state: DailyStepLedgerState): Boolean {
        val baselineFields = listOf(
            state.lastCounterValue,
            state.lastEpochDay,
            state.lastElapsedRealtimeMs,
            state.lastObservedAtWallMs,
        )
        val present = baselineFields.count { it != null }
        if (present != 0 && present != baselineFields.size) return false
        if (state.lastBootCount != null && state.lastBootCount < 0) return false
        if (state.lastCounterValue != null && state.lastCounterValue < 0L) return false
        if (state.lastEpochDay != null && state.lastEpochDay < 0L) return false
        if (state.lastElapsedRealtimeMs != null && state.lastElapsedRealtimeMs < 0L) return false
        if (state.lastObservedAtWallMs != null && state.lastObservedAtWallMs <= 0L) return false

        val seenDays = mutableSetOf<Long>()
        var total = 0L
        for (day in state.days) {
            if (day.epochDay < 0L || day.steps < 0L ||
                day.firstObservedAtWallMs <= 0L ||
                day.lastObservedAtWallMs < day.firstObservedAtWallMs ||
                !seenDays.add(day.epochDay)
            ) return false
            if (Long.MAX_VALUE - total < day.steps) return false
            total += day.steps
        }
        if (state.lastEpochDay != null && state.days.none { it.epochDay == state.lastEpochDay }) return false
        return true
    }

    private fun emptySummary() = DailyStepSummary(
        totalSteps = 0L,
        observedDayCount = 0,
        partialDayCount = 0,
        completeDayCount = 0,
        averageStepsPerObservedDay = null,
        completeDayAverage = null,
        includesPartialDays = false,
    )
}
