package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class GpsAccuracyPresentationPolicyTest {
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
