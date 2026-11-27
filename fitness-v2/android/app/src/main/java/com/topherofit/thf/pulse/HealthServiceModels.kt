package com.topherofit.thf.pulse

import java.time.Instant
import kotlinx.coroutines.CancellationException

enum class HealthService(
    val permission: String,
    val titleAr: String,
    val titleEn: String,
    val purposeAr: String,
    val purposeEn: String,
) {
    STEPS("android.permission.health.READ_STEPS", "خطوات اليوم", "Today's steps",
        "عرض خطوات اليوم من المصادر التي اخترتها في Health Connect.", "View today's steps from your Health Connect sources."),
    DISTANCE("android.permission.health.READ_DISTANCE", "مسافة اليوم", "Today's distance",
        "عرض المسافة المسجلة اليوم، وليست مسار GPS حيًا.", "View distance recorded today, not a live GPS route."),
    ACTIVE_CALORIES("android.permission.health.READ_ACTIVE_CALORIES_BURNED", "السعرات النشطة اليوم", "Today's active calories",
        "عرض تقدير طاقة النشاط المسجل دون تخمين قيم مفقودة.", "View recorded active-energy estimates without inventing missing values."),
    TOTAL_CALORIES("android.permission.health.READ_TOTAL_CALORIES_BURNED", "إجمالي السعرات اليوم", "Today's total calories",
        "عرض إجمالي الطاقة المسجل منفصلًا عن السعرات النشطة؛ لا نجمعهما.", "View recorded total energy separately from active calories; never add the two."),
    EXERCISE("android.permission.health.READ_EXERCISE", "سجلات التمارين / ٧ أيام", "Exercise records / 7 days",
        "عدّ السجلات حسب المصدر؛ قد يسجل تطبيقان التمرين نفسه. ليس عدّ جلسات فريدة.", "Count source records; two apps may record the same workout. This is not a unique-session count."),
    SLEEP("android.permission.health.READ_SLEEP", "النوم / ٧ أيام", "Sleep / 7 days",
        "عرض مدة النوم المسجلة لفهم انتظام الراحة، دون تشخيص أو درجة تعافٍ مفترضة.", "View recorded sleep duration for rest awareness, without diagnosis or an invented recovery score."),
    HEART_RATE("android.permission.health.READ_HEART_RATE", "متوسط النبض اليوم", "Today's average heart rate",
        "عرض متوسط قياسات النبض المسجلة من ساعة أو مصدر متوافق؛ الهاتف لا يقيسه هنا.", "View average heart-rate samples from a compatible source; the phone is not measuring it here."),
    RESTING_HEART_RATE("android.permission.health.READ_RESTING_HEART_RATE", "آخر نبض راحة مسجل", "Latest resting heart rate",
        "عرض آخر قياس مسجل وتاريخه دون تفسير طبي.", "View the latest recorded measurement and date without medical interpretation."),
    WEIGHT("android.permission.health.READ_WEIGHT", "آخر وزن مسجل", "Latest recorded weight",
        "عرض الوزن من مصدره؛ لا نستبدل وزن ملف التدريب تلقائيًا.", "View source weight without automatically replacing your training-profile weight."),
    HEIGHT("android.permission.health.READ_HEIGHT", "آخر طول مسجل", "Latest recorded height",
        "عرض الطول المسجل دون اختلاق أو تعديل قياس الجسم.", "View recorded height without inventing or changing body measurements."),
    BODY_FAT("android.permission.health.READ_BODY_FAT", "آخر نسبة دهون مسجلة", "Latest recorded body fat",
        "عرض قراءة نسبة الدهون من ميزان أو مصدر متوافق مع تاريخها.", "View a body-fat reading from a compatible scale or source with its date."),
    BASAL_METABOLIC_RATE("android.permission.health.READ_BASAL_METABOLIC_RATE", "آخر معدل أيض أساسي", "Latest basal metabolic rate",
        "عرض تقدير المصدر للطاقة الأساسية؛ ليس وصفة سعرات أو قياسًا يجريه التطبيق.", "View the source's basal-energy estimate, not a calorie prescription or a measurement by this app."),
    OXYGEN_SATURATION("android.permission.health.READ_OXYGEN_SATURATION", "آخر تشبع أكسجين مسجل", "Latest recorded oxygen saturation",
        "عرض آخر قراءة من مصدر متوافق؛ لا يوفر الهاتف هنا قياس أكسجين أو تنبيهًا طبيًا.", "View the latest compatible-source reading, not a phone oxygen measurement or medical alert."),
    VO2_MAX("android.permission.health.READ_VO2_MAX", "آخر VO₂ max مسجل", "Latest recorded VO2 max",
        "عرض تقدير اللياقة القلبية من مصدره؛ لا نحسب اختبارًا مخبريًا وهميًا.", "View the source's cardiorespiratory-fitness estimate, not an invented laboratory test."),
    SPEED("android.permission.health.READ_SPEED", "أقصى سرعة مسجلة اليوم", "Today's recorded maximum speed",
        "عرض أقصى سرعة مسجلة اليوم؛ ليست سرعة GPS الحالية.", "View today's recorded maximum speed, not current GPS speed."),
    NUTRITION("android.permission.health.READ_NUTRITION", "آخر سجل تغذية", "Latest nutrition record",
        "عرض طاقة ومغذيات آخر سجل فقط، لا جمع وجبات مكررة بين التطبيقات أو وصف حمية.", "View energy and macros from the latest record only; no cross-app meal double counting or diet prescription."),
    BLOOD_PRESSURE("android.permission.health.READ_BLOOD_PRESSURE", "آخر ضغط دم مسجل", "Latest recorded blood pressure",
        "عرض قراءة مسجلة وتاريخها فقط؛ لا يقيس الهاتف الضغط ولا يصنفه طبيًا.", "View a recorded reading and date only; the phone does not measure or medically classify blood pressure."),
    BLOOD_GLUCOSE("android.permission.health.READ_BLOOD_GLUCOSE", "آخر جلوكوز مسجل", "Latest recorded blood glucose",
        "عرض قراءة الجلوكوز المسجلة دون تشخيص أو توصية دواء أو تعديل جرعة.", "View recorded glucose without diagnosis, medication advice or dose adjustment."),
}

enum class HealthMetricStatus { NOT_LOADED, PERMISSION_REQUIRED, NO_DATA, READY, ERROR }
data class HealthMetricValue(val value: Double, val unit: String, val labelAr: String = "", val labelEn: String = "")
data class HealthMetricResult(
    val service: HealthService,
    val status: HealthMetricStatus,
    val values: List<HealthMetricValue> = emptyList(),
    val origins: Set<String> = emptySet(),
    val observedAt: Instant? = null,
    val windowStart: Instant? = null,
    val windowEnd: Instant? = null,
    val recordingMethod: Int? = null,
)

interface HealthServiceSource {
    suspend fun grantedPermissions(): Set<String>
    suspend fun read(service: HealthService): HealthMetricResult
}

object HealthServiceAccessPolicy {
    fun visibleResult(service: HealthService, granted: Set<String>, result: HealthMetricResult?): HealthMetricResult {
        if (service.permission !in granted) return HealthMetricResult(service, HealthMetricStatus.PERMISSION_REQUIRED)
        if (result == null) return HealthMetricResult(service, HealthMetricStatus.NOT_LOADED)
        if (result.service != service) return HealthMetricResult(service, HealthMetricStatus.ERROR)
        if (result.status != HealthMetricStatus.READY) return HealthMetricResult(service, result.status)
        return measurement(service, result.values).copy(
            origins = result.origins, observedAt = result.observedAt,
            windowStart = result.windowStart, windowEnd = result.windowEnd,
            recordingMethod = result.recordingMethod,
        )
    }

    fun measurement(service: HealthService, values: List<HealthMetricValue>): HealthMetricResult {
        val valid = values.filter { it.value.isFinite() && it.value >= 0 }
        return HealthMetricResult(service, if (valid.isEmpty()) HealthMetricStatus.NO_DATA else HealthMetricStatus.READY, valid)
    }
}

class HealthServicesReader(private val source: HealthServiceSource) {
    suspend fun read(service: HealthService): HealthMetricResult = try {
        if (service.permission !in source.grantedPermissions()) {
            HealthMetricResult(service, HealthMetricStatus.PERMISSION_REQUIRED)
        } else {
            val result = source.read(service)
            HealthServiceAccessPolicy.visibleResult(service, source.grantedPermissions(), result)
        }
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (_: SecurityException) {
        HealthMetricResult(service, HealthMetricStatus.PERMISSION_REQUIRED)
    } catch (_: Exception) {
        // Provider exceptions may contain private data. Never surface or log them.
        HealthMetricResult(service, HealthMetricStatus.ERROR)
    }
}
