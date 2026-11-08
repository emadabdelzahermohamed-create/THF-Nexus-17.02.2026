package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class HealthReadPermissionPolicyTest {
    private val permissions = linkedMapOf(
        HealthReadMetric.STEPS to "health.read_steps",
        HealthReadMetric.EXERCISE_SESSIONS to "health.read_exercise",
        HealthReadMetric.DISTANCE to "health.read_distance",
        HealthReadMetric.ACTIVE_CALORIES to "health.read_active_calories",
    )

    @Test
    fun allGrantedMakesEveryCoreMetricReadable() {
        val plan = HealthReadPermissionPolicy.plan(permissions.values.toSet(), permissions)

        assertTrue(plan.hasAnyReadPermission)
        assertTrue(plan.hasAllReadPermissions)
        assertEquals(permissions.keys, plan.readableMetrics)
        assertTrue(plan.missingPermissions.isEmpty())
    }

    @Test
    fun partialGrantReadsOnlyExplicitlyGrantedMetrics() {
        val granted = setOf("health.read_steps", "health.read_exercise")
        val plan = HealthReadPermissionPolicy.plan(granted, permissions)

        assertTrue(plan.hasAnyReadPermission)
        assertFalse(plan.hasAllReadPermissions)
        assertTrue(plan.canRead(HealthReadMetric.STEPS))
        assertTrue(plan.canRead(HealthReadMetric.EXERCISE_SESSIONS))
        assertFalse(plan.canRead(HealthReadMetric.DISTANCE))
        assertFalse(plan.canRead(HealthReadMetric.ACTIVE_CALORIES))
        assertEquals(
            setOf("health.read_distance", "health.read_active_calories"),
            plan.missingPermissions,
        )
    }

    @Test
    fun oneGrantedMetricIsEnoughForAReadOnlyConnection() {
        val plan = HealthReadPermissionPolicy.plan(setOf("health.read_distance"), permissions)

        assertTrue(plan.hasAnyReadPermission)
        assertFalse(plan.hasAllReadPermissions)
        assertEquals(setOf(HealthReadMetric.DISTANCE), plan.readableMetrics)
    }

    @Test
    fun noCoreReadPermissionDoesNotOpenTheReadPath() {
        val plan = HealthReadPermissionPolicy.plan(setOf("health.write_exercise"), permissions)

        assertFalse(plan.hasAnyReadPermission)
        assertFalse(plan.canRead(HealthReadMetric.STEPS))
        assertEquals(permissions.values.toSet(), plan.missingPermissions)
    }

    @Test
    fun unrelatedGrantedPermissionDoesNotImplyHealthMetricAccess() {
        val plan = HealthReadPermissionPolicy.plan(
            setOf("health.read_sleep", "health.read_heart_rate"),
            permissions,
        )

        assertFalse(plan.hasAnyReadPermission)
        assertTrue(plan.readableMetrics.isEmpty())
        assertEquals(permissions.values.toSet(), plan.missingPermissions)
    }

    @Test
    fun allowedZeroIsPreservedButMissingPermissionReturnsNull() {
        val partial = HealthReadPermissionPolicy.plan(setOf("health.read_steps"), permissions)

        assertEquals(0L, partial.valueIfReadable(HealthReadMetric.STEPS, 0L))
        assertNull(partial.valueIfReadable(HealthReadMetric.DISTANCE, 0.0))
    }
}
