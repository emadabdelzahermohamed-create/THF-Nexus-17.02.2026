package com.topherofit.thf.pulse

import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.security.SecureRandom

object WorkoutIdentity {
    private const val PREFIX = "thf-workout-"
    private val secureRandom = SecureRandom()

    /** Creates a replay-resistant local workout identity for a newly-started sensor session. */
    fun newSessionId(nowMillis: Long = System.currentTimeMillis()): String {
        val nonce = ByteArray(16).also(secureRandom::nextBytes)
            .joinToString("") { "%02x".format(it) }
        return "$PREFIX$nowMillis-$nonce"
    }

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
}
