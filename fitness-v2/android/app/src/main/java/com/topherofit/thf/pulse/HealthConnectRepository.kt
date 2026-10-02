package com.topherofit.thf.pulse

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ActiveCaloriesBurnedRecord
import androidx.health.connect.client.records.DistanceRecord
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.Record
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.metadata.Device
import androidx.health.connect.client.records.metadata.Metadata
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.ZoneId
import java.time.temporal.ChronoUnit
import kotlin.reflect.KClass

data class HealthConnectionState(
    val availability: String,
    val connected: Boolean,
    val grantedPermissions: Set<String>,
    val missingPermissions: Set<String>,
)

data class HealthSnapshot(
    val steps: Long,
    val distanceMeters: Double,
    val activeCaloriesKcal: Double,
    val exerciseSessions: Int,
    val origins: Set<String>,
    val latestSessionEnd: Instant?,
)

data class WorkoutForHealth(
    val clientRecordId: String,
    val clientRecordVersion: Long,
    val exerciseId: String,
    val sport: String,
    val title: String,
    val startTime: Instant,
    val endTime: Instant,
    val notes: String?,
)

class HealthConnectRepository(private val context: Context) {
    companion object {
        val REQUIRED_PERMISSIONS: Set<String> = setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(ExerciseSessionRecord::class),
            HealthPermission.getWritePermission(ExerciseSessionRecord::class),
            HealthPermission.getReadPermission(DistanceRecord::class),
            HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        )
    }

    private fun sdkStatus(): Int = HealthConnectClient.getSdkStatus(context)

    private fun clientOrNull(): HealthConnectClient? =
        if (sdkStatus() == HealthConnectClient.SDK_AVAILABLE) HealthConnectClient.getOrCreate(context) else null

    fun availability(): String = when (sdkStatus()) {
        HealthConnectClient.SDK_AVAILABLE -> "AVAILABLE"
        HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> "PROVIDER_UPDATE_REQUIRED"
        else -> "UNAVAILABLE"
    }

    suspend fun connectionState(): HealthConnectionState {
        val client = clientOrNull()
            ?: return HealthConnectionState(availability(), false, emptySet(), REQUIRED_PERMISSIONS)
        val granted = client.permissionController.getGrantedPermissions()
        val missing = REQUIRED_PERMISSIONS - granted
        return HealthConnectionState(availability(), missing.isEmpty(), granted, missing)
    }

    suspend fun readRecent(days: Long = 7): HealthSnapshot {
        val client = requireNotNull(clientOrNull()) { "Health Connect is unavailable" }
        val granted = client.permissionController.getGrantedPermissions()
        require(granted.containsAll(REQUIRED_PERMISSIONS.filterNot { it.contains("WRITE_") })) {
            "Health Connect read permissions are missing"
        }

        val end = Instant.now()
        val start = end.minus(days, ChronoUnit.DAYS)
        val steps = readAll(client, StepsRecord::class, start, end)
        val distances = readAll(client, DistanceRecord::class, start, end)
        val calories = readAll(client, ActiveCaloriesBurnedRecord::class, start, end)
        val sessions = readAll(client, ExerciseSessionRecord::class, start, end)

        val origins = buildSet {
            steps.mapTo(this) { it.metadata.dataOrigin.packageName }
            distances.mapTo(this) { it.metadata.dataOrigin.packageName }
            calories.mapTo(this) { it.metadata.dataOrigin.packageName }
            sessions.mapTo(this) { it.metadata.dataOrigin.packageName }
        }.filter { it.isNotBlank() }.toSet()

        return HealthSnapshot(
            steps = steps.sumOf { it.count },
            distanceMeters = distances.sumOf { it.distance.inMeters },
            activeCaloriesKcal = calories.sumOf { it.energy.inKilocalories },
            exerciseSessions = sessions.size,
            origins = origins,
            latestSessionEnd = sessions.maxOfOrNull { it.endTime },
        )
    }

    suspend fun writeWorkout(workout: WorkoutForHealth) {
        val client = requireNotNull(clientOrNull()) { "Health Connect is unavailable" }
        val writePermission = HealthPermission.getWritePermission(ExerciseSessionRecord::class)
        require(writePermission in client.permissionController.getGrantedPermissions()) {
            "Health Connect exercise write permission is missing"
        }
        require(workout.endTime.isAfter(workout.startTime)) { "Workout end must be after start" }

        val zone = ZoneId.systemDefault().rules.getOffset(workout.startTime)
        val record = ExerciseSessionRecord(
            startTime = workout.startTime,
            startZoneOffset = zone,
            endTime = workout.endTime,
            endZoneOffset = ZoneId.systemDefault().rules.getOffset(workout.endTime),
            exerciseType = HealthSportMapper.toExerciseType(workout.sport, workout.exerciseId),
            title = workout.title.take(120),
            notes = workout.notes?.take(500),
            metadata = Metadata.activelyRecorded(
                clientRecordId = workout.clientRecordId,
                clientRecordVersion = workout.clientRecordVersion,
                device = Device(type = Device.TYPE_PHONE),
            ),
        )
        client.insertRecords(listOf(record))
    }

    private suspend fun <T : Record> readAll(
        client: HealthConnectClient,
        type: KClass<T>,
        start: Instant,
        end: Instant,
    ): List<T> {
        val records = mutableListOf<T>()
        var pageToken: String? = null
        do {
            val response = client.readRecords(
                ReadRecordsRequest(
                    recordType = type,
                    timeRangeFilter = TimeRangeFilter.between(start, end),
                    ascendingOrder = false,
                    pageSize = 1000,
                    pageToken = pageToken,
                ),
            )
            records += response.records
            pageToken = response.pageToken
        } while (pageToken != null)
        return records
    }
}
