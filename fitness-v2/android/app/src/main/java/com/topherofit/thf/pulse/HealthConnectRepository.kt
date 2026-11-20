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
    /** True when at least one core read metric is accessible; partial grants are usable. */
    val connected: Boolean,
    /** True only when every currently requested core read permission is granted. */
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
    val integrityClass: IntegrityClass,
    val verifiedForRewards: Boolean,
    val verificationReason: String,
    /** Raw session fields retained internally for sport-specific provenance checks. */
    val exerciseType: Int? = null,
    val startEpochMillis: Long? = null,
    val endEpochMillis: Long? = null,
    /** Read-boundary clock used to reject future-dated imported sessions. */
    val observedAtEpochMillis: Long? = null,
)

data class HealthSnapshot(
    /** Null means the matching permission is absent; zero means granted with no records. */
    val steps: Long?,
    val distanceMeters: Double?,
    val activeCaloriesKcal: Double?,
    val exerciseSessions: Int?,
    val origins: Set<String>,
    val latestSessionEnd: Instant?,
    val recordsRead: Int,
    val verifiedRecords: Int,
    val excludedManualOrUnknownRecords: Int,
    val duplicateRecordsExcluded: Int,
    val recordEvidence: List<HealthRecordEvidence>,
    val dataReadSuccessfully: Boolean,
    val hasVerifiedRewardData: Boolean,
) {
    /**
     * Privacy-reduced per-record source metadata for UI/bridge consumers.
     * Raw provider/client IDs and device manufacturer/model are not exposed.
     */
    val recordProvenance: List<HealthRecordProvenanceSummary>
        get() = recordEvidence.map(HealthRecordProvenancePresentationPolicy::summarize)
}

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
    private data class HealthRecordEntry(
        val record: Record,
        val evidence: HealthRecordEvidence,
    )

    companion object {
        val READ_PERMISSION_BY_METRIC: Map<HealthReadMetric, String> = linkedMapOf(
            HealthReadMetric.STEPS to HealthPermission.getReadPermission(StepsRecord::class),
            HealthReadMetric.EXERCISE_SESSIONS to HealthPermission.getReadPermission(ExerciseSessionRecord::class),
            HealthReadMetric.DISTANCE to HealthPermission.getReadPermission(DistanceRecord::class),
            HealthReadMetric.ACTIVE_CALORIES to HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        )
        val READ_PERMISSIONS: Set<String> = READ_PERMISSION_BY_METRIC.values.toSet()
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
        val readPlan = HealthReadPermissionPolicy.plan(granted, READ_PERMISSION_BY_METRIC)
        val missingRead = readPlan.missingPermissions
        val missingWrite = WRITE_PERMISSIONS - granted
        val missing = missingRead + missingWrite
        val readsGranted = readPlan.hasAllReadPermissions
        val writesGranted = missingWrite.isEmpty()
        return HealthConnectionState(
            availability = availability(),
            connected = readPlan.hasAnyReadPermission,
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
        val readPlan = HealthReadPermissionPolicy.plan(granted, READ_PERMISSION_BY_METRIC)
        require(readPlan.hasAnyReadPermission) {
            "At least one Health Connect read permission is required"
        }

        val end = Instant.now()
        val start = end.minus(days, ChronoUnit.DAYS)
        // Read only record types for which the user granted the matching permission.
        // Missing permissions stay null in HealthSnapshot; they are never represented as zero.
        val steps = if (readPlan.canRead(HealthReadMetric.STEPS)) {
            readAll(client, StepsRecord::class, start, end)
        } else {
            emptyList()
        }
        val distances = if (readPlan.canRead(HealthReadMetric.DISTANCE)) {
            readAll(client, DistanceRecord::class, start, end)
        } else {
            emptyList()
        }
        val calories = if (readPlan.canRead(HealthReadMetric.ACTIVE_CALORIES)) {
            readAll(client, ActiveCaloriesBurnedRecord::class, start, end)
        } else {
            emptyList()
        }
        val sessions = if (readPlan.canRead(HealthReadMetric.EXERCISE_SESSIONS)) {
            readAll(client, ExerciseSessionRecord::class, start, end)
        } else {
            emptyList()
        }
        val allRecords: List<Record> = steps + distances + calories + sessions
        val entries = allRecords.map { record -> HealthRecordEntry(record, record.toEvidence(end)) }
        // Use the same selected record version for both evidence and metric aggregation.
        // Stable identity is source + explicit record type + provider record ID. Records
        // without complete identity are never collapsed into one synthetic duplicate group.
        val deduplication = HealthRecordDeduplicationPolicy.selectLatest(
            entries.map { entry ->
                HealthRecordVersion(
                    stableKey = entry.evidence.canonicalKey.takeIf {
                        entry.evidence.dataOrigin.isNotBlank() &&
                            entry.evidence.recordType.isNotBlank() &&
                            entry.evidence.recordId.isNotBlank()
                    },
                    clientRecordVersion = entry.evidence.clientRecordVersion,
                    lastModifiedTime = entry.evidence.lastModifiedTime,
                    value = entry,
                )
            },
        )
        val sourceSelectedEntries = deduplication.selected.map { it.value }
        // Provider record IDs deduplicate versions within a source. Reconcile exact mirrored
        // metric intervals across sources/record IDs, and fail closed on overlapping verified
        // intervals whose values cannot be safely apportioned. Preserve every source label in
        // recordEvidence; only accepted entries can contribute to reward totals.
        val metricCandidates = sourceSelectedEntries.mapIndexedNotNull { index, entry ->
            entry.toMetricSourceCandidate(index)
        }
        val metricCandidateIndices = metricCandidates.map { it.originalIndex }.toSet()
        val metricReconciliation = HealthMetricSourceReconciliationPolicy.reconcile(metricCandidates)
        val reconciledByIndex = mutableMapOf<Int, HealthRecordEntry>()
        metricReconciliation.accepted.forEach { candidate ->
            reconciledByIndex[candidate.originalIndex] = candidate.value
        }
        metricReconciliation.duplicates.forEach { candidate ->
            val duplicate = candidate.value
            // Preserve an existing manual, unknown-provider or anomaly reason. Only a
            // previously verified duplicate is downgraded specifically for mirror exclusion.
            reconciledByIndex[candidate.originalIndex] =
                if (duplicate.evidence.verifiedForRewards) {
                    duplicate.withProvenanceFailure("DUPLICATE_METRIC_INTERVAL")
                } else {
                    duplicate
                }
        }
        metricReconciliation.ambiguous.forEach { candidate ->
            reconciledByIndex[candidate.originalIndex] =
                candidate.value.withProvenanceFailure("OVERLAPPING_METRIC_INTERVAL_AMBIGUOUS")
        }
        sourceSelectedEntries.forEachIndexed { index, entry ->
            if (index !in metricCandidateIndices) reconciledByIndex[index] = entry
        }

        // Reconcile walking/running/cycling Health Connect sessions after provider-version
        // selection. Near-identical sessions with one sport label are mirrored records;
        // conflicting sport labels are ambiguous and must not inflate verified session counts.
        val sessionCandidates = sourceSelectedEntries.mapIndexedNotNull { index, entry ->
            val session = entry.record as? ExerciseSessionRecord ?: return@mapIndexedNotNull null
            val activityKind = HealthExerciseSessionReconciliationPolicy.kindForExerciseType(
                session.exerciseType,
            ) ?: return@mapIndexedNotNull null
            HealthExerciseSessionCandidate(
                originalIndex = index,
                sourcePackage = entry.evidence.dataOrigin,
                recordId = entry.evidence.recordId,
                activityKind = activityKind,
                startTime = session.startTime,
                endTime = session.endTime,
                observedAt = entry.evidence.observedAtEpochMillis?.let(Instant::ofEpochMilli),
                deviceType = entry.evidence.deviceType,
                verifiedForRewards = entry.evidence.verifiedForRewards,
                lastModifiedTime = entry.evidence.lastModifiedTime,
                value = entry,
            )
        }
        val sessionReconciliation = HealthExerciseSessionReconciliationPolicy.reconcile(sessionCandidates)
        sessionReconciliation.accepted.forEach { candidate ->
            reconciledByIndex[candidate.originalIndex] = candidate.value
        }
        sessionReconciliation.duplicates.forEach { candidate ->
            reconciledByIndex[candidate.originalIndex] =
                candidate.value.withProvenanceFailure("DUPLICATE_ACTIVITY_SESSION")
        }
        sessionReconciliation.ambiguous.forEach { candidate ->
            reconciledByIndex[candidate.originalIndex] =
                candidate.value.withProvenanceFailure("CONFLICTING_ACTIVITY_TYPE_AMBIGUOUS")
        }
        sessionReconciliation.invalid.forEach { rejection ->
            reconciledByIndex[rejection.originalIndex] =
                rejection.value.withProvenanceFailure(rejection.reason)
        }

        val reconciledEntries = reconciledByIndex.toSortedMap().values.toList()
        val verifiedEntries = reconciledEntries.filter { it.evidence.verifiedForRewards }
        val verifiedCount = verifiedEntries.size
        val excludedUnverifiedCount = entries.count { !it.evidence.verifiedForRewards }
        val origins = reconciledEntries.map { it.evidence.dataOrigin }.filter { it.isNotBlank() }.toSet()

        val verifiedSteps = verifiedEntries.mapNotNull { it.record as? StepsRecord }
        val verifiedDistances = verifiedEntries.mapNotNull { it.record as? DistanceRecord }
        val verifiedCalories = verifiedEntries.mapNotNull { it.record as? ActiveCaloriesBurnedRecord }
        val verifiedSessions = verifiedEntries.mapNotNull { it.record as? ExerciseSessionRecord }

        return HealthSnapshot(
            steps = readPlan.valueIfReadable(
                HealthReadMetric.STEPS,
                verifiedSteps.sumOf { it.count },
            ),
            distanceMeters = readPlan.valueIfReadable(
                HealthReadMetric.DISTANCE,
                verifiedDistances.sumOf { it.distance.inMeters },
            ),
            activeCaloriesKcal = readPlan.valueIfReadable(
                HealthReadMetric.ACTIVE_CALORIES,
                verifiedCalories.sumOf { it.energy.inKilocalories },
            ),
            exerciseSessions = readPlan.valueIfReadable(
                HealthReadMetric.EXERCISE_SESSIONS,
                verifiedSessions.size,
            ),
            origins = origins,
            latestSessionEnd = readPlan.valueIfReadable(
                HealthReadMetric.EXERCISE_SESSIONS,
                verifiedSessions.maxOfOrNull { it.endTime },
            ),
            recordsRead = allRecords.size,
            verifiedRecords = verifiedCount,
            excludedManualOrUnknownRecords = excludedUnverifiedCount,
            duplicateRecordsExcluded = deduplication.duplicateCount + metricReconciliation.duplicateCount + sessionReconciliation.duplicateCount,
            recordEvidence = reconciledEntries.map { it.evidence },
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

    private fun HealthRecordEntry.toMetricSourceCandidate(
        originalIndex: Int,
    ): HealthMetricSourceCandidate<HealthRecordEntry>? {
        val source = evidence.dataOrigin.trim().takeIf { it.isNotEmpty() } ?: return null
        return when (val metric = record) {
            is StepsRecord -> HealthMetricSourceCandidate(
                originalIndex = originalIndex,
                sourcePackage = source,
                recordId = evidence.recordId.trim(),
                metricType = HealthRecordType.STEPS.stableId,
                startTime = metric.startTime,
                endTime = metric.endTime,
                valueFingerprint = metric.count.toString(),
                verifiedForRewards = evidence.verifiedForRewards,
                lastModifiedTime = evidence.lastModifiedTime,
                value = this,
            )
            is DistanceRecord -> HealthMetricSourceCandidate(
                originalIndex = originalIndex,
                sourcePackage = source,
                recordId = evidence.recordId.trim(),
                metricType = HealthRecordType.DISTANCE.stableId,
                startTime = metric.startTime,
                endTime = metric.endTime,
                valueFingerprint = metric.distance.inMeters.metricFingerprint(),
                verifiedForRewards = evidence.verifiedForRewards,
                lastModifiedTime = evidence.lastModifiedTime,
                value = this,
            )
            is ActiveCaloriesBurnedRecord -> HealthMetricSourceCandidate(
                originalIndex = originalIndex,
                sourcePackage = source,
                recordId = evidence.recordId.trim(),
                metricType = HealthRecordType.ACTIVE_CALORIES.stableId,
                startTime = metric.startTime,
                endTime = metric.endTime,
                valueFingerprint = metric.energy.inKilocalories.metricFingerprint(),
                verifiedForRewards = evidence.verifiedForRewards,
                lastModifiedTime = evidence.lastModifiedTime,
                value = this,
            )
            else -> null
        }
    }

    private fun Double.metricFingerprint(): String =
        if (this == 0.0) "0" else toBits().toString(16)

    private fun HealthRecordEntry.withProvenanceFailure(reason: String): HealthRecordEntry =
        copy(
            evidence = evidence.copy(
                integrityClass = IntegrityClass.SUPPORTED,
                verifiedForRewards = false,
                verificationReason = reason,
            ),
        )

    private fun Record.toEvidence(observedAt: Instant): HealthRecordEvidence {
        val method = metadata.recordingMethod
        val device = metadata.device
        val origin = metadata.dataOrigin.packageName
        val recordType = stableRecordType()
        val trustedMethod = method == Metadata.RECORDING_METHOD_ACTIVELY_RECORDED ||
            method == Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED
        val session = this as? ExerciseSessionRecord
        val assessment = HealthRecordEvidencePolicy.assess(
            appPackageName = context.packageName,
            dataOrigin = origin,
            recordType = recordType,
            recordId = metadata.id,
            trustedRecordingMethod = trustedMethod,
            deviceType = device?.type,
            recordingMethod = method,
            exerciseType = session?.exerciseType,
            startEpochMillis = session?.startTime?.toEpochMilli(),
            endEpochMillis = session?.endTime?.toEpochMilli(),
            isExerciseSession = session != null,
            observedAtEpochMillis = observedAt.toEpochMilli(),
        )
        // Health Connect metric records are source-labelled and version-deduplicated above,
        // but a reviewed writer can still emit malformed, future-dated or implausible values.
        // Keep those records visible as rejected evidence while excluding them from totals.
        val metricAnomalyReason = if (assessment.verifiedForRewards) {
            when (this) {
                is StepsRecord -> HealthMetricEvidencePolicy.assessSteps(
                    count = count,
                    start = startTime,
                    end = endTime,
                    observedAt = observedAt,
                )
                is DistanceRecord -> HealthMetricEvidencePolicy.assessDistance(
                    meters = distance.inMeters,
                    start = startTime,
                    end = endTime,
                    observedAt = observedAt,
                )
                is ActiveCaloriesBurnedRecord -> HealthMetricEvidencePolicy.assessActiveCalories(
                    kilocalories = energy.inKilocalories,
                    start = startTime,
                    end = endTime,
                    observedAt = observedAt,
                )
                else -> null
            }
        } else {
            null
        }
        val finalAssessment = metricAnomalyReason?.let { reason ->
            HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.REJECTED,
                verifiedForRewards = false,
                reason = reason,
            )
        } ?: assessment
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
            integrityClass = finalAssessment.integrityClass,
            verifiedForRewards = finalAssessment.verifiedForRewards,
            verificationReason = finalAssessment.reason,
            exerciseType = session?.exerciseType,
            startEpochMillis = session?.startTime?.toEpochMilli(),
            endEpochMillis = session?.endTime?.toEpochMilli(),
            observedAtEpochMillis = observedAt.toEpochMilli(),
        )
    }

    /**
     * Explicit stable IDs avoid using minifiable runtime class names in Health record identity.
     * readRecent() currently requests exactly these four record families.
     */
    private fun Record.stableRecordType(): String = when (this) {
        is StepsRecord -> HealthRecordType.STEPS.stableId
        is DistanceRecord -> HealthRecordType.DISTANCE.stableId
        is ActiveCaloriesBurnedRecord -> HealthRecordType.ACTIVE_CALORIES.stableId
        is ExerciseSessionRecord -> HealthRecordType.EXERCISE_SESSION.stableId
        else -> "UnknownRecord"
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
