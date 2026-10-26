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

    @Test fun swimming_requires_wearable_health_provenance() {
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.PHONE_MEASURED, gps = true)))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "phone")))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "spoofed-device")))
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "watch")))
        assertEquals(CompetitionTrust.VERIFIED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_OPEN_WATER, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "smartwatch", gps = false)))
    }

    @Test fun imported_and_manual_swimming_never_become_verified() {
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.HEALTH_IMPORTED, source = "health.app")))
        assertEquals(CompetitionTrust.MANUAL, WearableProvenancePolicy.classify(evidence(SportKind.SWIMMING_POOL, EvidenceOrigin.MANUAL)))
    }

    @Test fun wearable_origin_without_wearable_device_is_not_trusted() {
        assertEquals(CompetitionTrust.IMPORTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "health.app", device = "phone")))
        assertEquals(CompetitionTrust.TRUSTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "fitness_tracker")))
    }

    @Test fun anomalies_fail_closed() {
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, rejected = true)))
        assertEquals(CompetitionTrust.REJECTED, WearableProvenancePolicy.classify(evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, start = 10L, end = 10L)))
    }

    @Test fun overlapping_phone_and_health_records_deduplicate() {
        val phone = evidence(SportKind.RUNNING, EvidenceOrigin.PHONE_MEASURED, gps = true, start = 1_000_000L, end = 1_600_000L)
        val health = evidence(SportKind.RUNNING, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "watch", start = 1_060_000L, end = 1_660_000L)
        assertTrue(WearableProvenancePolicy.isDuplicate(phone, health))
        assertFalse(WearableProvenancePolicy.isDuplicate(phone, health.copy(sport = SportKind.CYCLING)))
    }

    @Test fun stable_record_identity_deduplicates() {
        val a = evidence(SportKind.WALKING, EvidenceOrigin.HEALTH_WEARABLE, source = "watch.app", device = "watch", recordId = "record-1")
        val b = a.copy(startEpochMillis = 9_000_000L, endEpochMillis = 9_600_000L)
        assertTrue(WearableProvenancePolicy.isDuplicate(a, b))
    }
}