package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Test

class HealthUxStateTest {
    private fun input(
        availability: String = "AVAILABLE",
        readPermissionsGranted: Boolean = true,
        syncing: Boolean = false,
        hasSuccessfulSync: Boolean = true,
        recordsRead: Int = 1,
        verifiedRecords: Int = 1,
        lastErrorCode: String? = null,
    ) = HealthUxInput(
        availability,
        readPermissionsGranted,
        syncing,
        hasSuccessfulSync,
        recordsRead,
        verifiedRecords,
        lastErrorCode,
    )

    @Test fun permissionFailureIsNotRenderedAsNoData() {
        assertEquals(
            HealthUxState.PERMISSION_REQUIRED,
            HealthUxStateClassifier.classify(input(readPermissionsGranted = false, recordsRead = 0, verifiedRecords = 0)),
        )
    }

    @Test fun providerUpdateIsExplicit() {
        assertEquals(
            HealthUxState.PROVIDER_UPDATE_REQUIRED,
            HealthUxStateClassifier.classify(input(availability = "PROVIDER_UPDATE_REQUIRED")),
        )
    }

    @Test fun successfulEmptyReadIsNoRecords() {
        assertEquals(
            HealthUxState.SYNCED_NO_RECORDS,
            HealthUxStateClassifier.classify(input(recordsRead = 0, verifiedRecords = 0)),
        )
    }

    @Test fun recordsWithoutTrustedProvenanceAreUnverifiedOnly() {
        assertEquals(
            HealthUxState.SYNCED_UNVERIFIED_ONLY,
            HealthUxStateClassifier.classify(input(recordsRead = 3, verifiedRecords = 0)),
        )
    }

    @Test fun verifiedRecordsProduceVerifiedState() {
        assertEquals(
            HealthUxState.SYNCED_VERIFIED,
            HealthUxStateClassifier.classify(input(recordsRead = 4, verifiedRecords = 2)),
        )
    }

    @Test fun rateLimitOverridesLastSuccessfulSnapshot() {
        assertEquals(
            HealthUxState.RATE_LIMITED,
            HealthUxStateClassifier.classify(input(lastErrorCode = "RATE_LIMITED")),
        )
    }
}
