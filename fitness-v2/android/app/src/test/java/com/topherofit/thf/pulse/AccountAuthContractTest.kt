package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class AccountAuthContractTest {
    @Test
    fun accountOriginAndPkceRequestAreFailClosed() {
        assertEquals(
            "https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/",
            AccountAuthContract.persistentHttpsBase("https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai"),
        )
        assertNull(AccountAuthContract.persistentHttpsBase("http://example.com"))
        assertNull(AccountAuthContract.persistentHttpsBase("https://localhost"))
        assertNull(AccountAuthContract.persistentHttpsBase("https://preview.trycloudflare.com"))
        assertNull(AccountAuthContract.persistentHttpsBase("https://user:pass@example.com"))

        val request = AccountAuthContract.newRequest("https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/")
        assertEquals(43, request.verifier.length)
        assertEquals(43, request.challenge.length)
        assertTrue(request.startUrl.startsWith("https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/?nativeAuth=android-v2"))
        assertTrue(request.startUrl.contains("code_challenge_method=S256"))
        assertTrue(request.startUrl.contains("redirect_uri=topherofit%3A%2F%2Fauth%2Fv2%2Fcomplete"))
    }

    @Test
    fun callbackAcceptsOnlyExactAppRouteAndOpaqueTicket() {
        val ticket = "A".repeat(43)
        assertEquals(ticket, AccountAuthContract.callbackTicket("topherofit://auth/v2/complete?ticket=$ticket"))
        assertEquals(ticket, AccountAuthContract.callbackTicket("https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/android/auth/v2/complete?ticket=$ticket"))
        assertNull(AccountAuthContract.callbackTicket("topherofit://evil/v2/complete?ticket=$ticket"))
        assertNull(AccountAuthContract.callbackTicket("https://evil.example/android/auth/v2/complete?ticket=$ticket"))
        assertNull(AccountAuthContract.callbackTicket("topherofit://auth/v2/complete?ticket=short"))
        assertNull(AccountAuthContract.callbackTicket("https://auth/v2/complete?ticket=$ticket"))
    }

    @Test
    fun acceptsOnlyShortLivedOpaqueOrJwtAccessTokens() {
        assertEquals("thf_v2_${"B".repeat(43)}", AccountAuthContract.validAccessToken("thf_v2_${"B".repeat(43)}"))
        assertNotNull(AccountAuthContract.validAccessToken("${"a".repeat(16)}.${"b".repeat(16)}.${"c".repeat(16)}"))
        assertFalse(AccountAuthContract.validVerifier("short"))
        runCatching { AccountAuthContract.validAccessToken("not-a-token") }.onSuccess { throw AssertionError("invalid token accepted") }
    }
}
