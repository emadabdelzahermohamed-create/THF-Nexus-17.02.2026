package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Test

class ActivityIntegrityTest {
    private fun input(
        source: ActivitySourceKind = ActivitySourceKind.HEALTH_CONNECT,
        provider: String? = "com.samsung.android.wear.shealth",
        recordId: String? = "record-12345678",
        selfAuthored: Boolean = false,
        duplicate: Boolean = false,
        monotonicTimestamps: Boolean = true,
        durationMs: Long = 30 * 60_000L,
        speedMps: Double? = 3.2,
        cadenceSpm: Double? = 165.0,
    ) = ActivityIntegrityInput(
        provenance = ActivityProvenance(
            source = source,
            providerPackageName = provider,
            providerRecordId = recordId,
            selfAuthoredByThf = selfAuthored,
            duplicate = duplicate,
            monotonicTimestamps = monotonicTimestamps,
        ),
        durationMs = durationMs,
        speedMps = speedMps,
        cadenceSpm = cadenceSpm,
    )

    @Test fun externalHealthProviderRecordIsVerified() {
        assertEquals(IntegrityClass.VERIFIED, ActivityIntegrityClassifier.classify(input()))
    }

    @Test fun validDeviceSensorEvidenceIsSupported() {
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(
                input(source = ActivitySourceKind.DEVICE_SENSOR, provider = null, recordId = null),
            ),
        )
    }

    @Test fun manualEvidenceStaysManual() {
        assertEquals(
            IntegrityClass.MANUAL,
            ActivityIntegrityClassifier.classify(
                input(source = ActivitySourceKind.MANUAL, provider = null, recordId = null),
            ),
        )
    }

    @Test fun duplicateProviderRecordIsRejected() {
        assertEquals(IntegrityClass.REJECTED, ActivityIntegrityClassifier.classify(input(duplicate = true)))
    }

    @Test fun selfAuthoredHealthRecordIsRejected() {
        assertEquals(IntegrityClass.REJECTED, ActivityIntegrityClassifier.classify(input(selfAuthored = true)))
    }

    @Test fun nonFiniteMetricsAreRejected() {
        assertEquals(
            IntegrityClass.REJECTED,
            ActivityIntegrityClassifier.classify(input(speedMps = Double.NaN)),
        )
    }

    @Test fun implausibleSpeedIsRejected() {
        assertEquals(
            IntegrityClass.REJECTED,
            ActivityIntegrityClassifier.classify(input(speedMps = 80.0)),
        )
    }

    @Test fun implausibleCadenceIsRejected() {
        assertEquals(
            IntegrityClass.REJECTED,
            ActivityIntegrityClassifier.classify(input(cadenceSpm = 400.0)),
        )
    }

    @Test fun nonMonotonicSensorTimeIsRejected() {
        assertEquals(
            IntegrityClass.REJECTED,
            ActivityIntegrityClassifier.classify(
                input(
                    source = ActivitySourceKind.DEVICE_SENSOR,
                    provider = null,
                    recordId = null,
                    monotonicTimestamps = false,
                ),
            ),
        )
    }
}
