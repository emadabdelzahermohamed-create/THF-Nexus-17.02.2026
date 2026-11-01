package com.topherofit.thf.pulse

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WebViewNetworkPolicyTest {
    @Test
    fun allowsOnlySecureOpenStreetMapRasterTiles() {
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/12/1205/1539.png"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/0/0/0.png"))
    }

    @Test
    fun rejectsLookalikeHostsAndNonTilePaths() {
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org.evil.example/12/1205/1539.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://evil.example/tile.openstreetmap.org/12/1205/1539.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/export"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/12/1205/1539.jpg"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://user@tile.openstreetmap.org/12/1205/1539.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org:444/12/1205/1539.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("http://tile.openstreetmap.org/12/1205/1539.png"))
    }

    @Test
    fun blocksExternalWebViewRequestsExceptApprovedMapTiles() {
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("https://tile.openstreetmap.org/12/1205/1539.png"))
        assertTrue(WebViewNetworkPolicy.shouldBlockExternalResource("https://example.com/script.js"))
        assertTrue(WebViewNetworkPolicy.shouldBlockExternalResource("http://tile.openstreetmap.org/12/1205/1539.png"))
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("file:///android_asset/pulse/index.html"))
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("data:image/png;base64,AAAA"))
    }
}
