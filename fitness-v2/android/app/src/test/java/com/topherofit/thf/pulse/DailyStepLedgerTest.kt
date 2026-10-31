package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class DailyStepLedgerTest {
    private fun record(
        state: DailyStepLedgerState,
        day: Long = 20_000L,
        wall: Long = 1_800_000_000_000L,
        elapsed: Long,
        boot: Int? = 4,
        raw: Long,
    ) = DailyStepLedger.recordCounterReading(
        state = state,
        epochDay = day,
        observedAtWallMs = wall,
        elapsedRealtimeMs = elapsed,
        bootCount = boot,
        cumulativeSteps = raw,
    )

    @Test
    fun firstReadingEstablishesBaselineWithoutCreditingSinceBootSteps() {
        val update = record(DailyStepLedgerState(), elapsed = 10_000L, raw = 12_345L)

        assertEquals(DailyStepRecordStatus.BASELINE_ESTABLISHED, update.status)
        assertEquals(0L, update.delta)
        assertEquals(0L, update.state.days.single().steps)
        assertTrue(update.state.days.single().isPartial)
    }

    @Test
    fun sameDayReadingsAccumulateOnlyCounterDeltas() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 1_000L)
        val second = record(first.state, wall = 1_800_000_024_000L, elapsed = 25_000L, raw = 1_120L)
        val third = record(second.state, wall = 1_800_000_040_000L, elapsed = 41_000L, raw = 1_200L)

        assertEquals(120L, second.delta)
        assertEquals(80L, third.delta)
        assertEquals(200L, third.state.days.single().steps)
    }

    @Test
    fun duplicateCounterReadingDoesNotDoubleCount() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 100L)
        val second = record(first.state, elapsed = 2_000L, raw = 100L)

        assertEquals(DailyStepRecordStatus.NO_CHANGE, second.status)
        assertEquals(0L, second.delta)
        assertEquals(0L, second.state.days.single().steps)
    }

    @Test
    fun dayBoundaryDropsAmbiguousCrossMidnightDeltaAndStartsPartialDay() {
        val first = record(DailyStepLedgerState(), day = 20_000L, elapsed = 10_000L, raw = 500L)
        val nextDay = record(first.state, day = 20_001L, wall = 1_800_086_400_000L, elapsed = 86_410_000L, raw = 2_500L)
        val later = record(nextDay.state, day = 20_001L, wall = 1_800_086_430_000L, elapsed = 86_440_000L, raw = 2_530L)

        assertEquals(DailyStepRecordStatus.DAY_BOUNDARY_REBASE, nextDay.status)
        assertEquals(0L, nextDay.delta)
        assertEquals(0L, nextDay.state.days.last().steps)
        assertEquals(30L, later.delta)
        assertEquals(30L, later.state.days.last().steps)
        assertEquals(2, later.state.days.size)
        assertTrue(later.state.days.last().isPartial)
    }

    @Test
    fun bootChangeRebasesCounterWithoutInventingSteps() {
        val first = record(DailyStepLedgerState(), elapsed = 50_000L, boot = 4, raw = 900L)
        val afterBoot = record(first.state, elapsed = 2_000L, boot = 5, raw = 15L)

        assertEquals(DailyStepRecordStatus.BOOT_REBASE, afterBoot.status)
        assertEquals(0L, afterBoot.delta)
        assertEquals(0L, afterBoot.state.days.single().steps)
    }

    @Test
    fun counterResetDoesNotSubtractOrAddSteps() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 900L)
        val reset = record(first.state, elapsed = 5_000L, raw = 12L)

        assertEquals(DailyStepRecordStatus.COUNTER_RESET_REBASE, reset.status)
        assertEquals(0L, reset.delta)
        assertEquals(0L, reset.state.days.single().steps)
    }

    @Test
    fun implausibleCounterJumpIsRejectedAndRebased() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 100L)
        val jump = record(first.state, elapsed = 2_000L, raw = 10_000L)

        assertEquals(DailyStepRecordStatus.IMPLAUSIBLE_DELTA_REBASE, jump.status)
        assertEquals(0L, jump.delta)
        assertEquals(0L, jump.state.days.single().steps)
        val next = record(jump.state, elapsed = 32_000L, raw = 10_120L)
        assertEquals(120L, next.delta)
    }

    @Test
    fun outOfOrderReadingLeavesStateUnchanged() {
        val first = record(DailyStepLedgerState(), elapsed = 10_000L, raw = 100L)
        val stale = record(first.state, wall = 1_799_999_000_000L, elapsed = 9_000L, raw = 500L)

        assertEquals(DailyStepRecordStatus.REJECTED_OUT_OF_ORDER, stale.status)
        assertEquals(first.state, stale.state)
    }

    @Test
    fun summaryUsesOnlyPersistedDaysAndLabelsPartialCoverage() {
        val first = record(DailyStepLedgerState(), day = 20_000L, elapsed = 1_000L, raw = 100L)
        val dayOne = record(first.state, elapsed = 21_000L, raw = 160L)
        val dayTwo = record(dayOne.state, day = 20_002L, wall = 1_800_172_800_000L, elapsed = 172_801_000L, raw = 500L)
        val dayTwoCounted = record(dayTwo.state, day = 20_002L, wall = 1_800_172_830_000L, elapsed = 172_831_000L, raw = 580L)

        val summary = DailyStepLedger.summarize(dayTwoCounted.state, fromEpochDay = 20_000L, throughEpochDay = 20_002L)

        assertEquals(140L, summary.totalSteps)
        assertEquals(2, summary.observedDayCount)
        assertEquals(2, summary.partialDayCount)
        assertEquals(70.0, summary.averageStepsPerObservedDay!!, 0.0)
        assertTrue(summary.includesPartialDays)
        assertNull(summary.completeDayAverage)
    }

    @Test
    fun codecRoundTripsDailyHistoryAndCounterBaseline() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 100L)
        val second = record(first.state, elapsed = 21_000L, raw = 150L)
        val encoded = DailyStepLedger.encode(second.state)
        val decoded = requireNotNull(DailyStepLedger.decode(encoded))

        assertEquals(second.state, decoded)
    }

    @Test
    fun malformedOrInconsistentLedgerFailsClosed() {
        assertNull(DailyStepLedger.decode(""))
        assertNull(DailyStepLedger.decode("D1|NaN|20000|1000|1800000000000|4\n"))
        assertNull(DailyStepLedger.decode("D1|100|20000|1000|1800000000000|4\n20000|-1|1800000000000|1800000000000|1"))
        assertNull(DailyStepLedger.decode("D1|100|20000|1000|1800000000000|4\n20000|10|1800000000000|1800000000000|1\n20000|20|1800000000001|1800000000002|1"))
    }

    @Test
    fun invalidInputCannotChangePersistedState() {
        val first = record(DailyStepLedgerState(), elapsed = 1_000L, raw = 100L)
        val invalid = record(first.state, elapsed = 2_000L, raw = -1L)

        assertEquals(DailyStepRecordStatus.REJECTED_INVALID, invalid.status)
        assertEquals(first.state, invalid.state)
    }
}
