package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device
import java.util.Locale

/**
 * Narrow package allowlist for Health Connect writers reviewed by the current product lane.
 * This identifies the writing app only; it is not cryptographic device or wearable attestation.
 * Unknown writers remain importable as supported evidence, but cannot independently qualify rewards.
 */
internal object HealthSourceTrustPolicy {
    private val approvedProviderPackages = setOf(
        "com.google.android.apps.fitness",
        "com.sec.android.app.shealth",
        "com.samsung.android.wear.shealth",
    )

    private val compatibleActivityDeviceTypes = setOf(
        Device.TYPE_PHONE,
        Device.TYPE_WATCH,
        Device.TYPE_FITNESS_BAND,
        Device.TYPE_CHEST_STRAP,
        Device.TYPE_RING,
    )

    fun isCompatibleActivityDeviceType(deviceType: Int?): Boolean =
        deviceType != null && deviceType in compatibleActivityDeviceTypes

    /**
     * Health Connect device metadata must identify a water-compatible wearable for swimming.
     * Phone, ring, chest-strap, scale, and unknown device classes do not qualify.
     *
     * This is a metadata gate, not hardware attestation.
     */
    fun swimmingDeviceLabel(deviceType: Int?): String? = when (deviceType) {
        Device.TYPE_WATCH -> "watch"
        Device.TYPE_FITNESS_BAND -> "fitness_band"
        else -> null
    }

    fun isApprovedHealthConnectProvider(rawPackageName: String?): Boolean {
        val packageName = rawPackageName?.trim()?.lowercase(Locale.ROOT) ?: return false
        if (!isValidPackageName(packageName)) return false
        return packageName in approvedProviderPackages
    }

    private fun isValidPackageName(value: String): Boolean {
        if (value.isEmpty() || value.length > 255 || !value.contains('.')) return false
        return value.split('.').all { segment ->
            segment.isNotEmpty() &&
                (segment.first().isLetter() || segment.first() == '_') &&
                segment.all { it.isLetterOrDigit() || it == '_' }
        }
    }
}
