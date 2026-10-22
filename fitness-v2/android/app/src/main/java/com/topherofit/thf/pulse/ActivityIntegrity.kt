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
            ActivitySourceKind.HEALTH_CONNECT -> {
                if (!provenance.providerPackageName.isNullOrBlank() && !provenance.providerRecordId.isNullOrBlank()) {
                    IntegrityClass.VERIFIED
                } else {
                    IntegrityClass.SUPPORTED
                }
            }
        }
    }

    private fun metricPlausible(value: Double?, maximum: Double): Boolean {
        if (value == null) return true
        return value.isFinite() && value >= 0.0 && value <= maximum
    }
}
