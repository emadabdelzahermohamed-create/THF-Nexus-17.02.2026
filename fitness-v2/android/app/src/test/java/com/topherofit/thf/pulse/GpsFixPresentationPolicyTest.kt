package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Test

class GpsFixPresentationPolicyTest {
    private val now = 100_000L

    private fun state(
        permission: Boolean = true,
        provider: Boolean = true,
        observed: Long? = 99_000L,
        accepted: Long? = 99_000L,
    ) = GpsFixPresentationPolicy.state(permission, provider, observed, accepted, now)

    @Test fun missingPermissionTakesPriority() {
        assertEquals("permission", state(permission = false, provider = false, observed = null, accepted = null))
    }

    @Test fun disabledProviderIsReported() {
        assertEquals("off", state(provider = false))
    }

    @Test fun missingObservationRemainsAcquiring() {
        assertEquals("acquiring", state(observed = null, accepted = null))
    }

    @Test fun staleAndFutureObservationsAreNotPresentedAsReady() {
        assertEquals("stale", state(observed = now - 30_001L, accepted = now - 30_001L))
        assertEquals("stale", state(observed = now + 1L, accepted = null))
    }

    @Test fun freshObservationWithoutAcceptedFixIsFilteredNotWeak() {
        assertEquals("filtered", state(observed = now - 500L, accepted = null))
    }

    @Test fun newerRejectedObservationIsFilteredWhenAcceptedFixIsOlder() {
        assertEquals("filtered", state(observed = now - 500L, accepted = now - 1_000L))
    }

    @Test fun sameObservedAndAcceptedFixIsReady() {
        assertEquals("ready", state(observed = now - 500L, accepted = now - 500L))
    }

    @Test fun acceptedFixNewerThanLastValidObservationRemainsReady() {
        assertEquals("ready", state(observed = now - 1_000L, accepted = now - 500L))
    }
}
