package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import java.time.Instant

/** Actual Health Connect fields needed to reconcile one exercise-session record. */
data class HealthExerciseSessionDetails(
    val exerciseType: Int,
    val startTime: Instant,
    val endTime: Instant,
)

/**
 * Converts Health Connect exercise sessions into the existing sport-evidence contract.
 *
 * This adapter preserves the Health Connect source and stable hashed record identity. It does
 * not promote imported/manual records, infer GPS, or treat treadmill/stationary sessions as
 * outdoor route evidence.
 */
internal object HealthSessionSportEvidenceAdapter {
    private val stableHealthKey = Regex("^thf-health-[0-9a-f]{40}$")

    fun toSportEvidence(record: HealthRecordEvidence): SportEvidence? {
        if (record.recordType != HealthRecordType.EXERCISE_SESSION.stableId) return null
        val session = record.exerciseSession ?: return null
        val source = record.dataOrigin.trim()
        if (source.isEmpty() || !stableHealthKey.matches(record.canonicalKey)) return null

        val start = session.startTime.toEpochMilli()
        val end = session.endTime.toEpochMilli()
        if (start < 0L || end <= start) return null

        val sport = when (session.exerciseType) {
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING -> SportKind.WALKING
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING -> SportKind.RUNNING
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING -> SportKind.CYCLING
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL -> SportKind.SWIMMING_POOL
            ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER -> SportKind.SWIMMING_OPEN_WATER
            // Treadmill and stationary-bike sessions must not be time-matched to outdoor GPS.
            else -> return null
        }

        val device = when (record.deviceType) {
            Device.TYPE_WATCH -> "watch"
            Device.TYPE_FITNESS_BAND -> "fitness_band"
            Device.TYPE_PHONE -> "phone"
            Device.TYPE_RING -> "ring"
            Device.TYPE_CHEST_STRAP -> "chest_strap"
            else -> null
        }
        val compatibleWearable = device == "watch" || device == "fitness_band"
        val origin = when {
            record.integrityClass == IntegrityClass.MANUAL -> EvidenceOrigin.MANUAL
            record.integrityClass == IntegrityClass.REJECTED -> EvidenceOrigin.UNKNOWN
            record.verifiedForRewards && compatibleWearable -> EvidenceOrigin.HEALTH_WEARABLE
            else -> EvidenceOrigin.HEALTH_IMPORTED
        }

        return SportEvidence(
            sport = sport,
            origin = origin,
            sourcePackage = source,
            deviceType = device,
            // canonicalKey is already source-scoped and hashed; never forward provider IDs.
            recordId = record.canonicalKey,
            startEpochMillis = start,
            endEpochMillis = end,
            hasAcceptedGps = false,
            anomalyRejected = record.integrityClass == IntegrityClass.REJECTED,
        )
    }
}
