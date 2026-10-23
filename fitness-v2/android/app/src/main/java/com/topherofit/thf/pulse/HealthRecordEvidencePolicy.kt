package com.topherofit.thf.pulse

data class HealthRecordEvidenceAssessment(
    val integrityClass: IntegrityClass,
    val verifiedForRewards: Boolean,
    val reason: String,
)

object HealthRecordEvidencePolicy {
    fun assess(
        appPackageName: String,
        dataOrigin: String,
        recordType: String,
        recordId: String,
        trustedRecordingMethod: Boolean,
    ): HealthRecordEvidenceAssessment {
        val app = appPackageName.trim()
        val origin = dataOrigin.trim()
        val type = recordType.trim()
        val id = recordId.trim()

        if (origin == app && app.isNotEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.REJECTED,
                verifiedForRewards = false,
                reason = "SELF_AUTHORED",
            )
        }
        if (!trustedRecordingMethod) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "MANUAL_OR_UNKNOWN_METHOD",
            )
        }
        if (origin.isEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "UNKNOWN_ORIGIN",
            )
        }
        if (type.isEmpty() || id.isEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.SUPPORTED,
                verifiedForRewards = false,
                reason = "INCOMPLETE_PROVIDER_IDENTITY",
            )
        }
        return HealthRecordEvidenceAssessment(
            integrityClass = IntegrityClass.VERIFIED,
            verifiedForRewards = true,
            reason = "EXTERNAL_SENSOR_RECORDED",
        )
    }
}
