package com.topherofit.thf.pulse

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WebViewNetworkPolicyTest {
    @Test
    fun allowsOnlySecureApprovedRasterTiles() {
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/12/2403/1689.png"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://a.tile.opentopomap.org/12/2403/1689.png"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://b.tile.opentopomap.org/12/2403/1689.png"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://c.tile.opentopomap.org/12/2403/1689.png"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/12/1689/2403.jpg"))
        assertTrue(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tiles.maps.eox.at/wmts/1.0.0/streets_3857/default/g/12/1689/2403.png"))
    }

    @Test
    fun rejectsLookalikeHostsAndUnapprovedTilePaths() {
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org.evil.example/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://a.tile.opentopomap.org.evil.example/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tiles.maps.eox.at.evil.example/wmts/1.0.0/s2cloudless_3857/default/g/12/1689/2403.jpg"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tiles.maps.eox.at/wmts/1.0.0/other-layer/default/g/12/1689/2403.jpg"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/12/1689/2403.jpg?token=x"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/export"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org/12/2403/1689.jpg"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("http://tile.openstreetmap.org/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://user@tile.openstreetmap.org/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.isAllowedMapTileUrl("https://tile.openstreetmap.org:444/12/2403/1689.png"))
    }

    @Test
    fun blocksExternalWebViewRequestsExceptApprovedMapTiles() {
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("https://tile.openstreetmap.org/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/12/1689/2403.jpg"))
        assertTrue(WebViewNetworkPolicy.shouldBlockExternalResource("https://example.com/script.js"))
        assertTrue(WebViewNetworkPolicy.shouldBlockExternalResource("http://tile.openstreetmap.org/12/2403/1689.png"))
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("file:///android_asset/pulse/index.html"))
        assertFalse(WebViewNetworkPolicy.shouldBlockExternalResource("data:image/png;base64,AAAA"))
        assertTrue(WebViewNetworkPolicy.shouldBlockExternalResource("not a valid url"))
    }
}
