package com.topherofit.thf.pulse

enum class IntegrityClass { VERIFIED, SUPPORTED, MANUAL, REJECTED }

enum class ActivitySourceKind { HEALTH_CONNECT, DEVICE_SENSOR, MANUAL }

data class ActivityProvenance(
    val source: ActivitySourceKind,
    val providerPackageName: String? = null,
    val providerRecordId: String? = null,
    val selfAuthoredByThf: Boolean = false,
    val duplicate: Boolean = false,
    val monotonicTimestamps: Boolean = true,
)

data class ActivityIntegrityInput(
    val provenance: ActivityProvenance,
    val durationMs: Long,
    val speedMps: Double? = null,
    val cadenceSpm: Double? = null,
)

object ActivityIntegrityClassifier {
    private const val MAX_SPEED_MPS = 45.0
    private const val MAX_CADENCE_SPM = 240.0
    private const val THF_PACKAGE_NAME = "com.topherofit.thf.pulse"

    fun classify(input: ActivityIntegrityInput): IntegrityClass {
        val provenance = input.provenance
        if (input.durationMs <= 0L) return IntegrityClass.REJECTED
        if (provenance.duplicate || provenance.selfAuthoredByThf || !provenance.monotonicTimestamps) {
            return IntegrityClass.REJECTED
        }
        if (!metricPlausible(input.speedMps, MAX_SPEED_MPS)) return IntegrityClass.REJECTED
        if (!metricPlausible(input.cadenceSpm, MAX_CADENCE_SPM)) return IntegrityClass.REJECTED

        return when (provenance.source) {
            ActivitySourceKind.MANUAL -> IntegrityClass.MANUAL
            ActivitySourceKind.DEVICE_SENSOR -> IntegrityClass.SUPPORTED
            ActivitySourceKind.HEALTH_CONNECT -> classifyHealthConnect(provenance)
        }
    }

    private fun classifyHealthConnect(provenance: ActivityProvenance): IntegrityClass {
        val provider = provenance.providerPackageName?.trim().orEmpty()
        val recordId = provenance.providerRecordId?.trim().orEmpty()
        if (provider.equals(THF_PACKAGE_NAME, ignoreCase = true)) return IntegrityClass.REJECTED
        if (!validPackageName(provider) || recordId.isEmpty()) return IntegrityClass.SUPPORTED
        return IntegrityClass.VERIFIED
    }

    private fun validPackageName(value: String): Boolean {
        if (value.isEmpty() || value.length > 255 || !value.contains('.')) return false
        return value.split('.').all { segment ->
            segment.isNotEmpty() &&
                (segment.first().isLetter() || segment.first() == '_') &&
                segment.all { it.isLetterOrDigit() || it == '_' }
        }
    }

    private fun metricPlausible(value: Double?, maximum: Double): Boolean {
        if (value == null) return true
        return value.isFinite() && value >= 0.0 && value <= maximum
    }
}
