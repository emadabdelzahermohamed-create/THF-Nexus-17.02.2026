package com.topherofit.thf.pulse

data class ActivityNotificationTiming(
    val whenWallMs: Long,
    val showWhen: Boolean,
    val usesChronometer: Boolean,
)

/** Keeps the system notification clock aligned with the actual measured session phase. */
object ActivityNotificationTimingPolicy {
    fun forActivity(snapshot: ActivitySnapshot, nowWallMs: Long): ActivityNotificationTiming {
        val activatedAt = snapshot.startedAtWallMs
        if (snapshot.phase != ActivitySessionPhase.ACTIVE || activatedAt <= 0L) {
            return ActivityNotificationTiming(
                whenWallMs = nowWallMs.coerceAtLeast(0L),
                showWhen = false,
                usesChronometer = false,
            )
        }
        return ActivityNotificationTiming(
            whenWallMs = activatedAt,
            showWhen = true,
            usesChronometer = true,
        )
    }

    fun forWorkout(sessionStartedAtWallMs: Long): ActivityNotificationTiming {
        val start = sessionStartedAtWallMs.takeIf { it > 0L } ?: 0L
        return ActivityNotificationTiming(
            whenWallMs = start,
            showWhen = start > 0L,
            usesChronometer = start > 0L,
        )
    }
}
