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
    val readPermissionsGranted: Boolean,
    val writePermissionsGranted: Boolean,
    val grantedPermissions: Set<String>,
    val missingPermissions: Set<String>,
)

data class HealthRecordEvidence(
    val recordId: String,
    val clientRecordId: String?,
    val clientRecordVersion: Long,
    val lastModifiedTime: Instant,
    val recordType: String,
    val dataOrigin: String,
    val recordingMethod: Int,
    val deviceType: Int?,
    val deviceManufacturer: String?,
    val deviceModel: String?,
    val verifiedForRewards: Boolean,
    val verificationReason: String,
)

data class HealthSnapshot(
    val steps: Long,
    val distanceMeters: Double,
    val activeCaloriesKcal: Double,
    val exerciseSessions: Int,
    val origins: Set<String>,
    val latestSessionEnd: Instant?,
    val recordsRead: Int,
    val verifiedRecords: Int,
    val excludedManualOrUnknownRecords: Int,
    val duplicateRecordsExcluded: Int,
    val recordEvidence: List<HealthRecordEvidence>,
    val dataReadSuccessfully: Boolean,
    val hasVerifiedRewardData: Boolean,
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
        val READ_PERMISSIONS: Set<String> = setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(ExerciseSessionRecord::class),
            HealthPermission.getReadPermission(DistanceRecord::class),
            HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        )
        val WRITE_PERMISSIONS: Set<String> = setOf(
            HealthPermission.getWritePermission(ExerciseSessionRecord::class),
        )
        val REQUIRED_PERMISSIONS: Set<String> = READ_PERMISSIONS + WRITE_PERMISSIONS
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
            ?: return HealthConnectionState(
                availability = availability(),
                connected = false,
                readPermissionsGranted = false,
                writePermissionsGranted = false,
                grantedPermissions = emptySet(),
                missingPermissions = REQUIRED_PERMISSIONS,
            )
        val granted = client.permissionController.getGrantedPermissions()
        val missing = REQUIRED_PERMISSIONS - granted
        val readsGranted = granted.containsAll(READ_PERMISSIONS)
        val writesGranted = granted.containsAll(WRITE_PERMISSIONS)
        return HealthConnectionState(
            availability = availability(),
            connected = readsGranted,
            readPermissionsGranted = readsGranted,
            writePermissionsGranted = writesGranted,
            grantedPermissions = granted,
            missingPermissions = missing,
        )
    }

    suspend fun readRecent(days: Long = 7): HealthSnapshot {
        val client = requireNotNull(clientOrNull()) { "Health Connect is unavailable" }
        val granted = client.permissionController.getGrantedPermissions()
        require(granted.containsAll(READ_PERMISSIONS)) {
            "Health Connect read permissions are missing"
        }

        val end = Instant.now()
        val start = end.minus(days, ChronoUnit.DAYS)
        val steps = readAll(client, StepsRecord::class, start, end)
        val distances = readAll(client, DistanceRecord::class, start, end)
        val calories = readAll(client, ActiveCaloriesBurnedRecord::class, start, end)
        val sessions = readAll(client, ExerciseSessionRecord::class, start, end)
        val allRecords: List<Record> = steps + distances + calories + sessions
        val evidence = allRecords.map { it.toEvidence() }
        val verifiedEvidenceById = evidence
            .asSequence()
            .filter { it.verifiedForRewards }
            .groupBy { it.recordId }
            .mapValues { (_, versions) ->
                versions.maxWithOrNull(compareBy<HealthRecordEvidence> { it.clientRecordVersion }.thenBy { it.lastModifiedTime })!!
            }
        val verifiedIds = verifiedEvidenceById.keys
        val verifiedCount = verifiedIds.size
        val verifiedEvidenceCount = evidence.count { it.verifiedForRewards }
        val duplicateRecordsExcluded = verifiedEvidenceCount - verifiedCount

        val origins = evidence.map { it.dataOrigin }.filter { it.isNotBlank() }.toSet()

        return HealthSnapshot(
            steps = steps.filter { it.metadata.id in verifiedIds }.distinctBy { it.metadata.id }.sumOf { it.count },
            distanceMeters = distances.filter { it.metadata.id in verifiedIds }.distinctBy { it.metadata.id }.sumOf { it.distance.inMeters },
            activeCaloriesKcal = calories.filter { it.metadata.id in verifiedIds }.distinctBy { it.metadata.id }.sumOf { it.energy.inKilocalories },
            exerciseSessions = sessions.filter { it.metadata.id in verifiedIds }.distinctBy { it.metadata.id }.size,
            origins = origins,
            latestSessionEnd = sessions.filter { it.metadata.id in verifiedIds }.maxOfOrNull { it.endTime },
            recordsRead = allRecords.size,
            verifiedRecords = verifiedCount,
            excludedManualOrUnknownRecords = evidence.count { !it.verifiedForRewards },
            duplicateRecordsExcluded = duplicateRecordsExcluded,
            recordEvidence = evidence,
            dataReadSuccessfully = true,
            hasVerifiedRewardData = verifiedCount > 0,
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

    private fun Record.toEvidence(): HealthRecordEvidence {
        val method = metadata.recordingMethod
        val device = metadata.device
        val origin = metadata.dataOrigin.packageName
        val trustedMethod = method == Metadata.RECORDING_METHOD_ACTIVELY_RECORDED ||
            method == Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED
        val externalOrigin = origin.isNotBlank() && origin != context.packageName
        val hasDeviceMetadata = device != null && device.type != Device.TYPE_UNKNOWN
        // Reward verification is intentionally stricter than Health Connect acceptance:
        // a trusted recording method without device provenance is useful for history,
        // but is not sufficient evidence for a verified reward.
        val verified = trustedMethod && externalOrigin && hasDeviceMetadata
        val reason = when {
            origin.isBlank() -> "UNKNOWN_ORIGIN"
            origin == context.packageName -> "SELF_AUTHORED"
            !trustedMethod -> "MANUAL_OR_UNKNOWN_METHOD"
            !hasDeviceMetadata -> "DEVICE_PROVENANCE_MISSING"
            else -> "EXTERNAL_SENSOR_RECORDED"
        }
        return HealthRecordEvidence(
            recordId = metadata.id,
            clientRecordId = metadata.clientRecordId,
            clientRecordVersion = metadata.clientRecordVersion,
            lastModifiedTime = metadata.lastModifiedTime,
            recordType = this::class.simpleName ?: "Record",
            dataOrigin = origin,
            recordingMethod = method,
            deviceType = device?.type,
            deviceManufacturer = device?.manufacturer,
            deviceModel = device?.model,
            verifiedForRewards = verified,
            verificationReason = reason,
        )
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
