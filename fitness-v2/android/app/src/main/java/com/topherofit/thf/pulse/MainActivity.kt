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
import androidx.core.content.edit
import androidx.core.net.toUri
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
        private const val PENDING_BACKEND = "pending_backend_workouts"
        private const val SUMMARIES = "workout_summaries"
        private const val AUTH_PKCE_VERIFIER = "account_auth_pkce_verifier"
        private const val AUTH_STARTED_AT = "account_auth_started_at"
        private const val MAX_SUMMARY_BYTES = 256 * 1024
        private const val MAX_LOCAL_SUMMARIES = 120
    }

    private lateinit var web: WebView
    private lateinit var prefs: SharedPreferences
    private lateinit var healthRepository: HealthConnectRepository
    private lateinit var backendRepository: BackendSyncRepository
    private lateinit var accountAuthRepository: AccountAuthRepository
    private var sensorManager: SensorManager? = null
    private var stepSensor: Sensor? = null
    private var absoluteSteps = -1f
    private var sessionBaseline = -1f
    private var tts: TextToSpeech? = null
    private val healthFlushRunning = AtomicBoolean(false)
    private val backendFlushRunning = AtomicBoolean(false)
    private val accountExchangeRunning = AtomicBoolean(false)

    @Volatile
    private var backendAccessToken: String? = null

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
        backendRepository = BackendSyncRepository(BuildConfig.THF_BASE_URL)
        accountAuthRepository = AccountAuthRepository(BuildConfig.THF_BASE_URL)
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as? SensorManager
        stepSensor = sensorManager?.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) tts?.language = Locale("ar", "EG")
        }
        configureWebView()
        setContentView(web)
        web.loadUrl("file:///android_asset/pulse/index.html")
        handleAccountCallback(intent)
        lifecycleScope.launch { refreshHealthState() }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAccountCallback(intent)
    }

    @Suppress("SetJavaScriptEnabled")
    private fun configureWebView() {
        web = WebView(this)
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = false
            blockNetworkLoads = true
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
                if (isOnline()) flushPendingBackend()
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
        return value != null && AccountAuthContract.persistentHttpsBase(value) != null
    }

    private suspend fun refreshHealthState() {
        cachedHealthState = runCatching { healthRepository.connectionState() }
            .getOrElse { HealthConnectionState(healthRepository.availability(), false, emptySet(), HealthConnectRepository.REQUIRED_PERMISSIONS) }
    }

    private fun requestBackendSignIn() {
        if (!backendRepository.configured || !accountAuthRepository.configured) {
            dispatch(
                "thf:backend-auth",
                JSONObject().put("authenticated", false).put("error", "Production sync endpoint is not configured"),
            )
            return
        }
        val request = runCatching { AccountAuthContract.newRequest(BuildConfig.THF_ACCOUNT_URL) }
            .getOrElse { error ->
                dispatch(
                    "thf:backend-auth",
                    JSONObject().put("authenticated", false).put("error", error.message ?: "Account URL is not configured"),
                )
                return
            }
        prefs.edit {
            putString(AUTH_PKCE_VERIFIER, request.verifier)
            putLong(AUTH_STARTED_AT, System.currentTimeMillis())
        }
        val browser = Intent(Intent.ACTION_VIEW, request.startUrl.toUri()).apply {
            addCategory(Intent.CATEGORY_BROWSABLE)
        }
        runCatching { startActivity(browser) }
            .onSuccess {
                dispatch("thf:backend-auth", JSONObject().put("authenticated", false).put("pending", true))
            }
            .onFailure { error ->
                clearPendingAccountAuth()
                dispatch(
                    "thf:backend-auth",
                    JSONObject().put("authenticated", false).put("error", error.message ?: "No HTTPS browser is available"),
                )
            }
    }

    private fun handleAccountCallback(callbackIntent: Intent?) {
        val callback = callbackIntent?.data?.toString() ?: return
        callbackIntent.data = null
        val ticket = AccountAuthContract.callbackTicket(callback)
        val verifier = prefs.getString(AUTH_PKCE_VERIFIER, null)
        val startedAt = prefs.getLong(AUTH_STARTED_AT, 0L)
        val fresh = startedAt > 0L && System.currentTimeMillis() - startedAt in 0..AccountAuthContract.FLOW_TTL_MILLIS
        if (ticket == null || !fresh || !AccountAuthContract.validVerifier(verifier)) {
            clearPendingAccountAuth()
            dispatch(
                "thf:backend-auth",
                JSONObject().put("authenticated", false).put("error", "Invalid or expired account hand-off"),
            )
            return
        }
        if (!accountExchangeRunning.compareAndSet(false, true)) return
        lifecycleScope.launch {
            runCatching {
                withContext(Dispatchers.IO) { accountAuthRepository.consume(ticket, verifier.orEmpty()) }
            }.onSuccess { token ->
                backendAccessToken = backendRepository.validateAccessToken(token)
                prefs.edit { remove("backend_last_error") }
                dispatch(
                    "thf:backend-auth",
                    JSONObject().put("authenticated", true).put("persisted", false),
                )
                flushPendingBackend()
            }.onFailure { error ->
                backendAccessToken = null
                val message = error.message ?: error.javaClass.simpleName
                prefs.edit { putString("backend_last_error", message) }
                dispatch(
                    "thf:backend-auth",
                    JSONObject().put("authenticated", false).put("error", message),
                )
            }
            clearPendingAccountAuth()
            accountExchangeRunning.set(false)
        }
    }

    private fun clearPendingAccountAuth() {
        prefs.edit { remove(AUTH_PKCE_VERIFIER); remove(AUTH_STARTED_AT) }
    }

    private fun jsonArrayPreference(key: String): JSONArray = runCatching {
        JSONArray(prefs.getString(key, "[]") ?: "[]")
    }.getOrElse {
        prefs.edit { remove(key) }
        JSONArray()
    }

    /**
     * Version-aware local upsert used by both the offline history and the Health queue.
     * Replaying the same stable id/version is a no-op; a higher version replaces the
     * previous record and an older version cannot roll local facts back.
     */
    private fun upsertLocalRecord(key: String, item: JSONObject, maxEntries: Int): String {
        val id = item.optString("clientRecordId")
        require(id.matches(Regex("[A-Za-z0-9._:-]{8,120}"))) { "invalid clientRecordId" }
        val incomingVersion = item.optLong("recordVersion", 1L)
        require(incomingVersion in 1L..1_000_000L) { "invalid recordVersion" }

        val current = jsonArrayPreference(key)
        val next = JSONArray()
        var outcome = "inserted"
        var matched = false
        for (index in 0 until current.length()) {
            val existing = current.optJSONObject(index) ?: continue
            if (existing.optString("clientRecordId") != id) {
                next.put(existing)
                continue
            }
            if (matched) continue
            matched = true
            val existingVersion = existing.optLong("recordVersion", 1L)
            outcome = when {
                incomingVersion < existingVersion -> "stale"
                incomingVersion == existingVersion -> "duplicate"
                else -> "updated"
            }
            next.put(if (outcome == "updated") item else existing)
        }
        if (outcome == "inserted") next.put(item)

        val trimmed = JSONArray()
        val start = maxOf(0, next.length() - maxEntries)
        for (index in start until next.length()) trimmed.put(next.get(index))
        prefs.edit { putString(key, trimmed.toString()) }
        return outcome
    }

    private fun healthStatusJson(): JSONObject = JSONObject()
        .put("availability", cachedHealthState.availability)
        .put("connected", cachedHealthState.connected)
        .put("grantedCount", cachedHealthState.grantedPermissions.size)
        .put("requiredCount", HealthConnectRepository.REQUIRED_PERMISSIONS.size)
        .put("missingPermissions", JSONArray(cachedHealthState.missingPermissions.sorted()))
        .put("lastSync", prefs.getString("health_last_sync", ""))
        .put("lastError", prefs.getString("health_last_error", ""))
        .put("pendingWrites", jsonArrayPreference(PENDING_HEALTH).length())

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

    private fun openAccountResource(relativePath: String) {
        val base = AccountAuthContract.persistentHttpsBase(BuildConfig.THF_ACCOUNT_URL)
        if (base == null || relativePath !in setOf("privacy.html", "account-deletion.html")) {
            dispatch(
                "thf:account-resource",
                JSONObject().put("opened", false).put("error", "Approved account URL is not configured"),
            )
            return
        }
        runOnUiThread {
            runCatching {
                val intent = Intent(Intent.ACTION_VIEW, "$base$relativePath".toUri())
                    .addCategory(Intent.CATEGORY_BROWSABLE)
                startActivity(intent)
            }.onFailure { cause ->
                dispatch(
                    "thf:account-resource",
                    JSONObject().put("opened", false).put("error", cause.message ?: "Unable to open account resource"),
                )
            }
        }
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
                prefs.edit {
                    putString("health_last_sync", now)
                    remove("health_last_error")
                }
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
                prefs.edit { putString("health_last_error", message) }
                dispatch("thf:health-error", healthStatusJson().put("message", message))
            }
    }

    private fun enqueueSummaryForHealth(item: JSONObject): String =
        upsertLocalRecord(PENDING_HEALTH, item, MAX_LOCAL_SUMMARIES)

    private fun enqueueSummaryForBackend(item: JSONObject): String =
        upsertLocalRecord(PENDING_BACKEND, item, MAX_LOCAL_SUMMARIES)

    private suspend fun flushPendingHealth() {
        if (!healthFlushRunning.compareAndSet(false, true)) return
        try {
            refreshHealthState()
            if (!cachedHealthState.connected) return
            val pending = jsonArrayPreference(PENDING_HEALTH)
            val remaining = JSONArray()
            var written = 0
            var firstError: String? = null
            for (index in 0 until pending.length()) {
                val item = pending.optJSONObject(index)
                if (item == null) {
                    firstError = firstError ?: "Invalid queued workout"
                    continue
                }
                runCatching {
                    val startMillis = item.optLong(
                        "startedAtMs",
                        item.optLong("savedAt") - item.optLong("durationMin", 1) * 60_000L,
                    )
                    val endMillis = item.optLong("endedAtMs", item.optLong("savedAt", System.currentTimeMillis()))
                    require(startMillis > 0 && endMillis > startMillis) { "Invalid queued workout time" }
                    val workout = WorkoutForHealth(
                        clientRecordId = item.getString("clientRecordId"),
                        clientRecordVersion = item.optLong("recordVersion", 1L),
                        exerciseId = item.optString("id", "other"),
                        sport = item.optString("sport", item.optString("id", "other")),
                        title = item.optString("exercise", "THF workout"),
                        startTime = Instant.ofEpochMilli(startMillis),
                        endTime = Instant.ofEpochMilli(endMillis),
                        notes = "THF Fitness V2 · reps=${item.optInt("reps", 0)}",
                    )
                    withContext(Dispatchers.IO) { healthRepository.writeWorkout(workout) }
                }
                    .onSuccess { written += 1 }
                    .onFailure { error ->
                        remaining.put(item)
                        firstError = firstError ?: (error.message ?: error.javaClass.simpleName)
                    }
            }
            prefs.edit {
                putString(PENDING_HEALTH, remaining.toString())
                if (firstError == null) remove("health_last_error")
                else putString("health_last_error", firstError)
            }
            dispatch(
                "thf:health-write",
                JSONObject()
                    .put("written", written)
                    .put("pending", remaining.length())
                    .put("lastError", firstError ?: ""),
            )
            if (firstError != null) {
                dispatch("thf:health-error", healthStatusJson().put("message", firstError))
            }
        } finally {
            healthFlushRunning.set(false)
        }
    }

    private suspend fun flushPendingBackend() {
        if (!backendFlushRunning.compareAndSet(false, true)) return
        try {
            val token = backendAccessToken ?: return
            if (!backendRepository.configured || !isOnline()) return
            val pending = jsonArrayPreference(PENDING_BACKEND)
            val remaining = JSONArray()
            var synced = 0
            var firstError: String? = null
            for (index in 0 until pending.length()) {
                val item = pending.optJSONObject(index)
                if (item == null) {
                    firstError = firstError ?: "Invalid queued backend workout"
                    continue
                }
                runCatching {
                    withContext(Dispatchers.IO) { backendRepository.sync(token, item) }
                }.onSuccess {
                    synced += 1
                }.onFailure { error ->
                    remaining.put(item)
                    firstError = firstError ?: (error.message ?: error.javaClass.simpleName)
                    if (error is BackendSyncException && (error.statusCode == 401 || error.statusCode == 403)) {
                        backendAccessToken = null
                        dispatch(
                            "thf:backend-auth",
                            JSONObject().put("authenticated", false).put("error", "Account session expired"),
                        )
                    }
                }
                if (backendAccessToken == null) {
                    for (remainingIndex in index + 1 until pending.length()) {
                        pending.optJSONObject(remainingIndex)?.let { remaining.put(it) }
                    }
                    break
                }
            }
            prefs.edit {
                putString(PENDING_BACKEND, remaining.toString())
                putString("backend_last_sync", if (synced > 0) Instant.now().toString() else prefs.getString("backend_last_sync", ""))
                if (firstError == null) remove("backend_last_error")
                else putString("backend_last_error", firstError)
            }
            dispatch(
                "thf:backend-sync",
                JSONObject()
                    .put("synced", synced)
                    .put("pending", remaining.length())
                    .put("authenticated", backendAccessToken != null)
                    .put("lastError", firstError ?: ""),
            )
        } finally {
            backendFlushRunning.set(false)
        }
    }

    inner class PulseBridge {
        @JavascriptInterface
        fun status(): String = JSONObject()
            .put("mode", "offline_first")
            .put("version", BuildConfig.VERSION_NAME)
            .put("package", BuildConfig.APPLICATION_ID)
            .put("online", isOnline())
            .put("syncConfigured", validPersistentHttps(BuildConfig.THF_BASE_URL) && backendRepository.configured)
            .put("accountAuthConfigured", validPersistentHttps(BuildConfig.THF_ACCOUNT_URL) && accountAuthRepository.configured)
            .put("syncAuthenticated", backendAccessToken != null)
            .put("accountAuthPending", accountExchangeRunning.get() || prefs.contains(AUTH_PKCE_VERIFIER))
            .put("backendPending", jsonArrayPreference(PENDING_BACKEND).length())
            .put("backendLastSync", prefs.getString("backend_last_sync", ""))
            .put("backendLastError", prefs.getString("backend_last_error", ""))
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
        fun requestBackendSignIn() = runOnUiThread { this@MainActivity.requestBackendSignIn() }

        @JavascriptInterface
        fun openPrivacyPolicy() = this@MainActivity.openAccountResource("privacy.html")

        @JavascriptInterface
        fun openAccountDeletion() = this@MainActivity.openAccountResource("account-deletion.html")

        @JavascriptInterface
        fun clearBackendAccessToken() {
            backendAccessToken = null
            dispatch("thf:backend-auth", JSONObject().put("authenticated", false).put("signedOut", true))
        }

        @JavascriptInterface
        fun openHealthSettings() {
            runOnUiThread {
                runCatching { startActivity(Intent(HealthConnectClient.ACTION_HEALTH_CONNECT_SETTINGS)) }
                    .onFailure {
                        runCatching {
                            startActivity(Intent(Intent.ACTION_VIEW, "market://details?id=com.google.android.apps.healthdata".toUri()))
                        }.onFailure {
                            startActivity(
                                Intent(
                                    Intent.ACTION_VIEW,
                                    "https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata".toUri(),
                                ),
                            )
                        }
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
            prefs.edit { putFloat("step_baseline", sessionBaseline) }
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
            require(json != null && json.toByteArray(Charsets.UTF_8).size <= MAX_SUMMARY_BYTES) {
                "invalid workout summary size"
            }
            val item = JSONObject(json)
            val now = System.currentTimeMillis()
            val start = item.optLong("startedAtMs", now - item.optLong("durationMin", 1L) * 60_000L)
            val end = item.optLong("endedAtMs", now)
            require(start > 0 && end > start && end - start <= 48L * 60L * 60L * 1_000L) {
                "invalid workout summary time"
            }
            require((item.optJSONArray("sets")?.length() ?: 0) <= 1000) { "too many workout sets" }
            val clientId = WorkoutIdentity.stableClientRecordId(item.optString("clientRecordId"), start, item.optString("id", "other"))
            item.put("clientRecordId", clientId)
            item.put("recordVersion", maxOf(1L, item.optLong("recordVersion", 1L)))
            item.put("savedAt", now)
            item.put("endedAtMs", end)
            val localOutcome = upsertLocalRecord(SUMMARIES, item, MAX_LOCAL_SUMMARIES)
            val healthOutcome = if (localOutcome == "inserted" || localOutcome == "updated") {
                enqueueSummaryForHealth(item)
            } else {
                localOutcome
            }
            val backendOutcome = if (localOutcome == "inserted" || localOutcome == "updated") {
                enqueueSummaryForBackend(item)
            } else {
                localOutcome
            }
            if (healthOutcome == "inserted" || healthOutcome == "updated") {
                lifecycleScope.launch { flushPendingHealth() }
            }
            if (backendOutcome == "inserted" || backendOutcome == "updated") {
                lifecycleScope.launch { flushPendingBackend() }
            }
            JSONObject()
                .put("saved", localOutcome != "stale")
                .put("result", localOutcome)
                .put("clientRecordId", clientId)
                .put("healthQueued", healthOutcome == "inserted" || healthOutcome == "updated")
                .put("backendQueued", backendOutcome == "inserted" || backendOutcome == "updated")
                .toString()
        }.getOrElse { JSONObject().put("saved", false).put("error", it.javaClass.simpleName).toString() }

        @JavascriptInterface
        fun readSummaries(): String = jsonArrayPreference(SUMMARIES).toString()

        @JavascriptInterface
        fun setPref(key: String?, value: String?) {
            if (key != null) prefs.edit { putString("web_$key", value.orEmpty()) }
        }

        @JavascriptInterface
        fun getPref(key: String?): String = if (key == null) "" else prefs.getString("web_$key", "").orEmpty()
    }
}
