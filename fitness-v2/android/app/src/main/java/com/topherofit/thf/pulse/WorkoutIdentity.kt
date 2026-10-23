package com.topherofit.thf.pulse

import java.nio.charset.StandardCharsets
import java.security.MessageDigest

object WorkoutIdentity {
    private const val PREFIX = "thf-workout-"
    private const val HEALTH_PREFIX = "thf-health-"

    fun stableClientRecordId(
        suppliedId: String?,
        startedAtMillis: Long,
        exerciseId: String,
    ): String {
        val clean = suppliedId.orEmpty().trim()
        if (clean.matches(Regex("[A-Za-z0-9._:-]{8,120}"))) return clean

        val payload = "$startedAtMillis:${exerciseId.trim().lowercase()}"
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(payload.toByteArray(StandardCharsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
        return PREFIX + digest.take(40)
    }

    fun stableHealthRecordKey(
        dataOrigin: String,
        recordType: String,
        recordId: String,
    ): String {
        val payload = listOf(
            dataOrigin.trim().lowercase(),
            recordType.trim(),
            recordId.trim(),
        ).joinToString(":")
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(payload.toByteArray(StandardCharsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
        return HEALTH_PREFIX + digest.take(40)
    }
}
