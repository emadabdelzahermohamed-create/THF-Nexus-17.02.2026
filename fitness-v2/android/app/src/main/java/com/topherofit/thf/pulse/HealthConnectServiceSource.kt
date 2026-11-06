package com.topherofit.thf.pulse

import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.aggregate.AggregateMetric
import androidx.health.connect.client.aggregate.AggregationResult
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.ZoneId
import java.time.temporal.ChronoUnit
import kotlin.reflect.KClass

class HealthConnectServiceSource(
    private val client: HealthConnectClient,
    private val now: () -> Instant = Instant::now,
    private val zone: ZoneId = ZoneId.systemDefault(),
) : HealthServiceSource {
    override suspend fun grantedPermissions(): Set<String> = client.permissionController.getGrantedPermissions()

    override suspend fun read(service: HealthService): HealthMetricResult {
        val end = now()
        val today = end.atZone(zone).toLocalDate().atStartOfDay(zone).toInstant()
        return when (service) {
            HealthService.STEPS -> aggregate(service, StepsRecord.COUNT_TOTAL, today, end, "steps") { it.toDouble() }
            HealthService.DISTANCE -> aggregate(service, DistanceRecord.DISTANCE_TOTAL, today, end, "km") { it.inKilometers }
            HealthService.ACTIVE_CALORIES -> aggregate(service, ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL, today, end, "kcal") { it.inKilocalories }
            HealthService.TOTAL_CALORIES -> aggregate(service, TotalCaloriesBurnedRecord.ENERGY_TOTAL, today, end, "kcal") { it.inKilocalories }
            HealthService.HEART_RATE -> aggregate(service, HeartRateRecord.BPM_AVG, today, end, "bpm") { it.toDouble() }
            HealthService.SPEED -> aggregate(service, SpeedRecord.SPEED_MAX, today, end, "km/h") { it.inKilometersPerHour }
            HealthService.SLEEP -> aggregate(service, SleepSessionRecord.SLEEP_DURATION_TOTAL, end.minus(7, ChronoUnit.DAYS), end, "min") { it.toMillis() / 60000.0 }
            HealthService.EXERCISE -> readExerciseRecords(end)
            HealthService.WEIGHT -> latest(service, WeightRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.weight.inKilograms, "kg")) }
            HealthService.HEIGHT -> latest(service, HeightRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.height.inMeters * 100.0, "cm")) }
            HealthService.BODY_FAT -> latest(service, BodyFatRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.percentage.value, "%")) }
            HealthService.BASAL_METABOLIC_RATE -> latest(service, BasalMetabolicRateRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.basalMetabolicRate.inKilocaloriesPerDay, "kcal/day")) }
            HealthService.RESTING_HEART_RATE -> latest(service, RestingHeartRateRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.beatsPerMinute.toDouble(), "bpm")) }
            HealthService.OXYGEN_SATURATION -> latest(service, OxygenSaturationRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.percentage.value, "%")) }
            HealthService.VO2_MAX -> latest(service, Vo2MaxRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.vo2MillilitersPerMinuteKilogram, "mL/kg/min")) }
            HealthService.BLOOD_PRESSURE -> latest(service, BloodPressureRecord::class, end, { it.time }) { listOf(
                HealthMetricValue(it.systolic.inMillimetersOfMercury, "mmHg", "انقباضي", "Systolic"),
                HealthMetricValue(it.diastolic.inMillimetersOfMercury, "mmHg", "انبساطي", "Diastolic"),
            ) }
            HealthService.BLOOD_GLUCOSE -> latest(service, BloodGlucoseRecord::class, end, { it.time }) { listOf(HealthMetricValue(it.level.inMillimolesPerLiter, "mmol/L")) }
            HealthService.NUTRITION -> latest(service, NutritionRecord::class, end, { it.endTime }) { meal -> listOfNotNull(
                meal.energy?.let { HealthMetricValue(it.inKilocalories, "kcal", "طاقة السجل", "Record energy") },
                meal.protein?.let { HealthMetricValue(it.inGrams, "g", "بروتين", "Protein") },
                meal.totalCarbohydrate?.let { HealthMetricValue(it.inGrams, "g", "كربوهيدرات", "Carbohydrate") },
                meal.totalFat?.let { HealthMetricValue(it.inGrams, "g", "دهون", "Fat") },
            ) }
        }
    }

    private suspend fun <T : Any> aggregate(
        service: HealthService, metric: AggregateMetric<T>, start: Instant, end: Instant,
        unit: String, value: (T) -> Double,
    ): HealthMetricResult {
        val result: AggregationResult = client.aggregate(AggregateRequest(
            metrics = setOf(metric), timeRangeFilter = TimeRangeFilter.between(start, end),
        ))
        val values = result[metric]?.let { listOf(HealthMetricValue(value(it), unit)) }.orEmpty()
        return HealthServiceAccessPolicy.measurement(service, values).copy(
            origins = result.dataOrigins.map { it.packageName }.filter { it.isNotBlank() }.toSet(),
            windowStart = start, windowEnd = end,
        )
    }

    private suspend fun <T : Record> latest(
        service: HealthService, type: KClass<T>, end: Instant,
        observedAt: (T) -> Instant, values: (T) -> List<HealthMetricValue>,
    ): HealthMetricResult {
        val record = client.readRecords(ReadRecordsRequest(
            recordType = type,
            timeRangeFilter = TimeRangeFilter.between(end.minus(28, ChronoUnit.DAYS), end),
            ascendingOrder = false, pageSize = 1,
        )).records.firstOrNull() ?: return HealthMetricResult(service, HealthMetricStatus.NO_DATA)
        return HealthServiceAccessPolicy.measurement(service, values(record)).copy(
            origins = setOf(record.metadata.dataOrigin.packageName).filter { it.isNotBlank() }.toSet(),
            observedAt = observedAt(record), recordingMethod = record.metadata.recordingMethod,
        )
    }

    private suspend fun readExerciseRecords(end: Instant): HealthMetricResult {
        val start = end.minus(7, ChronoUnit.DAYS)
        val keys = mutableSetOf<String>()
        val origins = mutableSetOf<String>()
        var page: String? = null
        do {
            val response = client.readRecords(ReadRecordsRequest(
                recordType = ExerciseSessionRecord::class,
                timeRangeFilter = TimeRangeFilter.between(start, end), pageSize = 1000, pageToken = page,
            ))
            response.records.forEach { record ->
                val origin = record.metadata.dataOrigin.packageName
                keys += "$origin/${record.metadata.id}"
                if (origin.isNotBlank()) origins += origin
            }
            page = response.pageToken
        } while (page != null)
        return HealthServiceAccessPolicy.measurement(HealthService.EXERCISE,
            if (keys.isEmpty()) emptyList() else listOf(HealthMetricValue(keys.size.toDouble(), "records")),
        ).copy(origins = origins, windowStart = start, windowEnd = end)
    }
}
