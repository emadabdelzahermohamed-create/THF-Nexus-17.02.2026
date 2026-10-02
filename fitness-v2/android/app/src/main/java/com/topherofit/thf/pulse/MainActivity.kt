package com.topherofit.thf.pulse

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.lifecycle.lifecycleScope
import java.time.Instant
import java.util.Locale
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : ComponentActivity(), SensorEventListener {
    companion object {
        private const val PREFS = "thf_fitness_v2_local"
        private const val PENDING_HEALTH = "pending_health_workouts"
        private const val SUMMARIES = "workout_summaries"
    }

    private lateinit var web: WebView
    private lateinit var prefs: SharedPreferences
    private lateinit var healthRepository: HealthConnectRepository
    private var sensorManager: SensorManager? = null
    private var stepSensor: Sensor? = null
    private var absoluteSteps = -1f
    private var sessionBaseline = -1f
    private var tts: TextToSpeech? = null
    private val healthFlushRunning = AtomicBoolean(false)

    @Volatile
    private var cachedHealthState = HealthConnectionState("CHECKING", false, emptySet(), HealthConnectRepository.REQUIRED_PERMISSIONS)

    private val activityPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        dispatch("thf:activity-permission", JSONObject().put("granted", granted))
        if (granted) registerStepSensor()
    }

    private val healthPermissionLauncher = registerForActivityResult(
        PermissionController.createRequestPermissionResultContract(),
    ) { granted ->
        lifecycleScope.launch {
            refreshHealthState()
            dispatch(
                "thf:health-permission",
                healthStatusJson().put("grantedCount", granted.size),
            )
            if (cachedHealthState.connected) {
                flushPendingHealth()
                syncHealthInternal()
            }
        }
    }

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE)
        healthRepository = HealthConnectRepository(this)
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as? SensorManager
        stepSensor = sensorManager?.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) tts?.language = Locale("ar", "EG")
        }
        configureWebView()
        setContentView(web)
        web.loadUrl("file:///android_asset/pulse/index.html")
        lifecycleScope.launch { refreshHealthState() }
    }

    @Suppress("SetJavaScriptEnabled")
    private fun configureWebView() {
        web = WebView(this)
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            mediaPlaybackRequiresUserGesture = false
            @Suppress("DEPRECATION")
            allowFileAccessFromFileURLs = false
            @Suppress("DEPRECATION")
            allowUniversalAccessFromFileURLs = false
        }
        web.addJavascriptInterface(PulseBridge(), "PulseNative")
        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                return !request.url.scheme.equals("file", ignoreCase = true)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        registerStepSensor()
        if (::healthRepository.isInitialized) {
            lifecycleScope.launch {
                refreshHealthState()
                dispatch("thf:health-status", healthStatusJson())
                if (cachedHealthState.connected) flushPendingHealth()
            }
        }
    }

    override fun onPause() {
        sensorManager?.unregisterListener(this)
        super.onPause()
    }

    override fun onDestroy() {
        tts?.stop()
        tts?.shutdown()
        web.destroy()
        super.onDestroy()
    }

    private fun registerStepSensor() {
        if (stepSensor != null && hasActivityPermission()) {
            sensorManager?.registerListener(this, stepSensor, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    private fun hasActivityPermission(): Boolean =
        Build.VERSION.SDK_INT < 29 || checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type == Sensor.TYPE_STEP_COUNTER && event.values.isNotEmpty()) absoluteSteps = event.values[0]
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    private fun isOnline(): Boolean {
        val manager = getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager ?: return false
        val network = manager.activeNetwork ?: return false
        val capabilities = manager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
            capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    private fun validPersistentHttps(value: String?): Boolean {
        if (value.isNullOrBlank()) return false
        return runCatching {
            val uri = Uri.parse(value.trim())
            val host = uri.host.orEmpty().lowercase()
            val blocked = setOf("trycloudflare.com", "ngrok-free.app", "ngrok.io", "localhost", "127.0.0.1", ".local")
            uri.scheme.equals("https", true) && host.isNotBlank() && uri.userInfo == null &&
                blocked.none { host == it || host.endsWith(".$it") }
        }.getOrDefault(false)
    }

    private suspend fun refreshHealthState() {
        cachedHealthState = runCatching { healthRepository.connectionState() }
            .getOrElse { HealthConnectionState(healthRepository.availability(), false, emptySet(), HealthConnectRepository.REQUIRED_PERMISSIONS) }
    }

    private fun healthStatusJson(): JSONObject = JSONObject()
        .put("availability", cachedHealthState.availability)
        .put("connected", cachedHealthState.connected)
        .put("grantedCount", cachedHealthState.grantedPermissions.size)
        .put("requiredCount", HealthConnectRepository.REQUIRED_PERMISSIONS.size)
        .put("missingPermissions", JSONArray(cachedHealthState.missingPermissions.sorted()))
        .put("lastSync", prefs.getString("health_last_sync", ""))
        .put("lastError", prefs.getString("health_last_error", ""))
        .put("pendingWrites", JSONArray(prefs.getString(PENDING_HEALTH, "[]")).length())

    private fun dispatch(name: String, payload: JSONObject) {
        if (!::web.isInitialized) return
        val script = "window.dispatchEvent(new CustomEvent(${JSONObject.quote(name)},{detail:${payload}}));"
        runOnUiThread { web.evaluateJavascript(script, null) }
    }

    private fun requestHealthPermissions() {
        lifecycleScope.launch {
            refreshHealthState()
            if (cachedHealthState.availability != "AVAILABLE") {
                dispatch("thf:health-error", healthStatusJson().put("message", "Health Connect unavailable"))
                return@launch
            }
            if (cachedHealthState.connected) {
                dispatch("thf:health-permission", healthStatusJson())
                return@launch
            }
            healthPermissionLauncher.launch(HealthConnectRepository.REQUIRED_PERMISSIONS)
        }
    }

    private fun syncHealth() {
        lifecycleScope.launch { syncHealthInternal() }
    }

    private suspend fun syncHealthInternal() {
        refreshHealthState()
        if (!cachedHealthState.connected) {
            dispatch("thf:health-error", healthStatusJson().put("message", "Permissions required"))
            return
        }
        runCatching { withContext(Dispatchers.IO) { healthRepository.readRecent() } }
            .onSuccess { snapshot ->
                val now = Instant.now().toString()
                prefs.edit().putString("health_last_sync", now).remove("health_last_error").apply()
                dispatch(
                    "thf:health-sync",
                    JSONObject()
                        .put("status", "SYNCED")
                        .put("steps", snapshot.steps)
                        .put("distanceMeters", snapshot.distanceMeters)
                        .put("activeCaloriesKcal", snapshot.activeCaloriesKcal)
                        .put("exerciseSessions", snapshot.exerciseSessions)
                        .put("origins", JSONArray(snapshot.origins.sorted()))
                        .put("latestSessionEnd", snapshot.latestSessionEnd?.toString() ?: "")
                        .put("lastSync", now),
                )
            }
            .onFailure { error ->
                val message = error.message ?: error.javaClass.simpleName
                prefs.edit().putString("health_last_error", message).apply()
                dispatch("thf:health-error", healthStatusJson().put("message", message))
            }
    }

    private fun enqueueSummaryForHealth(item: JSONObject) {
        val pending = JSONArray(prefs.getString(PENDING_HEALTH, "[]"))
        val id = item.getString("clientRecordId")
        for (index in 0 until pending.length()) {
            if (pending.getJSONObject(index).optString("clientRecordId") == id) return
        }
        pending.put(item)
        prefs.edit().putString(PENDING_HEALTH, pending.toString()).apply()
    }

    private suspend fun flushPendingHealth() {
        if (!healthFlushRunning.compareAndSet(false, true)) return
        try {
            refreshHealthState()
            if (!cachedHealthState.connected) return
            val pending = JSONArray(prefs.getString(PENDING_HEALTH, "[]"))
            val remaining = JSONArray()
            var written = 0
            for (index in 0 until pending.length()) {
                val item = pending.getJSONObject(index)
                val startMillis = item.optLong("startedAtMs", item.optLong("savedAt") - item.optLong("durationMin", 1) * 60_000L)
                val endMillis = item.optLong("endedAtMs", item.optLong("savedAt", System.currentTimeMillis()))
                val workout = WorkoutForHealth(
                    clientRecordId = item.getString("clientRecordId"),
                    clientRecordVersion = item.optLong("recordVersion", 1L),
                    exerciseId = item.optString("id", "other"),
                    sport = item.optString("sport", item.optString("id", "other")),
                    title = item.optString("exercise", "THF workout"),
                    startTime = Instant.ofEpochMilli(startMillis),
                    endTime = Instant.ofEpochMilli(maxOf(startMillis + 1_000L, endMillis)),
                    notes = "THF Fitness V2 · reps=${item.optInt("reps", 0)}",
                )
                runCatching { withContext(Dispatchers.IO) { healthRepository.writeWorkout(workout) } }
                    .onSuccess { written += 1 }
                    .onFailure { remaining.put(item) }
            }
            prefs.edit().putString(PENDING_HEALTH, remaining.toString()).apply()
            dispatch(
                "thf:health-write",
                JSONObject().put("written", written).put("pending", remaining.length()),
            )
        } finally {
            healthFlushRunning.set(false)
        }
    }

    inner class PulseBridge {
        @JavascriptInterface
        fun status(): String = JSONObject()
            .put("mode", "offline_first")
            .put("version", BuildConfig.VERSION_NAME)
            .put("package", BuildConfig.APPLICATION_ID)
            .put("online", isOnline())
            .put("syncConfigured", validPersistentHttps(BuildConfig.THF_BASE_URL))
            .put("stepSensorAvailable", stepSensor != null)
            .put("activityPermission", hasActivityPermission())
            .put("sessionSteps", sessionSteps())
            .put("health", healthStatusJson())
            .toString()

        @JavascriptInterface
        fun healthStatus(): String = healthStatusJson().toString()

        @JavascriptInterface
        fun requestHealthPermissions() = runOnUiThread { this@MainActivity.requestHealthPermissions() }

        @JavascriptInterface
        fun syncHealth() = this@MainActivity.syncHealth()

        @JavascriptInterface
        fun openHealthSettings() {
            runOnUiThread {
                runCatching { startActivity(Intent(HealthConnectClient.ACTION_HEALTH_CONNECT_SETTINGS)) }
                    .onFailure {
                        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.google.android.apps.healthdata")))
                    }
            }
        }

        @JavascriptInterface
        fun requestActivityPermission() {
            if (Build.VERSION.SDK_INT < 29 || hasActivityPermission()) {
                dispatch("thf:activity-permission", JSONObject().put("granted", true))
            } else {
                runOnUiThread { activityPermissionLauncher.launch(Manifest.permission.ACTIVITY_RECOGNITION) }
            }
        }

        @JavascriptInterface
        fun beginStepSession() {
            sessionBaseline = if (absoluteSteps >= 0) absoluteSteps else -1f
            prefs.edit().putFloat("step_baseline", sessionBaseline).apply()
        }

        @JavascriptInterface
        fun sessionSteps(): Int {
            val baseline = if (sessionBaseline >= 0) sessionBaseline else prefs.getFloat("step_baseline", -1f)
            return if (absoluteSteps < 0 || baseline < 0) 0 else maxOf(0, (absoluteSteps - baseline).toInt())
        }

        @JavascriptInterface
        fun speak(text: String?, languageTag: String?) {
            if (text.isNullOrBlank()) return
            runOnUiThread {
                val locale = if (languageTag.orEmpty().lowercase().startsWith("ar")) Locale("ar", "EG") else Locale.US
                tts?.language = locale
                tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "thf-fitness-v2")
            }
        }

        @JavascriptInterface
        fun saveSummary(json: String?): String = runCatching {
            var summaries = JSONArray(prefs.getString(SUMMARIES, "[]"))
            val item = JSONObject(json ?: "{}")
            val now = System.currentTimeMillis()
            val start = item.optLong("startedAtMs", now - item.optLong("durationMin", 1L) * 60_000L)
            val clientId = WorkoutIdentity.stableClientRecordId(item.optString("clientRecordId"), start, item.optString("id", "other"))
            item.put("clientRecordId", clientId)
            item.put("recordVersion", maxOf(1L, item.optLong("recordVersion", 1L)))
            item.put("savedAt", now)
            if (!item.has("endedAtMs")) item.put("endedAtMs", now)
            summaries.put(item)
            if (summaries.length() > 120) {
                val trimmed = JSONArray()
                for (index in summaries.length() - 120 until summaries.length()) trimmed.put(summaries.get(index))
                summaries = trimmed
            }
            prefs.edit().putString(SUMMARIES, summaries.toString()).apply()
            enqueueSummaryForHealth(item)
            lifecycleScope.launch { flushPendingHealth() }
            JSONObject().put("saved", true).put("clientRecordId", clientId).put("healthQueued", true).toString()
        }.getOrElse { JSONObject().put("saved", false).put("error", it.javaClass.simpleName).toString() }

        @JavascriptInterface
        fun readSummaries(): String = prefs.getString(SUMMARIES, "[]") ?: "[]"

        @JavascriptInterface
        fun setPref(key: String?, value: String?) {
            if (key != null) prefs.edit().putString("web_$key", value.orEmpty()).apply()
        }

        @JavascriptInterface
        fun getPref(key: String?): String = if (key == null) "" else prefs.getString("web_$key", "").orEmpty()
    }
}
