package com.topherofit.thf.pulse

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
    }

}
