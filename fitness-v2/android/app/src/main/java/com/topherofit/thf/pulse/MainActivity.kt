package com.topherofit.thf.pulse

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
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

class MainActivity : ComponentActivity() {
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
    private lateinit var foundingHeroBilling: FoundingHeroBilling
    private lateinit var motionEngine: MotionSessionEngine
    private var lastEndedMotionEvidence: MotionEvidence? = null
    private var pendingActivityStart: Pair<ActivityMode, Double>? = null
    private var pendingWorkoutStart: Pair<String, MotionSensorProfile>? = null
    private var tts: TextToSpeech? = null
    private val healthFlushRunning = AtomicBoolean(false)
    private val healthSyncGate = HealthSyncGate()
    @Volatile private var healthSyncing = false
    private val backendFlushRunning = AtomicBoolean(false)
    private val accountExchangeRunning = AtomicBoolean(false)

    @Volatile
    private var backendAccessToken: String? = null

    @Volatile
    private var cachedHealthState = HealthConnectionState(
        availability = "CHECKING",
        connected = false,
        readPermissionsGranted = false,
        writePermissionsGranted = false,
        grantedPermissions = emptySet(),
        missingReadPermissions = HealthConnectRepository.READ_PERMISSIONS,
        missingWritePermissions = HealthConnectRepository.WRITE_PERMISSIONS,
        missingPermissions = HealthConnectRepository.REQUIRED_PERMISSIONS,
    )

    @Volatile
    private var cachedBillingState = FoundingHeroBillingState(configured = BuildConfig.THF_PLAY_LICENSE_KEY.isNotBlank())

    private val activityPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        dispatch("thf:activity-permission", JSONObject().put("granted", granted))
        if (granted) {
            val workout = pendingWorkoutStart
            if (workout != null) {
                pendingWorkoutStart = null
                startWorkoutTracking(workout.first, workout.second)
            }
            startPendingActivityIfReady()
        } else {
            pendingWorkoutStart = null
            pendingActivityStart = null
        }
        if (granted && ::motionEngine.isInitialized && motionEngine.currentState().hostResumed && !ActivityTrackingService.hasActiveTracking()) {
            motionEngine.onHostPause()
            motionEngine.onHostResume()
        }
    }

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        dispatch("thf:notification-permission", JSONObject().put("granted", granted))
    }

    private val locationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions(),
    ) { result ->
        val granted = result[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
            result[Manifest.permission.ACCESS_COARSE_LOCATION] == true || hasLocationPermission()
        dispatch("thf:location-permission", JSONObject().put("granted", granted))
        if (granted) startPendingActivityIfReady() else pendingActivityStart = null
    }

    private val healthReadPermissionLauncher = registerForActivityResult(
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
                syncHealth()
            }
        }
    }

    private val healthWritePermissionLauncher = registerForActivityResult(
        PermissionController.createRequestPermissionResultContract(),
    ) { granted ->
        lifecycleScope.launch {
            refreshHealthState()
            dispatch(
                "thf:health-write-permission",
                healthStatusJson().put("grantedCount", granted.size),
            )
            if (cachedHealthState.writePermissionsGranted) flushPendingHealth()
        }
    }

    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE)
        healthRepository = HealthConnectRepository(this)
        backendRepository = BackendSyncRepository(BuildConfig.THF_BASE_URL)
        accountAuthRepository = AccountAuthRepository(BuildConfig.THF_BASE_URL)
        foundingHeroBilling = FoundingHeroBilling(this, BuildConfig.THF_PLAY_LICENSE_KEY) { next ->
            cachedBillingState = next
            dispatch("thf:billing-status", next.toJson())
        }
        motionEngine = MotionSessionEngine(AndroidMotionSensorGateway(this))
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
        if (::prefs.isInitialized) clearExpiredPendingAccountAuth()
        if (::motionEngine.isInitialized && !ActivityTrackingService.hasActiveTracking()) motionEngine.onHostResume()
        if (::foundingHeroBilling.isInitialized) foundingHeroBilling.start()
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
        if (::motionEngine.isInitialized) motionEngine.onHostPause()
        super.onPause()
    }

    override fun onDestroy() {
        tts?.stop()
        tts?.shutdown()
        if (::foundingHeroBilling.isInitialized) foundingHeroBilling.close()
        web.destroy()
        super.onDestroy()
    }

    private fun hasActivityPermission(): Boolean =
        Build.VERSION.SDK_INT < 29 || checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED

    private fun hasLocationPermission(): Boolean =
        checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    private fun startPendingActivityIfReady() {
        val pending = pendingActivityStart ?: return
        if (!hasLocationPermission()) return
        if (pending.first.usesSteps && !hasActivityPermission()) {
            if (Build.VERSION.SDK_INT >= 29) activityPermissionLauncher.launch(Manifest.permission.ACTIVITY_RECOGNITION)
            return
        }
        pendingActivityStart = null
        startActivityTracking(pending.first, pending.second)
    }

    private fun startActivityTracking(mode: ActivityMode, weightKg: Double) {
        requestNotificationPermissionIfNeeded()
        if (::motionEngine.isInitialized) motionEngine.onHostPause()
        ActivityTrackingService.startActivity(this, mode, weightKg)
        dispatch("thf:activity-started", activitySnapshotJson(ActivityTrackingService.activitySnapshot()))
    }

    private fun startWorkoutTracking(sessionId: String, profile: MotionSensorProfile) {
        requestNotificationPermissionIfNeeded()
        if (::motionEngine.isInitialized) motionEngine.onHostPause()
        ActivityTrackingService.startWorkout(this, sessionId, profile)
        dispatch(
            "thf:motion-started",
            JSONObject().put("active", true).put("sessionId", sessionId).put("profile", profile.wireName),
        )
    }

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
            .getOrElse {
                HealthConnectionState(
                    availability = healthRepository.availability(),
                    connected = false,
                    readPermissionsGranted = false,
                    writePermissionsGranted = false,
                    grantedPermissions = emptySet(),
                    missingReadPermissions = HealthConnectRepository.READ_PERMISSIONS,
                    missingWritePermissions = HealthConnectRepository.WRITE_PERMISSIONS,
                    missingPermissions = HealthConnectRepository.REQUIRED_PERMISSIONS,
                )
            }
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

    private fun hasFreshPendingAccountAuth(nowMillis: Long = System.currentTimeMillis()): Boolean {
        val verifier = prefs.getString(AUTH_PKCE_VERIFIER, null)
        val startedAt = prefs.getLong(AUTH_STARTED_AT, 0L)
        return AccountAuthContract.validVerifier(verifier) && AccountAuthContract.flowIsFresh(startedAt, nowMillis)
    }

    private fun clearExpiredPendingAccountAuth() {
        val hasPendingState = prefs.contains(AUTH_PKCE_VERIFIER) || prefs.contains(AUTH_STARTED_AT)
        if (hasPendingState && !hasFreshPendingAccountAuth()) clearPendingAccountAuth()
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

    private fun healthStatusJson(): JSONObject {
        val lastSync = prefs.getString("health_last_sync", "").orEmpty()
        val lastErrorCode = prefs.getString("health_last_error_code", "")
        val recordsRead = prefs.getInt("health_last_records_read", 0)
        val verifiedRecords = prefs.getInt("health_last_verified_records", 0)
        val excludedRecords = prefs.getInt("health_last_excluded_records", 0)
        val duplicateRecords = prefs.getInt("health_last_duplicate_records", 0)
        val uxState = HealthUxStateClassifier.classify(
            HealthUxInput(
                availability = cachedHealthState.availability,
                readPermissionsGranted = cachedHealthState.readPermissionsGranted,
                syncing = healthSyncing,
                hasSuccessfulSync = lastSync.isNotBlank(),
                recordsRead = recordsRead,
                verifiedRecords = verifiedRecords,
                lastErrorCode = lastErrorCode,
            ),
        )
        return JSONObject()
            .put("availability", cachedHealthState.availability)
            .put("connected", cachedHealthState.connected)
            .put("uxState", uxState.name)
            .put("grantedCount", cachedHealthState.grantedPermissions.size)
            .put("readPermissionsGranted", cachedHealthState.readPermissionsGranted)
            .put("writePermissionsGranted", cachedHealthState.writePermissionsGranted)
            .put("requiredCount", HealthConnectRepository.READ_PERMISSIONS.size)
            .put("requiredReadCount", HealthConnectRepository.READ_PERMISSIONS.size)
            .put("optionalWriteCount", HealthConnectRepository.WRITE_PERMISSIONS.size)
            .put("missingPermissions", JSONArray(cachedHealthState.missingReadPermissions.sorted()))
            .put("missingReadPermissions", JSONArray(cachedHealthState.missingReadPermissions.sorted()))
            .put("missingWritePermissions", JSONArray(cachedHealthState.missingWritePermissions.sorted()))
            .put("recordsRead", recordsRead)
            .put("verifiedRecords", verifiedRecords)
            .put("excludedManualOrUnknownRecords", excludedRecords)
            .put("duplicateRecordsExcluded", duplicateRecords)
            .put("lastSync", lastSync)
            .put("lastError", prefs.getString("health_last_error", ""))
            .put("pendingWrites", jsonArrayPreference(PENDING_HEALTH).length())
    }

    private fun motionCapabilitiesJson(capabilities: SensorCapabilities): JSONObject = JSONObject()
        .put("stepCounter", capabilities.stepCounter)
        .put("stepDetector", capabilities.stepDetector)
        .put("accelerometer", capabilities.accelerometer)
        .put("gyroscope", capabilities.gyroscope)
        .put("activityRecognitionPermission", capabilities.activityRecognitionPermission)

    private fun motionSessionJson(state: MotionSessionState): JSONObject = JSONObject()
        .put("active", state.active)
        .put("sessionId", state.sessionId ?: "")
        .put("hostResumed", state.hostResumed)
        .put("profile", state.profile.wireName)
        .put("capabilities", motionCapabilitiesJson(state.capabilities))

    private fun activitySnapshotJson(snapshot: ActivitySnapshot): JSONObject {
        val route = JSONArray()
        snapshot.route.forEach { point ->
            route.put(
                JSONObject()
                    .put("lat", point.latitude)
                    .put("lng", point.longitude)
                    .put("altitudeMetres", point.altitudeMetres)
                    .put("accuracyMetres", point.accuracyMetres)
                    .put("elapsedMs", point.elapsedMs),
            )
        }
        return JSONObject()
            .put("active", snapshot.active)
            .put("paused", snapshot.paused)
            .put("phase", snapshot.phase.wireName)
            .put("mode", snapshot.mode?.wireName ?: "")
            .put("startedAtWallMs", snapshot.startedAtWallMs)
            .put("elapsedMs", snapshot.elapsedMs)
            .put("distanceMetres", snapshot.distanceMetres)
            .put("steps", snapshot.stepDelta)
            .put("currentSpeedKph", snapshot.currentSpeedKph)
            .put("averageSpeedKph", snapshot.averageSpeedKph)
            .put("paceMinutesPerKm", snapshot.paceMinutesPerKm)
            .put("estimatedCaloriesKcal", snapshot.estimatedCaloriesKcal)
            .put("gpsPointCount", snapshot.gpsPointCount)
            .put("lastAccuracyMetres", snapshot.lastAccuracyMetres)
            .put("observedAccuracyMetres", snapshot.observedAccuracyMetres)
            .put("gpsFixState", snapshot.gpsFixState)
            .put("route", route)
    }

    private fun motionEvidenceJson(evidence: MotionEvidence): JSONObject = JSONObject()
        .put("available", true)
        .put("sessionId", evidence.sessionId)
        .put("startedAtWallMs", evidence.startedAtWallMs)
        .put("endedAtWallMs", evidence.endedAtWallMs)
        .put("elapsedDurationMs", evidence.elapsedDurationMs)
        .put("activeDurationMs", evidence.activeDurationMs)
        .put("stepDelta", evidence.stepDelta)
        .put("stepDetectorCount", evidence.stepDetectorCount)
        .put("counterResetCount", evidence.counterResetCount)
        .put("accelerometerSampleCount", evidence.accelerometerSampleCount)
        .put("gyroscopeSampleCount", evidence.gyroscopeSampleCount)
        .put("accelerometerMagnitudeMean", evidence.accelerometerMagnitudeMean)
        .put("accelerometerMagnitudeVariance", evidence.accelerometerMagnitudeVariance)
        .put("accelerometerMagnitudePeak", evidence.accelerometerMagnitudePeak)
        .put("gyroscopeMagnitudeMean", evidence.gyroscopeMagnitudeMean)
        .put("gyroscopeMagnitudeVariance", evidence.gyroscopeMagnitudeVariance)
        .put("gyroscopeMagnitudePeak", evidence.gyroscopeMagnitudePeak)
        .put("activeMotionMs", evidence.activeMotionMs)
        .put("stationaryFraction", evidence.stationaryFraction)
        .put("interruptionMs", evidence.interruptionMs)
        .put("localConfidence", evidence.localConfidence)
        .put("detectedActivity", evidence.detectedActivity.name)
        .put("activityConfidence", evidence.activityConfidence)
        .put("plausibleForRewards", evidence.plausibleForRewards)
        .put("plausibilityReasons", org.json.JSONArray(evidence.plausibilityReasons))
        .put("evidenceDigest", evidence.evidenceDigest)
        .put("capabilities", motionCapabilitiesJson(evidence.capabilities))

    private fun billingStatusJson(): JSONObject = cachedBillingState.toJson()

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
            if (cachedHealthState.readPermissionsGranted) {
                dispatch("thf:health-permission", healthStatusJson())
                return@launch
            }
            healthReadPermissionLauncher.launch(HealthConnectRepository.READ_PERMISSIONS)
        }
    }

    private fun requestHealthWritePermission() {
        lifecycleScope.launch {
            refreshHealthState()
            if (cachedHealthState.availability != "AVAILABLE") {
                dispatch("thf:health-error", healthStatusJson().put("message", "Health Connect unavailable"))
                return@launch
            }
            if (cachedHealthState.writePermissionsGranted) {
                dispatch("thf:health-write-permission", healthStatusJson())
                flushPendingHealth()
                return@launch
            }
            healthWritePermissionLauncher.launch(HealthConnectRepository.WRITE_PERMISSIONS)
        }
    }

    private fun syncHealth(): String = when (val decision = healthSyncGate.tryStart()) {
        HealthSyncDecision.Started -> {
            healthSyncing = true
            dispatch("thf:health-status", healthStatusJson())
            lifecycleScope.launch { syncHealthInternal() }
            JSONObject().put("status", "STARTED").toString()
        }
        is HealthSyncDecision.Wait -> JSONObject()
            .put("status", "WAIT")
            .put("retryAfterMs", decision.retryAfterMs)
            .toString()
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

    private fun isHealthRateLimited(error: Throwable): Boolean {
        var current: Throwable? = error
        while (current != null) {
            val text = current.message.orEmpty()
            if (text.contains("rate limit", ignoreCase = true) || text.contains("quota", ignoreCase = true)) return true
            current = current.cause
        }
        return false
    }

    private suspend fun syncHealthInternal() {
        var rateLimited = false
        try {
            refreshHealthState()
            if (!cachedHealthState.connected) {
                dispatch(
                    "thf:health-error",
                    healthStatusJson()
                        .put("code", "PERMISSIONS_REQUIRED")
                        .put("message", "Health Connect permissions are required")
                        .put("retryAfterMs", 0),
                )
                return
            }
            runCatching { withContext(Dispatchers.IO) { healthRepository.readRecent() } }
                .onSuccess { snapshot ->
                    val now = Instant.now().toString()
                    prefs.edit {
                        putString("health_last_sync", now)
                        putInt("health_last_records_read", snapshot.recordsRead)
                        putInt("health_last_verified_records", snapshot.verifiedRecords)
                        putInt("health_last_excluded_records", snapshot.excludedManualOrUnknownRecords)
                        putInt("health_last_duplicate_records", snapshot.duplicateRecordsExcluded)
                        remove("health_last_error")
                        remove("health_last_error_code")
                    }
                    healthSyncing = false
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
                            .put("recordsRead", snapshot.recordsRead)
                            .put("verifiedRecords", snapshot.verifiedRecords)
                            .put("excludedManualOrUnknownRecords", snapshot.excludedManualOrUnknownRecords)
                            .put("duplicateRecordsExcluded", snapshot.duplicateRecordsExcluded)
                            .put("uxState", if (snapshot.recordsRead == 0) "SYNCED_NO_RECORDS" else if (snapshot.verifiedRecords == 0) "SYNCED_UNVERIFIED_ONLY" else "SYNCED_VERIFIED")
                            .put("lastSync", now),
                    )
                }
                .onFailure { error ->
                    rateLimited = isHealthRateLimited(error)
                    val code = if (rateLimited) "RATE_LIMITED" else "SYNC_FAILED"
                    val message = if (rateLimited) {
                        "Health Connect is temporarily rate limited. Please wait before syncing again."
                    } else {
                        error.message ?: error.javaClass.simpleName
                    }
                    val retryAfterMs = if (rateLimited) 60_000L else 5_000L
                    prefs.edit {
                        putString("health_last_error", message)
                        putString("health_last_error_code", code)
                    }
                    healthSyncing = false
                    dispatch(
                        "thf:health-error",
                        healthStatusJson()
                            .put("code", code)
                            .put("message", message)
                            .put("retryAfterMs", retryAfterMs),
                    )
                }
        } finally {
            healthSyncing = false
            healthSyncGate.finish(rateLimited = rateLimited)
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
            if (!cachedHealthState.writePermissionsGranted) {
                dispatch(
                    "thf:health-write",
                    JSONObject()
                        .put("written", 0)
                        .put("pending", jsonArrayPreference(PENDING_HEALTH).length())
                        .put("writePermissionRequired", true),
                )
                return
            }
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
            .put("accountAuthPending", accountExchangeRunning.get() || hasFreshPendingAccountAuth())
            .put("backendPending", jsonArrayPreference(PENDING_BACKEND).length())
            .put("backendLastSync", prefs.getString("backend_last_sync", ""))
            .put("backendLastError", prefs.getString("backend_last_error", ""))
            .put("stepSensorAvailable", motionEngine.capabilities().stepCounter)
            .put("activityPermission", hasActivityPermission())
            .put("sessionSteps", sessionSteps())
            .put("motionCapabilities", motionCapabilitiesJson(motionEngine.capabilities()))
            .put("motionSession", motionSessionJson(motionEngine.currentState()))
            .put("trackingServiceActive", ActivityTrackingService.hasActiveTracking())
            .put("activitySession", activitySnapshotJson(ActivityTrackingService.activitySnapshot()))
            .put("health", healthStatusJson())
            .put("billing", billingStatusJson())
            .toString()

        @JavascriptInterface
        fun healthStatus(): String = healthStatusJson().toString()

        @JavascriptInterface
        fun billingStatus(): String = billingStatusJson().toString()

        @JavascriptInterface
        fun purchaseFoundingHero() = runOnUiThread { foundingHeroBilling.launchPurchase() }

        @JavascriptInterface
        fun restoreFoundingHero() = runOnUiThread { foundingHeroBilling.refresh() }

        @JavascriptInterface
        fun requestHealthPermissions() = runOnUiThread { this@MainActivity.requestHealthPermissions() }

        @JavascriptInterface
        fun requestHealthWritePermission() = runOnUiThread { this@MainActivity.requestHealthWritePermission() }

        @JavascriptInterface
        fun syncHealth(): String = this@MainActivity.syncHealth()

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
        fun beginMotionSession(sessionId: String?, profile: String?): String = runCatching {
            val id = requireNotNull(sessionId).trim()
            require(id.isNotBlank()) { "sessionId is required" }
            val sensorProfile = MotionSensorProfile.fromWire(profile)
            if (Build.VERSION.SDK_INT >= 34 && !hasActivityPermission()) {
                pendingWorkoutStart = id to sensorProfile
                runOnUiThread { activityPermissionLauncher.launch(Manifest.permission.ACTIVITY_RECOGNITION) }
                return@runCatching JSONObject()
                    .put("active", false)
                    .put("permissionRequired", "activity_recognition")
                    .put("sessionId", id)
                    .put("profile", sensorProfile.wireName)
                    .toString()
            }
            startWorkoutTracking(id, sensorProfile)
            JSONObject().put("active", true).put("sessionId", id).put("profile", sensorProfile.wireName).toString()
        }.getOrElse { JSONObject().put("active", false).put("error", it.message ?: it.javaClass.simpleName).toString() }

        @JavascriptInterface
        fun motionSnapshot(): String = ActivityTrackingService.workoutSnapshot()?.let(::motionEvidenceJson)?.toString()
            ?: JSONObject().put("available", false).toString()

        @JavascriptInterface
        fun endMotionSession(): String {
            val evidence = ActivityTrackingService.finishWorkout()
            if (evidence != null) lastEndedMotionEvidence = evidence
            if (!ActivityTrackingService.hasActiveTracking()) motionEngine.onHostResume()
            return evidence?.let(::motionEvidenceJson)?.toString()
                ?: JSONObject().put("available", false).toString()
        }

        @JavascriptInterface
        fun beginActivitySession(mode: String?, weightKg: Double): String = runCatching {
            val parsedMode = requireNotNull(ActivityMode.fromWire(mode)) { "unsupported activity mode" }
            val live = ActivityTrackingService.activitySnapshot()
            if (live.active) {
                return@runCatching activitySnapshotJson(live).put("resumed", true).toString()
            }
            val safeWeight = weightKg.coerceIn(30.0, 250.0)
            if (!hasLocationPermission()) {
                pendingActivityStart = parsedMode to safeWeight
                runOnUiThread { locationPermissionLauncher.launch(arrayOf(Manifest.permission.ACCESS_COARSE_LOCATION, Manifest.permission.ACCESS_FINE_LOCATION)) }
                return@runCatching JSONObject().put("active", false).put("permissionRequired", "location").put("mode", parsedMode.wireName).toString()
            }
            if (parsedMode.usesSteps && !hasActivityPermission() && Build.VERSION.SDK_INT >= 29) {
                pendingActivityStart = parsedMode to safeWeight
                runOnUiThread { activityPermissionLauncher.launch(Manifest.permission.ACTIVITY_RECOGNITION) }
                return@runCatching JSONObject().put("active", false).put("permissionRequired", "activity_recognition").put("mode", parsedMode.wireName).toString()
            }
            startActivityTracking(parsedMode, safeWeight)
            JSONObject().put("active", true).put("mode", parsedMode.wireName).toString()
        }.getOrElse { JSONObject().put("active", false).put("error", it.message ?: it.javaClass.simpleName).toString() }

        @JavascriptInterface
        fun pauseActivitySession(): String {
            ActivityTrackingService.pauseActivity()
            return activitySnapshotJson(ActivityTrackingService.activitySnapshot()).toString()
        }

        @JavascriptInterface
        fun resumeActivitySession(): String {
            ActivityTrackingService.resumeActivity()
            return activitySnapshotJson(ActivityTrackingService.activitySnapshot()).toString()
        }

        @JavascriptInterface
        fun takePendingFinishedActivitySnapshot(): String = ActivityTrackingService.takePendingFinishedActivitySnapshot(this@MainActivity)

        @JavascriptInterface
        fun activitySnapshot(): String = activitySnapshotJson(ActivityTrackingService.activitySnapshot()).toString()

        @JavascriptInterface
        fun endActivitySession(): String {
            val snapshot = ActivityTrackingService.finishActivity()
            if (!ActivityTrackingService.hasActiveTracking()) motionEngine.onHostResume()
            return activitySnapshotJson(snapshot).toString()
        }

        @JavascriptInterface
        fun beginStepSession() {
            beginMotionSession("legacy-${System.currentTimeMillis()}", MotionSensorProfile.STEP_DRILL.wireName)
        }

        @JavascriptInterface
        fun sessionSteps(): Int = ActivityTrackingService.workoutSnapshot()?.stepDelta ?: 0

        @JavascriptInterface
        fun speak(text: String?, languageTag: String?, append: Boolean) {
            if (text.isNullOrBlank()) return
            runOnUiThread {
                val locale = if (languageTag.orEmpty().lowercase().startsWith("ar")) Locale("ar", "EG") else Locale.US
                tts?.language = locale
                tts?.speak(text, if (append) TextToSpeech.QUEUE_ADD else TextToSpeech.QUEUE_FLUSH, null, "thf-fitness-v2")
            }
        }

        @JavascriptInterface
        fun saveSummary(json: String?): String = runCatching {
            require(json != null && json.toByteArray(Charsets.UTF_8).size <= MAX_SUMMARY_BYTES) {
                "invalid workout summary size"
            }
            val item = JSONObject(json)
            item.remove("motionEvidence")
            item.remove("verification")
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
            if (ActivityTrackingService.workoutSnapshot()?.sessionId?.startsWith("legacy-") == true) {
                lastEndedMotionEvidence = ActivityTrackingService.finishWorkout()
            }
            val nativeEvidence = lastEndedMotionEvidence?.takeIf { it.sessionId == clientId }
            if (nativeEvidence != null) {
                item.put("motionEvidence", motionEvidenceJson(nativeEvidence))
                item.put("measurementSource", "SENSOR")
            } else {
                item.put("measurementSource", "MANUAL_OR_UNVERIFIED")
            }
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
