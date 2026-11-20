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
    @Test
    fun notificationStatusNamesTheAcceptedProviderInsteadOfCallingEverySourceGps() {
        assertEquals(
            "مصدر الموقع: الموقع المدمج · الدقة ±9 م",
            GpsFixPresentationPolicy.statusText("ready", "fused", 8.7f, 12f),
        )
        assertEquals(
            "مصدر الموقع: الشبكة · الدقة ±8 م",
            GpsFixPresentationPolicy.statusText("ready", "network", 8f, 20f),
        )
        assertEquals(
            "مصدر الموقع: GPS · الدقة ±<1 م",
            GpsFixPresentationPolicy.statusText("ready", "gps", 0.5f, null),
        )
    }

    @Test
    fun notificationNeverShowsAcceptedAccuracyForPausedStaleOrFilteredFixes() {
        assertEquals(
            "النشاط متوقف مؤقتًا · لا يتم احتساب مسافة",
            GpsFixPresentationPolicy.statusText("paused", "gps", 4f, 4f),
        )
        assertEquals(
            "إشارة الموقع متوقفة · بانتظار تحديث",
            GpsFixPresentationPolicy.statusText("stale", "fused", 4f, 4f),
        )
        assertEquals(
            "تم رصد الموقع ±5 م · النقطة لم تُقبل لاحتساب المسافة",
            GpsFixPresentationPolicy.statusText("filtered", "network", 4f, 4.1f),
        )
    }

    @Test
    fun notificationDoesNotInventAnAccuracyWhenTheAcceptedFixHasNone() {
        assertEquals(
            "مصدر الموقع: الموقع · الدقة غير متاحة",
            GpsFixPresentationPolicy.statusText("ready", null, null, null),
        )
    }

}
