package com.topherofit.thf.pulse

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FoundingHeroBillingStateTest {
    @Test
    fun waitsForBothCatalogAndOwnershipBeforeLeavingLoading() {
        val afterCatalog = FoundingHeroBillingState()
            .catalogResult(available = true, price = "EGP 99.00")

        assertTrue(afterCatalog.loading)
        assertTrue(afterCatalog.available)
        assertEquals("EGP 99.00", afterCatalog.price)

        val ready = afterCatalog.purchaseResult(FoundingHeroOwnership.NOT_OWNED)
        assertFalse(ready.loading)
        assertFalse(ready.owned)
        assertFalse(ready.pending)
    }

    @Test
    fun purchaseResultMayArriveBeforeCatalogWithoutFalseUnavailableState() {
        val afterPurchase = FoundingHeroBillingState()
            .purchaseResult(FoundingHeroOwnership.OWNED)

        assertTrue(afterPurchase.loading)
        assertTrue(afterPurchase.owned)

        val ready = afterPurchase.catalogResult(available = true, price = "$4.99")
        assertFalse(ready.loading)
        assertTrue(ready.owned)
        assertEquals("$4.99", ready.price)
    }

    @Test
    fun pendingPurchaseNeverGrantsTheCosmeticEntitlement() {
        val state = FoundingHeroBillingState()
            .catalogResult(available = true, price = "€4.99")
            .purchaseResult(FoundingHeroOwnership.PENDING)

        assertFalse(state.loading)
        assertFalse(state.owned)
        assertTrue(state.pending)
    }

    @Test
    fun unrelatedOrUnverifiedPurchaseDoesNotGrantEntitlement() {
        assertEquals(
            FoundingHeroOwnership.NOT_OWNED,
            FoundingHeroPurchasePolicy.ownership(
                productIds = listOf("other_product"),
                purchased = true,
                pending = false,
                signatureVerified = true,
            ),
        )
        assertEquals(
            FoundingHeroOwnership.NOT_OWNED,
            FoundingHeroPurchasePolicy.ownership(
                productIds = listOf(FoundingHeroPurchasePolicy.PRODUCT_ID),
                purchased = true,
                pending = false,
                signatureVerified = false,
            ),
        )
    }

    @Test
    fun verifiedPurchasedProductGrantsOnlyTheCosmeticEntitlement() {
        assertEquals(
            FoundingHeroOwnership.OWNED,
            FoundingHeroPurchasePolicy.ownership(
                productIds = listOf(FoundingHeroPurchasePolicy.PRODUCT_ID),
                purchased = true,
                pending = false,
                signatureVerified = true,
            ),
        )
        assertEquals("thf_founding_hero_lifetime", FoundingHeroPurchasePolicy.PRODUCT_ID)
    }
}
