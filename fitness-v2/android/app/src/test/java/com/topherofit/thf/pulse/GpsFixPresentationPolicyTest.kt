package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Test

class GpsFixPresentationPolicyTest {
    @Test
    fun missingPermissionTakesPrecedenceOverEnabledLocationServices() {
        assertEquals(
            "permission",
            GpsFixPresentationPolicy.state(false, true, null, null, 1_000L),
        )
    }

    @Test
    fun disabledSystemLocationSwitchReportsOffBeforeUsingOldFixes() {
        assertEquals(
            "off",
            GpsFixPresentationPolicy.state(true, false, 900L, 900L, 1_000L),
        )
    }

    @Test
    fun freshObservationWithoutAcceptedMeasurementReportsFiltered() {
        assertEquals(
            "filtered",
            GpsFixPresentationPolicy.state(true, true, 950L, 900L, 1_000L),
        )
    }

    @Test
    fun oldObservationReportsStaleEvenWhenAnOlderFixWasAccepted() {
        assertEquals(
            "stale",
            GpsFixPresentationPolicy.state(true, true, 8_999L, 8_999L, 40_000L),
        )
    }

    @Test
    fun freshAcceptedObservationReportsReady() {
        assertEquals(
            "ready",
            GpsFixPresentationPolicy.state(true, true, 950L, 950L, 1_000L),
        )
    }

    @Test
    fun notificationSourceLabelDistinguishesGpsNetworkAndFused() {
        assertEquals("GPS", GpsFixPresentationPolicy.sourceLabel("gps"))
        assertEquals("الشبكة", GpsFixPresentationPolicy.sourceLabel("network"))
        assertEquals("الموقع المدمج", GpsFixPresentationPolicy.sourceLabel("fused"))
        assertEquals("الموقع", GpsFixPresentationPolicy.sourceLabel(null))
    }
}
