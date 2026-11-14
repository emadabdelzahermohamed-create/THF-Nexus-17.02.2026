package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivityLocationFallbackPolicyTest {
    @Test
    fun waitsForInitialFusedFixBeforeRegisteringFrameworkFallback() {
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(10_000L, null, 17_999L))
        assertTrue(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(10_000L, null, 18_000L))
    }

    @Test
    fun reactivatesFallbackWhenLastAcceptedFixBecomesStale() {
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(10_000L, 20_000L, 31_999L))
        assertTrue(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(10_000L, 20_000L, 32_000L))
    }

    @Test
    fun rejectsInvalidMonotonicClockInputs() {
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(0L, null, 50_000L))
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(20_000L, null, 19_999L))
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyProviders(10_000L, 30_000L, 29_999L))
    }
    @Test
    fun fusedRegistrationIsKeptOnlyForTheCurrentUnpausedSessionGeneration() {
        assertTrue(ActivityLocationFallbackPolicy.shouldKeepFusedLocationRegistration(true, false, true))
        assertFalse(ActivityLocationFallbackPolicy.shouldKeepFusedLocationRegistration(false, false, true))
        assertFalse(ActivityLocationFallbackPolicy.shouldKeepFusedLocationRegistration(true, true, true))
        assertFalse(ActivityLocationFallbackPolicy.shouldKeepFusedLocationRegistration(true, false, false))
    }

    @Test
    fun legacyFallbackCannotRegisterAfterPauseStopOrDuplicateRegistration() {
        assertTrue(ActivityLocationFallbackPolicy.shouldRegisterLegacyLocationProvider(true, false, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyLocationProvider(false, false, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyLocationProvider(true, true, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldRegisterLegacyLocationProvider(true, false, true))
        assertTrue(
            ActivityLocationFallbackPolicy.shouldRegisterLegacyLocationProvider(
                sessionModeMatches = true,
                paused = false,
                alreadyRegistered = true,
                allowProviderSwitch = true,
            ),
        )
    }

    @Test
    fun silentGpsProviderFallsBackToNetworkAfterBoundedWait() {
        val start = 20_000L
        fun shouldSwitch(now: Long, accepted: Long? = null) =
            ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
                currentProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                coarsePermissionGranted = true,
                networkProviderEnabled = true,
                gpsRegistrationSucceeded = true,
                providerAttemptStartedElapsedMs = start,
                lastAcceptedElapsedMs = accepted,
                nowElapsedMs = now,
            )

        assertFalse(shouldSwitch(31_999L))
        assertTrue(shouldSwitch(32_000L))
        assertFalse(shouldSwitch(32_000L, accepted = 31_000L))
        assertTrue(shouldSwitch(32_000L, accepted = 19_000L))
        assertFalse(shouldSwitch(32_000L, accepted = 32_001L))
    }

    @Test
    fun failedGpsRegistrationFallsBackImmediatelyWhenNetworkPermissionAndProviderExist() {
        assertTrue(
            ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
                currentProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                coarsePermissionGranted = true,
                networkProviderEnabled = true,
                gpsRegistrationSucceeded = false,
                providerAttemptStartedElapsedMs = 20_000L,
                lastAcceptedElapsedMs = null,
                nowElapsedMs = 20_001L,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
                currentProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                coarsePermissionGranted = false,
                networkProviderEnabled = true,
                gpsRegistrationSucceeded = false,
                providerAttemptStartedElapsedMs = 20_000L,
                lastAcceptedElapsedMs = null,
                nowElapsedMs = 20_001L,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
                currentProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
                coarsePermissionGranted = true,
                networkProviderEnabled = true,
                gpsRegistrationSucceeded = false,
                providerAttemptStartedElapsedMs = 20_000L,
                lastAcceptedElapsedMs = null,
                nowElapsedMs = 20_001L,
            ),
        )
    }

    @Test
    fun approximateOnlyPermissionUsesNetworkEvenWhenGpsIsEnabled() {
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = false,
                coarsePermissionGranted = true,
                gpsProviderEnabled = true,
                networkProviderEnabled = true,
            ),
        )
    }

    @Test
    fun finePermissionPrefersGpsAndFallsBackToNetworkWhenGpsIsUnavailable() {
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.GPS,
            ActivityLocationFallbackPolicy.selectLegacyProvider(true, true, true, true),
        )
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ActivityLocationFallbackPolicy.selectLegacyProvider(true, true, false, true),
        )
    }

    @Test
    fun currentProviderIsRetainedOnlyWhileItRemainsEligible() {
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = true,
                coarsePermissionGranted = true,
                gpsProviderEnabled = true,
                networkProviderEnabled = true,
                preferredProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ),
        )
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.GPS,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = true,
                coarsePermissionGranted = true,
                gpsProviderEnabled = true,
                networkProviderEnabled = false,
                preferredProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ),
        )
        assertEquals(
            ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = true,
                coarsePermissionGranted = true,
                gpsProviderEnabled = false,
                networkProviderEnabled = true,
                preferredProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
            ),
        )
    }

    @Test
    fun frameworkProviderRegistrationRetryUsesBoundedBackoff() {
        assertEquals(0L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(0))
        assertEquals(4_000L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(1))
        assertEquals(8_000L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(2))
        assertEquals(16_000L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(3))
        assertEquals(30_000L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(4))
        assertEquals(30_000L, ActivityLocationFallbackPolicy.legacyProviderRetryDelayMs(9))
    }

    @Test
    fun fallbackProviderSelectionFailsClosedWithoutPermissionOrEnabledProvider() {
        assertEquals(
            null,
            ActivityLocationFallbackPolicy.selectLegacyProvider(false, false, true, true),
        )
        assertEquals(
            null,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = true,
                coarsePermissionGranted = false,
                gpsProviderEnabled = false,
                networkProviderEnabled = true,
            ),
        )
        assertEquals(
            null,
            ActivityLocationFallbackPolicy.selectLegacyProvider(false, true, true, false),
        )
        assertEquals(
            null,
            ActivityLocationFallbackPolicy.selectLegacyProvider(true, false, false, false),
        )
    }

}
