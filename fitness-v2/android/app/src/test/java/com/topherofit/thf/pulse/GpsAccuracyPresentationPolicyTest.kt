package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class GpsAccuracyPresentationPolicyTest {
    @Test
    fun accuracyFormattingNeverTurnsSubMetreOrMissingValuesIntoZeroMetres() {
        assertEquals("±<1 م", GpsAccuracyPresentationPolicy.formatAccuracyMetres(0.5f))
        assertEquals("±9 م", GpsAccuracyPresentationPolicy.formatAccuracyMetres(8.7f))
        assertEquals("±8 م", GpsAccuracyPresentationPolicy.formatAccuracyMetres(8f))
        assertEquals("±9 م", GpsAccuracyPresentationPolicy.formatAccuracyMetres(8.01f))
        assertEquals("غير متاحة", GpsAccuracyPresentationPolicy.formatAccuracyMetres(null))
        assertEquals("غير متاحة", GpsAccuracyPresentationPolicy.formatAccuracyMetres(0f))
        assertEquals("غير متاحة", GpsAccuracyPresentationPolicy.formatAccuracyMetres(Float.NaN))
        assertEquals("غير متاحة", GpsAccuracyPresentationPolicy.formatAccuracyMetres(Float.POSITIVE_INFINITY))
    }

    @Test
    fun onlyReadyStateShowsAcceptedAccuracy() {
        assertEquals(8f, GpsAccuracyPresentationPolicy.visibleAccuracy("ready", 8f))
        listOf("permission", "off", "acquiring", "stale", "filtered", "paused").forEach { state ->
            assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy(state, 8f))
        }
    }

    @Test
    fun missingOrInvalidAccuracyNeverBecomesZeroMetres() {
        assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy("ready", null))
        assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy("ready", 0f))
        assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy("ready", -1f))
        assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy("ready", Float.NaN))
        assertNull(GpsAccuracyPresentationPolicy.visibleAccuracy("ready", Float.POSITIVE_INFINITY))
    }
}
