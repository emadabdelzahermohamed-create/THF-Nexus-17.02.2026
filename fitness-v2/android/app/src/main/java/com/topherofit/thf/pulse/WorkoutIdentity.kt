package com.topherofit.thf.pulse

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.Locale

object WorkoutIdentity {
    private const val PREFIX = "thf-workout-"
    private const val HEALTH_PREFIX = "thf-health-"
    private const val HEX_DIGITS = "0123456789abcdef"

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
        // Package names are case-insensitive ASCII identifiers. Locale.ROOT keeps their
        // pseudonymous identity stable on devices whose default locale has special casing
        // rules (for example, Turkish dotted/dotless I).
        val payload = listOf(
            dataOrigin.trim().lowercase(Locale.ROOT),
            recordType.trim(),
            recordId.trim(),
        ).joinToString(":")
        val digest = MessageDigest.getInstance("SHA-256")
            .digest(payload.toByteArray(StandardCharsets.UTF_8))
        val hex = buildString(digest.size * 2) {
            digest.forEach { byte ->
                val value = byte.toInt() and 0xff
                append(HEX_DIGITS[value ushr 4])
                append(HEX_DIGITS[value and 0x0f])
            }
        }
        return HEALTH_PREFIX + hex.take(40)
    }
}
