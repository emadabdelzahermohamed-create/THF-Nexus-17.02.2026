package com.topherofit.thf.pulse

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ActivitySessionStartPolicyTest {
    @Test
    fun startsOnlyWhenNoActivitySessionAlreadyExists() {
        assertTrue(ActivitySessionStartPolicy.shouldStart(currentMode = null, requestedMode = ActivityMode.WALK))
        assertFalse(ActivitySessionStartPolicy.shouldStart(currentMode = ActivityMode.WALK, requestedMode = ActivityMode.WALK))
        assertFalse(ActivitySessionStartPolicy.shouldStart(currentMode = ActivityMode.WALK, requestedMode = ActivityMode.RUN))
    }
}
