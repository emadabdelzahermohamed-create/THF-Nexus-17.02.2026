package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device
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
        deviceType: Int? = Device.TYPE_WATCH,
        trustedRecordingMethod: Boolean = true,
    ) = ActivityIntegrityInput(
        provenance = ActivityProvenance(
            source = source,
            providerPackageName = provider,
            providerRecordId = recordId,
            selfAuthoredByThf = selfAuthored,
            duplicate = duplicate,
            monotonicTimestamps = monotonicTimestamps,
            providerDeviceType = deviceType,
            trustedRecordingMethod = trustedRecordingMethod,
        ),
        durationMs = durationMs,
        speedMps = speedMps,
        cadenceSpm = cadenceSpm,
    )

    @Test fun externalHealthProviderRecordWithCompleteMetadataIsVerified() {
        assertEquals(IntegrityClass.VERIFIED, ActivityIntegrityClassifier.classify(input()))
    }

    @Test fun googleFitProviderIsAcceptedOnlyWithCompleteMetadata() {
        assertEquals(
            IntegrityClass.VERIFIED,
            ActivityIntegrityClassifier.classify(input(provider = "com.google.android.apps.fitness", deviceType = Device.TYPE_PHONE)),
        )
    }

    @Test fun unknownExternalHealthProviderIsSupportedNotVerified() {
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(input(provider = "com.example.unreviewed.health")),
        )
    }

    @Test fun missingOrUnknownDeviceClassCannotVerifyHealthConnectEvidence() {
        assertEquals(IntegrityClass.SUPPORTED, ActivityIntegrityClassifier.classify(input(deviceType = null)))
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(input(deviceType = Device.TYPE_UNKNOWN)),
        )
    }

    @Test fun untrustedRecordingMethodCannotVerifyHealthConnectEvidence() {
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(input(trustedRecordingMethod = false)),
        )
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

    @Test fun thfProviderPackageCannotVerifyItselfEvenIfFlagIsWrong() {
        assertEquals(
            IntegrityClass.REJECTED,
            ActivityIntegrityClassifier.classify(input(provider = "com.topherofit.thf.pulse")),
        )
    }

    @Test fun malformedProviderPackageCannotBecomeVerified() {
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(input(provider = "not-a-package")),
        )
    }

    @Test fun blankRecordIdCannotBecomeVerified() {
        assertEquals(
            IntegrityClass.SUPPORTED,
            ActivityIntegrityClassifier.classify(input(recordId = "   ")),
        )
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
