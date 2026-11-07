package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WearableProvenancePolicyTest {
    private fun evidence(
        sport: SportKind,
        origin: EvidenceOrigin,
        source: String? = null,
        device: String? = null,
        gps: Boolean = false,
        start: Long = 1_000_000L,
        end: Long = 1_600_000L,
        recordId: String? = null,
        rejected: Boolean = false,
    ) = SportEvidence(sport, origin, source, device, recordId, start, end, gps, rejected)

    @Test fun swimming_requires_reviewed_wearable_health_provenance() {
        val samsung = "com.sec.android.app.shealth"
        val google = "com.google.android.apps.fitness"
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.PHONE_MEASURED, gps = true)))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "watch", recordId = "session-1")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = samsung, device = "phone", recordId = "session-1")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = samsung, device = "spoofed-device", recordId = "session-1")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = samsung, device = "wearable", recordId = "session-1")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = samsung, device = "watch")))
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = samsung, device = "watch", recordId = "session-1")))
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.HEALTH_WEARABLE, source = google, device = "smartwatch", recordId = "session-2", gps = false)))
    }

    @Test fun imported_and_manual_swimming_never_become_verified() {
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_IMPORTED, source = "health.app")))
        assertEquals(CompetitionTrust.MANUAL, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.MANUAL)))
    }

    @Test fun wearable_origin_without_reviewed_writer_or_compatible_device_is_not_trusted() {
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "phone", recordId = "record-1")))
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "fitness_tracker", recordId = "record-1")))
    }

    @Test fun unreviewed_health_writers_cannot_become_trusted_for_walk_run_or_cycle() {
        for (sport in listOf(SportKind.WALKING, SportKind.RUNNING, SportKind.CYCLING)) {
            val unreviewed = evidence(sport, EvidenceOrigin.HEALTH_WEARABLE, source = "com.example.health", device = "watch", recordId = "record-1")
            val reviewed = evidence(sport, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch", recordId = "record-1")
            assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(unreviewed))
            assertEquals(CompetitionTrust.TRUSTED, WearableProvenancePolicy.classify(reviewed))
        }
    }

    @Test fun missing_record_identity_cannot_receive_health_wearable_trust() {
        for (sport in listOf(SportKind.WALKING, SportKind.RUNNING, SportKind.CYCLING)) {
            val missingId = evidence(sport, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch")
            assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(missingId))
        }
        val missingSwimmingId = evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch")
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(missingSwimmingId))
    }

    @Test fun anomalies_fail_closed() {
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, rejected = true)))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, start = 10L, end = 10L)))
    }

    @Test fun overlapping_phone_and_health_records_deduplicate() {
        val phone = evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, start = 1_000_000L, end = 1_600_000L)
        val health = evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch", recordId = "record-1", start = 1_060_000L, end = 1_660_000L)
        assertTrue(WearableProvenancePolicy.isDuplicate(phone, health))
        assertFalse(WearableProvenancePolicy.isDuplicate(phone, health.copy(sport = SportKind.CYCLING)))
    }

    @Test fun nearby_same_origin_sessions_are_not_silently_dropped() {
        val firstPhone = evidence(SportKind.WALKING, EvidenceOrigin.PHONE_MEASURED, start = 1_000_000L, end = 1_600_000L)
        val secondPhone = firstPhone.copy(startEpochMillis = 1_060_000L, endEpochMillis = 1_660_000L)
        val firstWatch = evidence(SportKind.CYCLING, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch", recordId = "record-1", start = 2_000_000L, end = 2_600_000L)
        val secondWatch = firstWatch.copy(startEpochMillis = 2_060_000L, endEpochMillis = 2_660_000L)
        assertFalse(WearableProvenancePolicy.isDuplicate(firstPhone, secondPhone))
        assertFalse(WearableProvenancePolicy.isDuplicate(firstWatch, secondWatch))
    }

    @Test fun swimming_never_time_deduplicates_without_stable_identity() {
        val phone = evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.PHONE_MEASURED, gps = true)
        val watch = evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch")
        assertFalse(WearableProvenancePolicy.isDuplicate(phone, watch))
    }

    @Test fun stable_record_identity_deduplicates_within_same_source() {
        val a = evidence(SportKind.WALKING, EvidenceOrigin.HEALTH_WEARABLE, source = "com.sec.android.app.shealth", device = "watch", recordId = "record-1")
        val b = a.copy(startEpochMillis = 9_000_000L, endEpochMillis = 9_600_000L)
        assertTrue(WearableProvenancePolicy.isDuplicate(a, b))
    }

    @Test fun record_id_without_nonblank_source_package_is_not_deduplicated() {
        val missingSource = evidence(SportKind.WALKING, EvidenceOrigin.HEALTH_WEARABLE, recordId = "record-1")
        val sameMissingSource = missingSource.copy(startEpochMillis = 9_000_000L, endEpochMillis = 9_600_000L)
        val blankSource = missingSource.copy(sourcePackage = " ")
        val sameBlankSource = blankSource.copy(startEpochMillis = 9_000_000L, endEpochMillis = 9_600_000L)
        assertFalse(WearableProvenancePolicy.isDuplicate(missingSource, sameMissingSource))
        assertFalse(WearableProvenancePolicy.isDuplicate(blankSource, sameBlankSource))
    }

    @Test fun same_record_id_from_different_source_packages_is_not_deduplicated() {
        val a = evidence(SportKind.WALKING, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.one", device = "watch", recordId = "record-1")
        val b = a.copy(sourcePackage = "watch.two")
        assertFalse(WearableProvenancePolicy.isDuplicate(a, b))
    }
}
