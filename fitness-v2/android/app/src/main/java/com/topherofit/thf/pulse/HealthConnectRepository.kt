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
    val missingReadPermissions: Set<String>,
    val missingWritePermissions: Set<String>,
    val missingPermissions: Set<String>,
)

data class HealthRecordEvidence(
    val recordId: String,
    val canonicalKey: String,
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
                missingReadPermissions = READ_PERMISSIONS,
                missingWritePermissions = WRITE_PERMISSIONS,
                missingPermissions = REQUIRED_PERMISSIONS,
            )
        val granted = client.permissionController.getGrantedPermissions()
        val missingRead = READ_PERMISSIONS - granted
        val missingWrite = WRITE_PERMISSIONS - granted
        val missing = missingRead + missingWrite
        val readsGranted = missingRead.isEmpty()
        val writesGranted = missingWrite.isEmpty()
        return HealthConnectionState(
            availability = availability(),
            connected = readsGranted,
            readPermissionsGranted = readsGranted,
            writePermissionsGranted = writesGranted,
            grantedPermissions = granted,
            missingReadPermissions = missingRead,
            missingWritePermissions = missingWrite,
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
        val verifiedEvidenceByKey = evidence
            .asSequence()
            .filter { it.verifiedForRewards }
            .groupBy { it.canonicalKey }
            .mapValues { (_, versions) ->
                versions.maxWithOrNull(compareBy<HealthRecordEvidence> { it.clientRecordVersion }.thenBy { it.lastModifiedTime })!!
            }
        val verifiedKeys = verifiedEvidenceByKey.keys
        val verifiedCount = verifiedKeys.size
        val verifiedEvidenceCount = evidence.count { it.verifiedForRewards }
        val duplicateRecordsExcluded = verifiedEvidenceCount - verifiedCount

        val origins = evidence.map { it.dataOrigin }.filter { it.isNotBlank() }.toSet()

        return HealthSnapshot(
            steps = steps.filter { it.healthRecordKey() in verifiedKeys }.distinctBy { it.healthRecordKey() }.sumOf { it.count },
            distanceMeters = distances.filter { it.healthRecordKey() in verifiedKeys }.distinctBy { it.healthRecordKey() }.sumOf { it.distance.inMeters },
            activeCaloriesKcal = calories.filter { it.healthRecordKey() in verifiedKeys }.distinctBy { it.healthRecordKey() }.sumOf { it.energy.inKilocalories },
            exerciseSessions = sessions.filter { it.healthRecordKey() in verifiedKeys }.distinctBy { it.healthRecordKey() }.size,
            origins = origins,
            latestSessionEnd = sessions.filter { it.healthRecordKey() in verifiedKeys }.maxOfOrNull { it.endTime },
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
        val recordType = this::class.simpleName ?: "Record"
        val trustedMethod = method == Metadata.RECORDING_METHOD_ACTIVELY_RECORDED ||
            method == Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED
        val assessment = HealthRecordEvidencePolicy.assess(
            appPackageName = context.packageName,
            dataOrigin = origin,
            recordType = recordType,
            recordId = metadata.id,
            trustedRecordingMethod = trustedMethod,
        )
        return HealthRecordEvidence(
            recordId = metadata.id,
            canonicalKey = WorkoutIdentity.stableHealthRecordKey(origin, recordType, metadata.id),
            clientRecordId = metadata.clientRecordId,
            clientRecordVersion = metadata.clientRecordVersion,
            lastModifiedTime = metadata.lastModifiedTime,
            recordType = recordType,
            dataOrigin = origin,
            recordingMethod = method,
            deviceType = device?.type,
            deviceManufacturer = device?.manufacturer,
            deviceModel = device?.model,
            verifiedForRewards = assessment.verifiedForRewards,
            verificationReason = assessment.reason,
        )
    }

    private fun Record.healthRecordKey(): String = WorkoutIdentity.stableHealthRecordKey(
        dataOrigin = metadata.dataOrigin.packageName,
        recordType = this::class.simpleName ?: "Record",
        recordId = metadata.id,
    )

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
