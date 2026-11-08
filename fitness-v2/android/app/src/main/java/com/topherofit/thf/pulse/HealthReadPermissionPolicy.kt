package com.topherofit.thf.pulse

/** Core Health Connect record families that can be read independently under partial consent. */
enum class HealthReadMetric {
    STEPS,
    EXERCISE_SESSIONS,
    DISTANCE,
    ACTIVE_CALORIES,
}

/**
 * A permission-derived read plan. It never infers access from provider availability or from
 * another metric's grant. Missing permission is distinct from an allowed read that returns zero.
 */
data class HealthReadPermissionPlan internal constructor(
    val readableMetrics: Set<HealthReadMetric>,
    val missingPermissions: Set<String>,
) {
    val hasAnyReadPermission: Boolean
        get() = readableMetrics.isNotEmpty()

    val hasAllReadPermissions: Boolean
        get() = missingPermissions.isEmpty()

    fun canRead(metric: HealthReadMetric): Boolean = metric in readableMetrics

    /** Returns null for a missing permission while preserving a real zero from an allowed read. */
    fun <T> valueIfReadable(metric: HealthReadMetric, value: T): T? =
        if (canRead(metric)) value else null
}

object HealthReadPermissionPolicy {
    fun plan(
        grantedPermissions: Set<String>,
        permissionByMetric: Map<HealthReadMetric, String>,
    ): HealthReadPermissionPlan {
        val readable = linkedSetOf<HealthReadMetric>()
        val missing = linkedSetOf<String>()
        permissionByMetric.forEach { (metric, permission) ->
            if (permission.isNotBlank() && permission in grantedPermissions) {
                readable += metric
            } else {
                missing += permission
            }
        }
        return HealthReadPermissionPlan(
            readableMetrics = readable.toSet(),
            missingPermissions = missing.toSet(),
        )
    }
}
