package com.topherofit.thf.pulse

import android.app.Activity
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClient.BillingResponseCode
import com.android.billingclient.api.BillingClient.ProductType
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import java.security.KeyFactory
import java.security.Signature
import java.security.spec.X509EncodedKeySpec
import java.util.Base64
import java.util.concurrent.atomic.AtomicBoolean
import org.json.JSONObject

internal enum class FoundingHeroOwnership { NOT_OWNED, PENDING, OWNED }

internal data class FoundingHeroBillingState(
    val configured: Boolean = true,
    val connected: Boolean = false,
    val productStateKnown: Boolean = false,
    val purchaseStateKnown: Boolean = false,
    val available: Boolean = false,
    val owned: Boolean = false,
    val pending: Boolean = false,
    val acknowledged: Boolean = false,
    val price: String = "",
    val errorCode: String = "",
) {
    val loading: Boolean get() = configured && (!productStateKnown || !purchaseStateKnown)

    fun catalogResult(available: Boolean, price: String = "", errorCode: String = "") = copy(
        productStateKnown = true,
        available = available,
        price = if (available) price else "",
        errorCode = errorCode.ifBlank { this.errorCode },
    )

    fun purchaseResult(
        ownership: FoundingHeroOwnership,
        acknowledged: Boolean = false,
        errorCode: String = "",
    ) = copy(
        purchaseStateKnown = true,
        owned = ownership == FoundingHeroOwnership.OWNED,
        pending = ownership == FoundingHeroOwnership.PENDING,
        acknowledged = ownership == FoundingHeroOwnership.OWNED && acknowledged,
        errorCode = errorCode.ifBlank { this.errorCode },
    )

    fun toJson(): JSONObject = JSONObject()
        .put("productId", FoundingHeroPurchasePolicy.PRODUCT_ID)
        .put("configured", configured)
        .put("connected", connected)
        .put("loading", loading)
        .put("available", available)
        .put("owned", owned)
        .put("pending", pending)
        .put("acknowledged", acknowledged)
        .put("price", price)
        .put("errorCode", errorCode)
}

internal object FoundingHeroPurchasePolicy {
    const val PRODUCT_ID = "thf_founding_hero_lifetime"

    fun ownership(
        productIds: List<String>,
        purchased: Boolean,
        pending: Boolean,
        signatureVerified: Boolean,
    ): FoundingHeroOwnership {
        if (PRODUCT_ID !in productIds) return FoundingHeroOwnership.NOT_OWNED
        if (pending) return FoundingHeroOwnership.PENDING
        return if (purchased && signatureVerified) FoundingHeroOwnership.OWNED else FoundingHeroOwnership.NOT_OWNED
    }
}

/**
 * Minimal client-side verification for the first low-risk cosmetic entitlement.
 * The configured Play RSA public key is not a secret. A future backend verifier
 * can replace this boundary without changing the web UI or product identifier.
 */
internal object PlayPurchaseVerifier {
    fun verify(publicKeyBase64: String, signedData: String, signatureBase64: String): Boolean = runCatching {
        if (publicKeyBase64.isBlank() || signedData.isBlank() || signatureBase64.isBlank()) return false
        val publicKey = KeyFactory.getInstance("RSA").generatePublic(
            X509EncodedKeySpec(Base64.getDecoder().decode(publicKeyBase64.filterNot(Char::isWhitespace))),
        )
        val verifier = Signature.getInstance("SHA1withRSA")
        verifier.initVerify(publicKey)
        verifier.update(signedData.toByteArray(Charsets.UTF_8))
        verifier.verify(Base64.getDecoder().decode(signatureBase64))
    }.getOrDefault(false)
}

internal class FoundingHeroBilling(
    private val activity: Activity,
    private val playLicenseKey: String,
    private val onState: (FoundingHeroBillingState) -> Unit,
) : PurchasesUpdatedListener {
    private val connecting = AtomicBoolean(false)

    @Volatile
    var state = FoundingHeroBillingState(configured = playLicenseKey.isNotBlank())
        private set

    private val client: BillingClient = BillingClient.newBuilder(activity)
        .setListener(this)
        .enablePendingPurchases(
            PendingPurchasesParams.newBuilder().enableOneTimeProducts().build(),
        )
        .enableAutoServiceReconnection()
        .build()

    fun start() {
        if (!state.configured) {
            publish(
                state.copy(
                    connected = false,
                    productStateKnown = true,
                    purchaseStateKnown = true,
                    errorCode = "PLAY_LICENSE_KEY_REQUIRED",
                ),
            )
            return
        }
        if (client.isReady) {
            refresh()
            return
        }
        if (!connecting.compareAndSet(false, true)) return
        publish(state.copy(errorCode = ""))
        client.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                connecting.set(false)
                if (result.responseCode == BillingResponseCode.OK) {
                    publish(state.copy(connected = true, errorCode = ""))
                    refresh()
                } else {
                    publish(unavailableState("BILLING_${result.responseCode}"))
                }
            }

            override fun onBillingServiceDisconnected() {
                connecting.set(false)
                publish(state.copy(connected = false, errorCode = "BILLING_DISCONNECTED"))
            }
        })
    }

    fun refresh() {
        if (!state.configured) {
            start()
            return
        }
        if (!client.isReady) {
            start()
            return
        }
        publish(
            state.copy(
                connected = true,
                productStateKnown = false,
                purchaseStateKnown = false,
                errorCode = "",
            ),
        )
        queryCatalog()
        queryPurchases()
    }

    fun launchPurchase() {
        if (!state.configured || state.owned || state.pending) {
            publish(state.copy(errorCode = if (state.configured) "ALREADY_OWNED_OR_PENDING" else "PLAY_LICENSE_KEY_REQUIRED"))
            return
        }
        if (!client.isReady) {
            start()
            publish(state.copy(errorCode = "BILLING_CONNECTING"))
            return
        }
        queryProductDetails { details, offerToken ->
            if (details == null || offerToken.isNullOrBlank()) {
                publish(state.catalogResult(available = false, errorCode = "PRODUCT_NOT_CONFIGURED"))
                return@queryProductDetails
            }
            val item = BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(details)
                .setOfferToken(offerToken)
                .build()
            val result = client.launchBillingFlow(
                activity,
                BillingFlowParams.newBuilder()
                    .setProductDetailsParamsList(listOf(item))
                    .setIsOfferPersonalized(false)
                    .build(),
            )
            if (result.responseCode != BillingResponseCode.OK) {
                publish(state.copy(errorCode = "PURCHASE_LAUNCH_${result.responseCode}"))
            }
        }
    }

    fun close() {
        if (client.isReady) client.endConnection()
    }

    override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
        when (result.responseCode) {
            BillingResponseCode.OK -> processPurchases(purchases.orEmpty())
            BillingResponseCode.USER_CANCELED -> publish(state.copy(errorCode = "PURCHASE_CANCELED"))
            BillingResponseCode.ITEM_ALREADY_OWNED -> queryPurchases()
            else -> publish(state.copy(errorCode = "PURCHASE_${result.responseCode}"))
        }
    }

    private fun queryCatalog() {
        queryProductDetails { details, offerToken ->
            val offer = details?.oneTimePurchaseOfferDetailsList?.firstOrNull { it.offerToken == offerToken }
            publish(
                state.catalogResult(
                    available = details != null && offer != null,
                    price = offer?.formattedPrice.orEmpty(),
                    errorCode = if (details == null || offer == null) "PRODUCT_NOT_CONFIGURED" else "",
                ),
            )
        }
    }

    private fun queryProductDetails(callback: (ProductDetails?, String?) -> Unit) {
        val item = QueryProductDetailsParams.Product.newBuilder()
            .setProductId(FoundingHeroPurchasePolicy.PRODUCT_ID)
            .setProductType(ProductType.INAPP)
            .build()
        client.queryProductDetailsAsync(
            QueryProductDetailsParams.newBuilder().setProductList(listOf(item)).build(),
        ) { result, response ->
            if (result.responseCode != BillingResponseCode.OK) {
                publish(state.catalogResult(available = false, errorCode = "CATALOG_${result.responseCode}"))
                callback(null, null)
                return@queryProductDetailsAsync
            }
            val details = response.productDetailsList.firstOrNull {
                it.productId == FoundingHeroPurchasePolicy.PRODUCT_ID
            }
            val offerToken = details?.oneTimePurchaseOfferDetailsList?.firstOrNull()?.offerToken
            callback(details, offerToken)
        }
    }

    private fun queryPurchases() {
        client.queryPurchasesAsync(
            QueryPurchasesParams.newBuilder().setProductType(ProductType.INAPP).build(),
        ) { result, purchases ->
            if (result.responseCode == BillingResponseCode.OK) {
                processPurchases(purchases)
            } else {
                publish(state.purchaseResult(FoundingHeroOwnership.NOT_OWNED, errorCode = "OWNERSHIP_${result.responseCode}"))
            }
        }
    }

    private fun processPurchases(purchases: List<Purchase>) {
        val purchase = purchases.firstOrNull { FoundingHeroPurchasePolicy.PRODUCT_ID in it.products }
        if (purchase == null) {
            publish(state.purchaseResult(FoundingHeroOwnership.NOT_OWNED))
            return
        }
        val isPending = purchase.purchaseState == Purchase.PurchaseState.PENDING
        val isPurchased = purchase.purchaseState == Purchase.PurchaseState.PURCHASED
        val signatureVerified = isPurchased && PlayPurchaseVerifier.verify(
            playLicenseKey,
            purchase.originalJson,
            purchase.signature,
        )
        val ownership = FoundingHeroPurchasePolicy.ownership(
            productIds = purchase.products,
            purchased = isPurchased,
            pending = isPending,
            signatureVerified = signatureVerified,
        )
        val verificationError = if (isPurchased && !signatureVerified) "PURCHASE_VERIFICATION_FAILED" else ""
        publish(state.purchaseResult(ownership, purchase.isAcknowledged, verificationError))
        if (ownership == FoundingHeroOwnership.OWNED && !purchase.isAcknowledged) acknowledge(purchase)
    }

    private fun acknowledge(purchase: Purchase) {
        client.acknowledgePurchase(
            AcknowledgePurchaseParams.newBuilder().setPurchaseToken(purchase.purchaseToken).build(),
        ) { result ->
            if (result.responseCode == BillingResponseCode.OK) {
                publish(state.copy(acknowledged = true, errorCode = ""))
            } else {
                publish(state.copy(acknowledged = false, errorCode = "ACKNOWLEDGE_${result.responseCode}"))
            }
        }
    }

    private fun unavailableState(errorCode: String) = state.copy(
        connected = false,
        productStateKnown = true,
        purchaseStateKnown = true,
        available = false,
        errorCode = errorCode,
    )

    private fun publish(next: FoundingHeroBillingState) {
        state = next
        onState(next)
    }
}
