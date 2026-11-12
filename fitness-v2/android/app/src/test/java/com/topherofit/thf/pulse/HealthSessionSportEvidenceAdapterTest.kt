package com.topherofit.thf.pulse

import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.metadata.Device
import java.time.Instant
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthSessionSportEvidenceAdapterTest {
    private val source = "com.sec.android.app.shealth"
    private val rawRecordId = "provider-private-record-123"
    private val rawClientRecordId = "private-client-record-456"

    private fun evidence(
        exerciseType: Int = ExerciseSessionRecord.EXERCISE_TYPE_RUNNING,
        deviceType: Int? = Device.TYPE_WATCH,
        integrity: IntegrityClass = IntegrityClass.VERIFIED,
        verified: Boolean = true,
        start: Instant = Instant.parse("2026-11-12T10:00:00Z"),
        end: Instant = Instant.parse("2026-11-12T10:30:00Z"),
        dataOrigin: String = source,
        recordType: String = HealthRecordType.EXERCISE_SESSION.stableId,
        canonicalKey: String = WorkoutIdentity.stableHealthRecordKey(
            source, HealthRecordType.EXERCISE_SESSION.stableId, rawRecordId,
        ),
        session: HealthExerciseSessionDetails? = HealthExerciseSessionDetails(exerciseType, start, end),
    ) = HealthRecordEvidence(
        recordId = rawRecordId,
        canonicalKey = canonicalKey,
        clientRecordId = rawClientRecordId,
        clientRecordVersion = 1L,
        lastModifiedTime = Instant.parse("2026-11-12T10:31:00Z"),
        recordType = recordType,
        dataOrigin = dataOrigin,
        recordingMethod = 2,
        deviceType = deviceType,
        deviceManufacturer = "private-manufacturer",
        deviceModel = "private-model",
        integrityClass = integrity,
        verifiedForRewards = verified,
        verificationReason = "TEST_FIXTURE_ONLY",
        exerciseSession = session,
    )

    @Test
    fun walking_running_and_biking_keep_the_real_session_interval() {
        val cases = listOf(
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING to SportKind.WALKING,
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING to SportKind.RUNNING,
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING to SportKind.CYCLING,
        )
        for ((exerciseType, expectedSport) in cases) {
            val mapped = HealthSessionSportEvidenceAdapter.toSportEvidence(
                evidence(exerciseType = exerciseType),
            )
            assertNotNull(mapped)
            assertEquals(expectedSport, mapped!!.sport)
            assertEquals(Instant.parse("2026-11-12T10:00:00Z").toEpochMilli(), mapped.startEpochMillis)
            assertEquals(Instant.parse("2026-11-12T10:30:00Z").toEpochMilli(), mapped.endEpochMillis)
            assertEquals(source, mapped.sourcePackage)
            assertEquals(EvidenceOrigin.HEALTH_WEARABLE, mapped.origin)
            assertFalse(mapped.hasAcceptedGps)
        }
    }

    @Test
    fun treadmill_and_stationary_bike_records_are_not_matched_to_outdoor_gps() {
        val unsupported = listOf(
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING_TREADMILL,
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING_TREADMILL,
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING_STATIONARY,
        )
        for (exerciseType in unsupported) {
            assertNull(
                HealthSessionSportEvidenceAdapter.toSportEvidence(
                    evidence(exerciseType = exerciseType),
                ),
            )
        }
    }

    @Test
    fun swimming_pool_and_open_water_keep_distinct_sport_kinds() {
        val pool = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL),
        )
        val openWater = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_OPEN_WATER),
        )
        assertEquals(SportKind.SWIMMING_POOL, pool?.sport)
        assertEquals(SportKind.SWIMMING_OPEN_WATER, openWater?.sport)
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(pool!!))
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(openWater!!))
    }

    @Test
    fun phone_health_records_are_imported_not_mislabeled_as_wearable_evidence() {
        val mapped = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(deviceType = Device.TYPE_PHONE),
        )!!
        assertEquals(EvidenceOrigin.HEALTH_IMPORTED, mapped.origin)
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(mapped))
    }

    @Test
    fun manual_and_rejected_records_never_gain_competition_trust() {
        val manual = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(integrity = IntegrityClass.MANUAL, verified = false),
        )!!
        val rejected = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(integrity = IntegrityClass.REJECTED, verified = false),
        )!!
        assertEquals(CompetitionTrust.MANUAL, WearableProvenancePolicy.classify(manual))
        assertTrue(rejected.anomalyRejected)
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(rejected))
    }

    @Test
    fun unknown_provider_or_incompatible_device_stays_imported() {
        val unknownProvider = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(dataOrigin = "com.example.unreviewed.health", verified = false),
        )!!
        val ring = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(deviceType = Device.TYPE_RING, verified = false),
        )!!
        assertEquals(EvidenceOrigin.HEALTH_IMPORTED, unknownProvider.origin)
        assertEquals(EvidenceOrigin.HEALTH_IMPORTED, ring.origin)
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(unknownProvider))
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(ring))
    }

    @Test
    fun stable_hashed_key_is_forwarded_without_raw_provider_or_client_ids() {
        val mapped = HealthSessionSportEvidenceAdapter.toSportEvidence(evidence())!!
        assertTrue(mapped.recordId!!.matches(Regex("^thf-health-[0-9a-f]{40}$")))
        assertFalse(mapped.recordId!!.contains(rawRecordId))
        assertFalse(mapped.toString().contains(rawRecordId))
        assertFalse(mapped.toString().contains(rawClientRecordId))
    }

    @Test
    fun incomplete_identity_invalid_time_and_non_session_records_fail_closed() {
        val blankSource = evidence(dataOrigin = " ")
        val badKey = evidence(canonicalKey = "provider-private-record-123")
        val invalidInterval = evidence(
            start = Instant.parse("2026-11-12T10:30:00Z"),
            end = Instant.parse("2026-11-12T10:00:00Z"),
        )
        val missingSession = evidence(session = null)
        val metricRecord = evidence(recordType = HealthRecordType.STEPS.stableId)
        assertNull(HealthSessionSportEvidenceAdapter.toSportEvidence(blankSource))
        assertNull(HealthSessionSportEvidenceAdapter.toSportEvidence(badKey))
        assertNull(HealthSessionSportEvidenceAdapter.toSportEvidence(invalidInterval))
        assertNull(HealthSessionSportEvidenceAdapter.toSportEvidence(missingSession))
        assertNull(HealthSessionSportEvidenceAdapter.toSportEvidence(metricRecord))
    }

    @Test
    fun only_cross_source_walk_run_cycle_pairs_use_time_proximity_deduplication() {
        val cases = listOf(
            ExerciseSessionRecord.EXERCISE_TYPE_WALKING to SportKind.WALKING,
            ExerciseSessionRecord.EXERCISE_TYPE_RUNNING to SportKind.RUNNING,
            ExerciseSessionRecord.EXERCISE_TYPE_BIKING to SportKind.CYCLING,
        )
        for ((exerciseType, sport) in cases) {
            val health = HealthSessionSportEvidenceAdapter.toSportEvidence(
                evidence(exerciseType = exerciseType),
            )!!
            val phone = SportEvidence(
                sport = sport,
                origin = EvidenceOrigin.PHONE_MEASURED,
                startEpochMillis = health.startEpochMillis + 30_000L,
                endEpochMillis = health.endEpochMillis + 30_000L,
                hasAcceptedGps = true,
            )
            assertTrue(WearableProvenancePolicy.isDuplicate(phone, health))
            val secondHealthSession = health.copy(recordId = "thf-health-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
            assertFalse(WearableProvenancePolicy.isDuplicate(health, secondHealthSession))
        }
    }

    @Test
    fun swimming_never_time_deduplicates_against_phone_activity() {
        val health = HealthSessionSportEvidenceAdapter.toSportEvidence(
            evidence(exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_SWIMMING_POOL),
        )!!
        val phone = SportEvidence(
            sport = SportKind.SWIMMING_POOL,
            origin = EvidenceOrigin.PHONE_MEASURED,
            startEpochMillis = health.startEpochMillis,
            endEpochMillis = health.endEpochMillis,
            hasAcceptedGps = true,
        )
        assertFalse(WearableProvenancePolicy.isDuplicate(phone, health))
    }
}
