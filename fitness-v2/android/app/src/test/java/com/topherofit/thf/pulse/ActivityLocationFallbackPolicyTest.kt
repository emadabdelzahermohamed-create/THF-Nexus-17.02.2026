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
    fun revokingTheLastLocationPermissionSuspendsAnyActiveLocationSource() {
        assertTrue(
            ActivityLocationFallbackPolicy.shouldSuspendLocationSources(
                hasLocationPermission = false,
                fusedCallbackRegistered = true,
                legacyProviderRegistered = false,
                hasLiveLocationState = false,
            ),
        )
        assertTrue(
            ActivityLocationFallbackPolicy.shouldSuspendLocationSources(
                hasLocationPermission = false,
                fusedCallbackRegistered = false,
                legacyProviderRegistered = true,
                hasLiveLocationState = false,
            ),
        )
        assertTrue(
            ActivityLocationFallbackPolicy.shouldSuspendLocationSources(
                hasLocationPermission = false,
                fusedCallbackRegistered = false,
                legacyProviderRegistered = false,
                hasLiveLocationState = true,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldSuspendLocationSources(
                hasLocationPermission = false,
                fusedCallbackRegistered = false,
                legacyProviderRegistered = false,
                hasLiveLocationState = false,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldSuspendLocationSources(
                hasLocationPermission = true,
                fusedCallbackRegistered = true,
                legacyProviderRegistered = true,
                hasLiveLocationState = true,
            ),
        )
    }

    @Test
    fun permissionRegrantRestartsOnlyTheSameUnpausedLiveSession() {
        assertTrue(ActivityLocationFallbackPolicy.shouldResumeLocationSources(true, true, true, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldResumeLocationSources(false, true, true, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldResumeLocationSources(true, false, true, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldResumeLocationSources(true, true, false, false))
        assertFalse(ActivityLocationFallbackPolicy.shouldResumeLocationSources(true, true, true, true))
    }

    @Test
    fun silentGpsProviderFallsBackToNetworkAfterBoundedWait() {
        val start = 20_000L
        fun shouldSwitch(now: Long, accepted: Long? = null) =
            ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
                currentProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                finePermissionGranted = true,
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
                finePermissionGranted = true,
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
                finePermissionGranted = true,
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
                finePermissionGranted = true,
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
    fun precisePermissionDowngradeSwitchesAnActiveGpsSubscriptionImmediately() {
        val start = 20_000L
        val recentAccepted = 25_000L
        val now = 26_000L

        fun shouldSwitch(
            fine: Boolean,
            coarse: Boolean = true,
            network: Boolean = true,
            provider: ActivityLocationFallbackPolicy.LegacyProvider? = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
        ) = ActivityLocationFallbackPolicy.shouldFallbackFromGpsToNetwork(
            currentProvider = provider,
            finePermissionGranted = fine,
            coarsePermissionGranted = coarse,
            networkProviderEnabled = network,
            gpsRegistrationSucceeded = true,
            providerAttemptStartedElapsedMs = start,
            lastAcceptedElapsedMs = recentAccepted,
            nowElapsedMs = now,
        )

        // A fresh GPS fix would normally keep the provider active for another 12 seconds.
        // A precision downgrade is an authorization change and must switch on the next poll.
        assertTrue(shouldSwitch(fine = false))
        assertFalse(shouldSwitch(fine = true))
        assertFalse(shouldSwitch(fine = false, coarse = false))
        assertFalse(shouldSwitch(fine = false, network = false))
        assertFalse(shouldSwitch(fine = false, provider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK))
    }

    @Test
    fun legacyProviderCallbacksMustMatchTheCurrentProviderAndRegistrationGeneration() {
        assertTrue(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                callbackProvider = "gps",
                registrationGenerationMatches = true,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.GPS,
                callbackProvider = "network",
                registrationGenerationMatches = true,
            ),
        )
        assertTrue(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
                callbackProvider = "NETWORK",
                registrationGenerationMatches = true,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
                callbackProvider = "gps",
                registrationGenerationMatches = true,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
                callbackProvider = "network",
                registrationGenerationMatches = false,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = null,
                callbackProvider = "network",
                registrationGenerationMatches = true,
            ),
        )
        assertFalse(
            ActivityLocationFallbackPolicy.shouldAcceptLegacyProviderCallback(
                expectedProvider = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK,
                callbackProvider = "fused",
                registrationGenerationMatches = true,
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
    fun legacyProviderAuthorizationTracksTheCurrentPermissionPrecision() {
        val gps = ActivityLocationFallbackPolicy.LegacyProvider.GPS
        val network = ActivityLocationFallbackPolicy.LegacyProvider.NETWORK

        assertTrue(ActivityLocationFallbackPolicy.isLegacyProviderAuthorized(gps, true, false))
        assertFalse(ActivityLocationFallbackPolicy.isLegacyProviderAuthorized(gps, false, true))
        assertTrue(ActivityLocationFallbackPolicy.isLegacyProviderAuthorized(network, false, true))
        assertFalse(ActivityLocationFallbackPolicy.isLegacyProviderAuthorized(network, true, false))
        assertFalse(ActivityLocationFallbackPolicy.isLegacyProviderAuthorized(null, true, true))

        assertEquals(
            null,
            ActivityLocationFallbackPolicy.selectLegacyProvider(
                finePermissionGranted = false,
                coarsePermissionGranted = true,
                gpsProviderEnabled = true,
                networkProviderEnabled = false,
                preferredProvider = gps,
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


    @Test
    fun fusedRecoveryRequiresTheCurrentUnpausedSessionAndAnActiveFallback() {
        fun shouldPromote(
            sessionMatches: Boolean = true,
            paused: Boolean = false,
            legacyActive: Boolean = true,
        ) = ActivityLocationFallbackPolicy.shouldPromoteFusedLocation(
            sessionModeMatches = sessionMatches,
            paused = paused,
            legacyProviderActive = legacyActive,
            fusedFixAccuracyMetres = 4.0,
            fusedFixElapsedMs = 20_001L,
            currentAcceptedAccuracyMetres = 6.0,
            currentAcceptedElapsedMs = 20_000L,
            currentAcceptedFixFresh = true,
        )

        assertTrue(shouldPromote())
        assertFalse(shouldPromote(sessionMatches = false))
        assertFalse(shouldPromote(paused = true))
        assertFalse(shouldPromote(legacyActive = false))
    }

    @Test
    fun fusedRecoveryRequiresANewerFixBeforeApplyingAccuracyArbitration() {
        fun shouldPromote(
            fusedAccuracy: Double,
            legacyAccuracy: Double,
            fusedElapsed: Long,
            legacyElapsed: Long,
        ) = ActivityLocationFallbackPolicy.shouldPromoteFusedLocation(
            sessionModeMatches = true,
            paused = false,
            legacyProviderActive = true,
            fusedFixAccuracyMetres = fusedAccuracy,
            fusedFixElapsedMs = fusedElapsed,
            currentAcceptedAccuracyMetres = legacyAccuracy,
            currentAcceptedElapsedMs = legacyElapsed,
            currentAcceptedFixFresh = true,
        )

        assertTrue(shouldPromote(4.0, 5.0, fusedElapsed = 20_001L, legacyElapsed = 20_000L))
        assertTrue(shouldPromote(5.0, 5.0, fusedElapsed = 20_001L, legacyElapsed = 20_000L))
        assertFalse(shouldPromote(6.0, 5.0, fusedElapsed = 20_001L, legacyElapsed = 20_000L))
        // A Fused fix can be fresh relative to now yet still be older than the fresh framework fix.
        assertFalse(shouldPromote(1.0, 5.0, fusedElapsed = 19_999L, legacyElapsed = 20_000L))
        // Equal timestamps cannot establish ordering and must not replace the current route source.
        assertFalse(shouldPromote(1.0, 5.0, fusedElapsed = 20_000L, legacyElapsed = 20_000L))
    }

    @Test
    fun fusedRecoveryCanReplaceMissingOrStaleLegacyFixButRejectsInvalidCandidateAccuracy() {
        fun shouldPromote(
            fusedAccuracy: Double?,
            legacyAccuracy: Double?,
            legacyFresh: Boolean,
        ) = ActivityLocationFallbackPolicy.shouldPromoteFusedLocation(
            sessionModeMatches = true,
            paused = false,
            legacyProviderActive = true,
            fusedFixAccuracyMetres = fusedAccuracy,
            fusedFixElapsedMs = 20_001L,
            currentAcceptedAccuracyMetres = legacyAccuracy,
            currentAcceptedElapsedMs = 20_000L,
            currentAcceptedFixFresh = legacyFresh,
        )

        assertTrue(shouldPromote(10.0, 4.0, legacyFresh = false))
        assertTrue(shouldPromote(10.0, null, legacyFresh = true))
        assertFalse(shouldPromote(null, 4.0, legacyFresh = false))
        assertFalse(shouldPromote(0.0, 4.0, legacyFresh = false))
        assertFalse(shouldPromote(Double.NaN, 4.0, legacyFresh = false))
        assertFalse(shouldPromote(Double.POSITIVE_INFINITY, 4.0, legacyFresh = false))
    }



    @Test
    fun activityForegroundServiceUsesHealthWhenSystemLocationIsDisabledAndRejectsNoEligibleType() {
        assertEquals(
            ActivityForegroundServiceKind.LOCATION,
            ActivityForegroundServiceTypePolicy.forActivity(
                locationPermissionGranted = true,
                locationServicesEnabled = true,
                activityRecognitionPermissionGranted = true,
            ),
        )
        assertEquals(
            ActivityForegroundServiceKind.HEALTH,
            ActivityForegroundServiceTypePolicy.forActivity(
                locationPermissionGranted = true,
                locationServicesEnabled = false,
                activityRecognitionPermissionGranted = true,
            ),
        )
        assertEquals(
            ActivityForegroundServiceKind.HEALTH,
            ActivityForegroundServiceTypePolicy.forActivity(
                locationPermissionGranted = false,
                locationServicesEnabled = true,
                activityRecognitionPermissionGranted = true,
            ),
        )
        assertEquals(
            null,
            ActivityForegroundServiceTypePolicy.forActivity(
                locationPermissionGranted = true,
                locationServicesEnabled = false,
                activityRecognitionPermissionGranted = false,
            ),
        )
        assertEquals(
            null,
            ActivityForegroundServiceTypePolicy.forActivity(
                locationPermissionGranted = false,
                locationServicesEnabled = false,
                activityRecognitionPermissionGranted = false,
            ),
        )
    }

}
