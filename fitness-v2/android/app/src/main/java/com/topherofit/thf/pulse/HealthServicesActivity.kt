package com.topherofit.thf.pulse

import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.core.net.toUri
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.records.metadata.Metadata
import androidx.lifecycle.lifecycleScope
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle
import java.util.Locale
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Optional, foreground-only local viewer. It never writes or uploads health data. */
class HealthServicesActivity : ComponentActivity() {
    private lateinit var column: LinearLayout
    private lateinit var status: TextView
    private val labels = mutableMapOf<HealthService, TextView>()
    private val buttons = mutableMapOf<HealthService, Button>()
    private val results = mutableMapOf<HealthService, HealthMetricResult>()
    private var grants: Set<String> = emptySet()
    private var work: Job? = null
    private var generation = 0
    private var busy: HealthService? = null
    private var available = false
    private var pending: HealthService? = null
    private val language by lazy {
        intent.getStringExtra("language")?.takeIf { it == "ar" || it == "en" }
            ?: if (Locale.getDefault().language == "ar") "ar" else "en"
    }
    private fun text(ar: String, en: String) = if (language == "ar") ar else en

    private val permissionLauncher = registerForActivityResult(PermissionController.createRequestPermissionResultContract()) {
        val selected = pending
        pending = null
        refreshPermissions(selected)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutDirection = if (language == "ar") View.LAYOUT_DIRECTION_RTL else View.LAYOUT_DIRECTION_LTR
            setPadding(dp(20), dp(12), dp(20), dp(24))
            setBackgroundColor(Color.rgb(7, 20, 27))
        }
        val scroll = ScrollView(this).apply { addView(column) }
        ViewCompat.setOnApplyWindowInsetsListener(scroll) { view, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        setContentView(scroll)
        addButton(column, text("العودة إلى اللياقة", "Back to Fitness")) { finish() }
        addText(column, text("خدماتك الصحية — اختيارية", "Your health services — optional"), 25f).apply {
            ViewCompat.setAccessibilityHeading(this, true)
        }
        addText(column, text(
            "هذه خدمات إضافية مستقلة عن إذن ملخص النشاط الأساسي. اختر فئة لقراءة بياناتها فقط بعد موافقتك في شاشة Android. لا يوجد زر سماح تلقائي من التطبيق.",
            "These services are separate from basic activity consent. Choose a category to read its data only after Android consent. The app cannot automatically grant access.",
        ))
        addText(column, text(
            "البيانات من Samsung Health أو مصدر متوافق عبر Health Connect، وقد لا توجد قراءات. لا يقيس الهاتف هنا النبض أو الضغط أو الأكسجين. لا تشخيص ولا توصيات دواء ولا استحقاق مكافآت. تبقى هذه القراءات على الجهاز ولا نرفعها للخادم.",
            "Data comes from Samsung Health or another compatible source through Health Connect and may be absent. This phone is not measuring heart rate, pressure or oxygen here. No diagnosis, medication advice or reward eligibility. These readings stay on-device and are not uploaded.",
        ))
        status = addText(column, text("جارٍ فحص Health Connect…", "Checking Health Connect…"))
        status.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
        addButton(column, text("إعدادات Health Connect وسحب الأذونات", "Health Connect settings / revoke access")) { openSystemSettings() }
        for (service in HealthService.entries) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(dp(16), dp(12), dp(16), dp(12))
                background = GradientDrawable().apply {
                    setColor(Color.rgb(19, 38, 48)); cornerRadius = dp(16).toFloat()
                }
            }
            column.addView(card, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(14) })
            addText(card, text(service.titleAr, service.titleEn), 20f).apply {
                ViewCompat.setAccessibilityHeading(this, true)
            }
            addText(card, text(service.purposeAr, service.purposeEn))
            labels[service] = addText(card, "").apply {
                accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
            }
            buttons[service] = addButton(card, text("اختيار هذه الخدمة", "Choose this service")) { choose(service) }
        }
        addText(column, text(
            "المجاميع تعرض نطاقها الزمني، والقراءات المفردة آخر سجل متاح خلال ٢٨ يومًا مع طريقة تسجيله. لا نطلب قراءة الخلفية أو السجل الأقدم. نزيل القيم المعروضة عند مغادرة هذه الشاشة.",
            "Totals show their time window. Individual readings show the latest available record within 28 days and its recording method. No background or extended-history access is requested. Displayed values are cleared when leaving this screen.",
        ))
        render()
    }

    override fun onResume() { super.onResume(); refreshPermissions() }

    override fun onStop() {
        generation++
        work?.cancel()
        grants = emptySet()
        results.clear()
        busy = null
        render()
        super.onStop()
    }

    private fun refreshPermissions(readAfterGrant: HealthService? = null) {
        val ticket = ++generation
        work?.cancel()
        available = HealthConnectClient.getSdkStatus(this) == HealthConnectClient.SDK_AVAILABLE
        if (!available) {
            grants = emptySet(); results.clear(); render()
            status.text = text("Health Connect غير متاح أو يحتاج تحديثًا. يمكنك فتح إعداداته أعلاه.", "Health Connect is unavailable or needs updating. Open its settings above.")
            return
        }
        work = lifecycleScope.launch {
            try {
                val client = HealthConnectClient.getOrCreate(this@HealthServicesActivity)
                grants = client.permissionController.getGrantedPermissions()
                results.keys.toList().filter { it.permission !in grants }.forEach { results.remove(it) }
                if (readAfterGrant != null && readAfterGrant.permission in grants) {
                    readMetric(readAfterGrant)
                } else if (ticket == generation) {
                    status.text = text("الأذونات محدثة. اضغط قراءة على الفئة المطلوبة.", "Permissions refreshed. Read the category you want.")
                    render()
                }
            } catch (cancelled: CancellationException) { throw cancelled
            } catch (_: Exception) {
                grants = emptySet(); results.clear(); render()
                status.text = text("تعذر فحص الأذونات. أعد فتح الشاشة أو إعدادات Health Connect.", "Could not check permissions. Reopen this screen or Health Connect settings.")
            }
        }
    }

    private fun choose(service: HealthService) {
        if (!available || busy != null) return
        if (service.permission in grants) { readMetric(service); return }
        AlertDialog.Builder(this)
            .setTitle(text(service.titleAr, service.titleEn))
            .setMessage(text(service.purposeAr, service.purposeEn) + "\n\n" + text(
                "سنطلب قراءة هذه الفئة فقط. الرفض لا يعطل التمارين أو الخدمات الأخرى. لإلغاء إذن سابق استخدم إعدادات Health Connect.",
                "Only this category's read permission will be requested. Denial does not block workouts or other services. Revoke existing access in Health Connect settings.",
            ))
            .setNegativeButton(text("ليس الآن", "Not now"), null)
            .setPositiveButton(text("مراجعة إذن Android", "Review Android permission")) { _, _ ->
                pending = service
                runCatching { permissionLauncher.launch(setOf(service.permission)) }.onFailure {
                    pending = null
                    status.text = text("تعذر فتح طلب الإذن. راجع Health Connect.", "Could not open consent. Check Health Connect.")
                }
            }.show()
    }

    private fun readMetric(service: HealthService) {
        val ticket = ++generation
        work?.cancel()
        busy = service
        results.remove(service)
        render()
        status.text = text("جارٍ قراءة الفئة المختارة…", "Reading the selected category…")
        work = lifecycleScope.launch {
            try {
                val source = HealthConnectServiceSource(HealthConnectClient.getOrCreate(this@HealthServicesActivity))
                val result = withContext(Dispatchers.IO) { HealthServicesReader(source).read(service) }
                val latestGrants = source.grantedPermissions()
                if (ticket != generation) return@launch
                grants = latestGrants
                results[service] = HealthServiceAccessPolicy.visibleResult(service, grants, result)
                status.text = text("انتهت القراءة المحلية. القيم المفقودة لا يتم تخمينها.", "Local read complete. Missing values are never guessed.")
            } catch (cancelled: CancellationException) { throw cancelled
            } catch (_: Exception) {
                if (ticket == generation) {
                    results[service] = HealthMetricResult(service, HealthMetricStatus.ERROR)
                    status.text = text("تعذرت القراءة. انتظر ثم حاول مجددًا.", "Read failed. Wait and try again.")
                }
            } finally {
                if (ticket == generation) { busy = null; render() }
            }
        }
    }

    private fun render() {
        for (service in HealthService.entries) {
            val result = HealthServiceAccessPolicy.visibleResult(service, grants, results[service])
            labels[service]?.text = if (busy == service) text("جارٍ القراءة…", "Reading…") else format(result)
            buttons[service]?.apply {
                isEnabled = available && busy == null
                text = if (service.permission in grants) this@HealthServicesActivity.text("قراءة البيانات", "Read data")
                    else this@HealthServicesActivity.text("شرح الفائدة وطلب القراءة", "Explain purpose / request read")
            }
        }
    }

    private fun format(result: HealthMetricResult): String = when (result.status) {
        HealthMetricStatus.PERMISSION_REQUIRED -> text("غير مسموح — لا نقرأ هذه الفئة.", "Not allowed — this category is not read.")
        HealthMetricStatus.NOT_LOADED -> text("مسموح، لم تُقرأ البيانات بعد.", "Allowed, data not read yet.")
        HealthMetricStatus.NO_DATA -> text("لا توجد بيانات في النطاق الحالي. سجّلها وشاركها من مصدر متوافق ثم أعد القراءة.", "No data in this window. Record and share it from a compatible source, then read again.")
        HealthMetricStatus.ERROR -> text("تعذرت القراءة؛ لا نعرض قيمة قديمة أو تقديرية. أعد المحاولة لاحقًا.", "Read failed; no stale or guessed value is shown. Try later.")
        HealthMetricStatus.READY -> buildString {
            append(result.values.joinToString("\n") { value ->
                val label = text(value.labelAr, value.labelEn)
                (if (label.isBlank()) "" else "$label: ") + String.format(Locale.forLanguageTag(language), "%.2f %s", value.value, value.unit)
            })
            result.observedAt?.let { append("\n" + text("تاريخ السجل: ", "Recorded: ") + date(it)) }
            result.windowStart?.let { append("\n" + text("النطاق: ", "Window: ") + date(it) + " — " + date(result.windowEnd ?: it)) }
            append("\n" + text("المصدر: ", "Source: ") + result.origins.sorted().joinToString().ifBlank { text("غير معروف", "Unknown") })
            result.recordingMethod?.let {
                append("\n" + when (it) {
                    Metadata.RECORDING_METHOD_MANUAL_ENTRY -> text("إدخال يدوي لدى المصدر — غير متحقق للمكافآت", "Manual source entry — not reward-verified")
                    Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED -> text("يصفه المصدر كتسجيل تلقائي — ليس تحقق مكافآت", "Source labels this automatic — not reward verification")
                    Metadata.RECORDING_METHOD_ACTIVELY_RECORDED -> text("يصفه المصدر كتسجيل نشط — ليس تحقق مكافآت", "Source labels this active — not reward verification")
                    else -> text("طريقة التسجيل غير معروفة", "Recording method unknown")
                })
            }
        }
    }

    private fun date(value: Instant): String = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.SHORT)
        .withLocale(Locale.forLanguageTag(language)).withZone(ZoneId.systemDefault()).format(value)

    private fun openSystemSettings() {
        runCatching { startActivity(Intent(HealthConnectClient.ACTION_HEALTH_CONNECT_SETTINGS)) }.onFailure {
            runCatching { startActivity(Intent(Intent.ACTION_VIEW, "https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata".toUri())) }
                .onFailure { status.text = text("لا يوجد تطبيق لفتح الإعدادات.", "No app can open settings.") }
        }
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
    private fun addText(parent: LinearLayout, value: String, size: Float = 16f) = TextView(this).apply {
        text = value; textSize = size; setTextColor(Color.rgb(239, 245, 247))
        setPadding(0, dp(6), 0, dp(6))
        parent.addView(this, LinearLayout.LayoutParams(-1, -2))
    }
    private fun addButton(parent: LinearLayout, value: String, action: () -> Unit) = Button(this).apply {
        text = value; isAllCaps = false; minHeight = dp(48)
        setOnClickListener { action() }
        parent.addView(this, LinearLayout.LayoutParams(-1, -2))
    }
}
