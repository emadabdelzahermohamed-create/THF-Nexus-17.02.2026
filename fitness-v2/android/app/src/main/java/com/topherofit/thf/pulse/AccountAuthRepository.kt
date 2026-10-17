package com.topherofit.thf.pulse

import java.io.ByteArrayOutputStream
import java.net.URL
import java.nio.charset.StandardCharsets
import javax.net.ssl.HttpsURLConnection
import org.json.JSONObject

/** Exchanges a single-use browser ticket for a short-lived, memory-only Android session. */
class AccountAuthRepository(baseUrl: String) {
    companion object {
        private const val MAX_RESPONSE_BYTES = 32 * 1024
    }

    private val endpoint: URL? = runCatching {
        val clean = AccountAuthContract.persistentHttpsBase(baseUrl)?.trimEnd('/')
            ?: return@runCatching null
        URL("$clean/api/v2/auth/android/sessions")
    }.getOrNull()

    val configured: Boolean get() = endpoint != null

    fun consume(ticket: String, verifier: String): String {
        require(AccountAuthContract.validTicket(ticket)) { "invalid one-time ticket" }
        require(AccountAuthContract.validVerifier(verifier)) { "invalid PKCE verifier" }
        val target = endpoint ?: throw BackendSyncException("Production backend endpoint is not configured")
        val payload = JSONObject().put("ticket", ticket).put("codeVerifier", verifier).toString().toByteArray()
        val connection = (target.openConnection() as HttpsURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15_000
            readTimeout = 20_000
            doOutput = true
            instanceFollowRedirects = false
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Cache-Control", "no-store")
            setFixedLengthStreamingMode(payload.size)
        }
        return try {
            connection.outputStream.use { it.write(payload) }
            val status = connection.responseCode
            val body = readBounded(if (status in 200..299) connection.inputStream else connection.errorStream)
            if (status !in 200..299) throw BackendSyncException("Account hand-off failed ($status)", status)
            val document = JSONObject(body)
            require(document.optString("tokenType") == "Bearer") { "unexpected account token type" }
            AccountAuthContract.validAccessToken(document.getString("accessToken"))
        } finally {
            connection.disconnect()
        }
    }

    private fun readBounded(stream: java.io.InputStream?): String {
        if (stream == null) return "{}"
        val output = ByteArrayOutputStream()
        val buffer = ByteArray(4096)
        stream.use { input ->
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                if (output.size() + count > MAX_RESPONSE_BYTES) throw BackendSyncException("Account response is too large")
                output.write(buffer, 0, count)
            }
        }
        return output.toString(StandardCharsets.UTF_8.name())
    }
}
