package com.topherofit.thf.pulse

import android.annotation.SuppressLint
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.aggregate.AggregationResult
import androidx.health.connect.client.records.*
import androidx.health.connect.client.records.metadata.DataOrigin
import androidx.health.connect.client.records.metadata.Metadata
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.response.ReadRecordsResponse
import androidx.health.connect.client.time.TimeRangeFilter
import androidx.health.connect.client.units.Mass
import java.lang.reflect.Proxy
import java.time.Instant
import java.time.ZoneOffset
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test

@SuppressLint("RestrictedApi")
class HealthServicesReaderTest {
    private val now = Instant.parse("2026-10-25T08:00:00Z")

    @Test fun stepsUseProviderAggregateInsteadOfDoubleCountingRawSources() = runBlocking {
        var request: AggregateRequest? = null
        val client = client { name, args ->
            check(name == "aggregate") { "Cumulative steps must not use raw record reads" }
            request = args[0] as AggregateRequest
            AggregationResult(mapOf("Steps_count_total" to 1234L), emptyMap(), setOf(DataOrigin("com.sec.android.app.shealth")))
        }
        val result = source(client).read(HealthService.STEPS)
        assertEquals(1234.0, result.values.single().value, 0.0)
        assertEquals(AggregateRequest(setOf(StepsRecord.COUNT_TOTAL), TimeRangeFilter.between(
            Instant.parse("2026-10-25T00:00:00Z"), now,
        )), request)
        assertEquals(Instant.parse("2026-10-25T00:00:00Z"), result.windowStart)
        assertEquals(now, result.windowEnd)
        assertEquals(setOf("com.sec.android.app.shealth"), result.origins)
    }

    @Test fun absentAggregateIsNoDataButMeasuredZeroIsReady() = runBlocking {
        val empty = source(client { _, _ -> AggregationResult(emptyMap(), emptyMap(), emptySet()) })
        assertEquals(HealthMetricStatus.NO_DATA, empty.read(HealthService.STEPS).status)
        val zero = source(client { _, _ -> AggregationResult(mapOf("Steps_count_total" to 0L), emptyMap(), emptySet()) })
        assertEquals(0.0, zero.read(HealthService.STEPS).values.single().value, 0.0)
    }

    @Test fun latestWeightUsesBoundedReadAndPreservesManualProvenance() = runBlocking {
        var request: ReadRecordsRequest<*>? = null
        val weight = WeightRecord(now.minusSeconds(60), ZoneOffset.UTC, Mass.kilograms(72.5), Metadata.manualEntry())
        val client = client { name, args ->
            check(name == "readRecords")
            request = args[0] as ReadRecordsRequest<*>
            ReadRecordsResponse(listOf(weight), null)
        }
        val result = source(client).read(HealthService.WEIGHT)
        assertEquals(72.5, result.values.single().value, 0.001)
        assertEquals("kg", result.values.single().unit)
        assertEquals(now.minusSeconds(60), result.observedAt)
        assertEquals(Metadata.RECORDING_METHOD_MANUAL_ENTRY, result.recordingMethod)
        assertEquals(WeightRecord::class, request!!.recordType)
        assertFalse(request!!.ascendingOrder)
        assertEquals(1, request!!.pageSize)
        assertEquals(now.minusSeconds(28 * 86400L), request!!.timeRangeFilter.startTime)
    }

    @Test fun nutritionWithMacrosButNoEnergyDoesNotInventCalories() = runBlocking {
        val meal = NutritionRecord(
            startTime = now.minusSeconds(300), startZoneOffset = ZoneOffset.UTC,
            endTime = now.minusSeconds(240), endZoneOffset = ZoneOffset.UTC,
            metadata = Metadata.manualEntry(), protein = Mass.grams(20.0),
        )
        val result = source(client { _, _ -> ReadRecordsResponse(listOf(meal), null) }).read(HealthService.NUTRITION)
        assertEquals(HealthMetricStatus.READY, result.status)
        assertEquals(1, result.values.size)
        assertEquals(20.0, result.values.single().value, 0.0)
        assertEquals("g", result.values.single().unit)
    }

    @Test fun everyServiceHasAnExecutableReadAndNoWriteOrNetworkOperation() = runBlocking {
        val client = client { name, _ ->
            when (name) {
                "aggregate" -> AggregationResult(emptyMap(), emptyMap(), emptySet())
                "readRecords" -> ReadRecordsResponse(emptyList<Record>(), null)
                else -> error("Unexpected operation $name")
            }
        }
        for (service in HealthService.entries) {
            val result = source(client).read(service)
            assertEquals(service, result.service)
            assertEquals(HealthMetricStatus.NO_DATA, result.status)
        }
    }

    private fun source(client: HealthConnectClient) = HealthConnectServiceSource(client, { now }, ZoneOffset.UTC)

    // Only the external IPC boundary is doubled. Query selection, units, policy,
    // time windows and returned-result mapping execute the production adapter.
    private fun client(answer: (String, Array<out Any?>) -> Any): HealthConnectClient =
        Proxy.newProxyInstance(
            HealthConnectClient::class.java.classLoader, arrayOf(HealthConnectClient::class.java),
        ) { _, method, args -> answer(method.name, args ?: emptyArray()) } as HealthConnectClient
}
