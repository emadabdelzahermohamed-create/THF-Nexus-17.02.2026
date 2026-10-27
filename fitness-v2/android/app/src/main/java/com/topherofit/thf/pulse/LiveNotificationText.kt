package com.topherofit.thf.pulse

import java.util.Locale

data class LiveNotificationContent(val compact: String, val expanded: String)

/** Presentation of measured session values; never substitutes daily totals or invented metrics. */
object LiveNotificationText {
    fun activity(s: ActivitySnapshot, stepsAvailable: Boolean, gpsStatus: String): LiveNotificationContent {
        val distance = String.format(Locale.US, "%.2f km", s.distanceMetres / 1000.0)
        val calories = String.format(Locale.US, "%.0f kcal تقديرية", s.estimatedCaloriesKcal)
        val steps = if (stepsAvailable) "${s.stepDelta} خطوة في الجلسة" else "الخطوات غير متاحة"
        val pace = s.paceMinutesPerKm?.takeIf { it.isFinite() && it > 0 }?.let {
            val seconds = (it.coerceAtMost(99.0) * 60).toInt()
            String.format(Locale.US, "%d:%02d /km", seconds / 60, seconds % 60)
        } ?: "— /km"
        val speed = String.format(Locale.US, "%.1f km/h", s.averageSpeedKph)
        val waitingForMovement = s.phase == ActivitySessionPhase.ARMED
        val phaseLabel = if (waitingForMovement) "بانتظار حركة مقاسة" else "النشاط مستمر"
        val compactMetrics = if (s.mode == ActivityMode.WALK) "$steps · $distance" else "$distance · $calories"
        val compact = if (waitingForMovement) "$phaseLabel · $compactMetrics" else compactMetrics
        val detail = if (s.mode == ActivityMode.CYCLE) "$distance · $speed" else "$steps\n$distance · $pace"
        val expandedMetrics = "$detail\n$calories\n$gpsStatus"
        val expanded = if (waitingForMovement) "$phaseLabel\n$expandedMetrics" else expandedMetrics
        return LiveNotificationContent(compact, expanded)
    }

    fun workout(steps: Int?, profile: String, stepSensorAvailable: Boolean?): LiveNotificationContent {
        val measurement = when (stepSensorAvailable) {
            true -> "${steps ?: 0} خطوة في الجلسة"
            false -> "الخطوات غير متاحة"
            null -> "خطوات غير مقاسة لهذا التمرين"
        }
        return LiveNotificationContent("$profile · $measurement", "$profile\n$measurement\nقياس الحركة مستمر · افتح التطبيق لتفاصيل التمرين")
    }
}
