package com.topherofit.thf.pulse

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.SystemClock
import com.google.android.gms.common.ConnectionResult
import com.google.android.gms.common.GoogleApiAvailability
import com.google.android.gms.location.Granularity
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import kotlin.math.max

/**
 * Owns any live tracking session so collection is independent from MainActivity/WebView lifecycle.
 * A foreground notification is deliberately required: if the UI goes to the background, the user
 * can still see that GPS/motion collection is active and can stop it from the notification.
 */
class ActivityTrackingService : Service(), LocationListener, SensorEventListener {
    companion object {
        const val ACTION_START_ACTIVITY = "com.topherofit.thf.pulse.START_ACTIVITY"
        const val ACTION_START_WORKOUT = "com.topherofit.thf.pulse.START_WORKOUT"
        const val ACTION_STOP_TRACKING = "com.topherofit.thf.pulse.STOP_TRACKING"
        const val EXTRA_MODE = "mode"
        const val EXTRA_WEIGHT_KG = "weight_kg"
        const val EXTRA_SESSION_ID = "session_id"
        const val EXTRA_SENSOR_PROFILE = "sensor_profile"

        private const val CHANNEL_ID = "thf_live_tracking"
        private const val NOTIFICATION_ID = 51009
        private const val MAX_ROUTE_POINTS = 1200
        private const val ACTIVITY_CHECKPOINT_PREFS = "thf_activity_tracking"
        private const val ACTIVITY_CHECKPOINT_KEY = "active_activity_checkpoint"
        private const val ACTIVITY_CHECKPOINT_INTERVAL_MS = 10_000L

        @Volatile private var instance: ActivityTrackingService? = null
        @Volatile private var lastActivitySnapshot = ActivitySnapshot(
            active = false,
            phase = ActivitySessionPhase.ARMED,
            mode = null,
            startedAtWallMs = 0L,
            elapsedMs = 0L,
            distanceMetres = 0.0,
            stepDelta = 0,
            currentSpeedKph = 0.0,
            averageSpeedKph = 0.0,
            paceMinutesPerKm = null,
            estimatedCaloriesKcal = 0.0,
            gpsPointCount = 0,
            lastAccuracyMetres = null,
            route = emptyList(),
        )
        @Volatile private var lastWorkoutEvidence: MotionEvidence? = null

        fun hasActiveTracking(): Boolean = instance?.hasLiveSession() == true
        fun activitySnapshot(): ActivitySnapshot = instance?.buildActivitySnapshot(active = true) ?: lastActivitySnapshot
        fun workoutSnapshot(): MotionEvidence? = instance?.workoutEngine?.snapshot() ?: lastWorkoutEvidence

        fun startActivity(context: Context, mode: ActivityMode, weightKg: Double) {
            val intent = Intent(context, ActivityTrackingService::class.java)
                .setAction(ACTION_START_ACTIVITY)
                .putExtra(EXTRA_MODE, mode.wireName)
                .putExtra(EXTRA_WEIGHT_KG, weightKg)
            startForegroundCompat(context, intent)
        }

        fun startWorkout(context: Context, sessionId: String, profile: MotionSensorProfile) {
            val intent = Intent(context, ActivityTrackingService::class.java)
                .setAction(ACTION_START_WORKOUT)
                .putExtra(EXTRA_SESSION_ID, sessionId)
                .putExtra(EXTRA_SENSOR_PROFILE, profile.wireName)
            startForegroundCompat(context, intent)
        }

        fun finishActivity(): ActivitySnapshot {
            val service = instance ?: return lastActivitySnapshot
            return service.finishActivityInternal()
        }

        fun finishWorkout(): MotionEvidence? {
            val service = instance ?: return lastWorkoutEvidence
            return service.finishWorkoutInternal()
        }

        private fun startForegroundCompat(context: Context, intent: Intent) {
            if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(intent) else context.startService(intent)
        }
    }

    private lateinit var notificationManager: NotificationManager
    private lateinit var locationManager: LocationManager
    private lateinit var fusedLocationClient: com.google.android.gms.location.FusedLocationProviderClient
    private lateinit var sensorManager: SensorManager
    private var stepCounter: Sensor? = null

    private var activityMode: ActivityMode? = null
    private var activityWeightKg = 70.0
    private var activityStartedAtWallMs = 0L
    private var activityStartedAtElapsedMs = 0L
    private var activityPhase = ActivitySessionPhase.ARMED
    private var activityActivatedAtWallMs: Long? = null
    private var activityActivatedAtElapsedMs: Long? = null
    private var activityDistanceMetres = 0.0
    private var activityStepBaseline: Float? = null
    private var activityStepDelta = 0
    private var currentSpeedKph = 0.0
    private var lastLocation: Location? = null
    private var lastObservedLocation: Location? = null
    private var lastAccuracyMetres: Float? = null
    private var lastObservedAccuracyMetres: Float? = null
    private val route = mutableListOf<ActivityRoutePoint>()
    private var sessionStartedAtWallMs = 0L
    private var lastActivityCheckpointWriteElapsedMs = 0L
    private val notificationHandler = Handler(Looper.getMainLooper())
    private val fusedLocationCallback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            result.locations.forEach(::onLocationChanged)
        }
    }
    private val notificationTicker = object : Runnable {
        override fun run() {
            if (!hasLiveSession()) return
            notificationManager.notify(NOTIFICATION_ID, buildNotification())
            notificationHandler.postDelayed(this, 5_000L)
        }
    }

    private fun startNotificationUpdates() {
        notificationHandler.removeCallbacks(notificationTicker)
        notificationHandler.postDelayed(notificationTicker, 5_000L)
    }

    internal var workoutEngine: MotionSessionEngine? = null
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        notificationManager = getSystemService(NotificationManager::class.java)
        locationManager = getSystemService(LocationManager::class.java)
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
        sensorManager = getSystemService(SensorManager::class.java)
        stepCounter = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent == null) {
            if (restorePersistedActivity()) return START_STICKY
            stopSelf(startId)
            return START_NOT_STICKY
        }
        when (intent.action) {
            ACTION_START_ACTIVITY -> {
                val mode = ActivityMode.fromWire(intent.getStringExtra(EXTRA_MODE)) ?: return START_NOT_STICKY
                startActivityInternal(mode, intent.getDoubleExtra(EXTRA_WEIGHT_KG, 70.0))
            }
            ACTION_START_WORKOUT -> {
                val sessionId = intent.getStringExtra(EXTRA_SESSION_ID).orEmpty().trim()
                if (sessionId.isNotEmpty()) {
                    startWorkoutInternal(sessionId, MotionSensorProfile.fromWire(intent.getStringExtra(EXTRA_SENSOR_PROFILE)))
                }
            }
            ACTION_STOP_TRACKING -> stopCurrentSession()
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onTaskRemoved(rootIntent: Intent?) {
        // Deliberately keep the foreground session alive when the task UI is swiped away.
        // The visible notification remains the user's stop/control surface.
        saveActivityCheckpoint(force = true)
        super.onTaskRemoved(rootIntent)
    }

    override fun onDestroy() {
        if (activityMode != null) saveActivityCheckpoint(force = true)
        notificationHandler.removeCallbacks(notificationTicker)
        unregisterActivitySources()
        workoutEngine?.let { engine ->
            lastWorkoutEvidence = runCatching { engine.stopSession() }.getOrNull() ?: lastWorkoutEvidence
            engine.onHostPause()
        }
        workoutEngine = null
        if (instance === this) instance = null
        super.onDestroy()
    }

    private fun hasLiveSession(): Boolean = activityMode != null || workoutEngine?.currentState()?.active == true

    private fun startActivityInternal(mode: ActivityMode, weightKg: Double) {
        if (!ActivitySessionStartPolicy.shouldStart(activityMode, mode)) {
            publishActivitySnapshot()
            return
        }
        stopCurrentSession(keepService = true)
        activityMode = mode
        activityWeightKg = weightKg.coerceIn(30.0, 250.0)
        activityStartedAtWallMs = System.currentTimeMillis()
        sessionStartedAtWallMs = activityStartedAtWallMs
        activityStartedAtElapsedMs = SystemClock.elapsedRealtime()
        activityPhase = ActivitySessionPhase.ARMED
        activityActivatedAtWallMs = null
        activityActivatedAtElapsedMs = null
        activityDistanceMetres = 0.0
        activityStepBaseline = null
        activityStepDelta = 0
        currentSpeedKph = 0.0
        lastLocation = null
        lastObservedLocation = null
        lastAccuracyMetres = null
        lastObservedAccuracyMetres = null
        route.clear()
        startForegroundForCurrentSession(buildNotification())
        registerActivitySources(mode)
        publishActivitySnapshot()
        saveActivityCheckpoint(force = true)
        startNotificationUpdates()
    }

    private fun startWorkoutInternal(sessionId: String, profile: MotionSensorProfile) {
        if (workoutEngine?.currentState()?.sessionId == sessionId) return
        stopCurrentSession(keepService = true)
        val engine = MotionSessionEngine(AndroidMotionSensorGateway(this))
        engine.onHostResume()
        engine.startSession(sessionId, profile)
        workoutEngine = engine
        sessionStartedAtWallMs = System.currentTimeMillis()
        startForegroundForCurrentSession(buildNotification())
        startNotificationUpdates()
    }

    private fun registerActivitySources(mode: ActivityMode) {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
        ) {
            registerStepSource(mode)
            return
        }

        registerStepSource(mode)
        val request = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 1_000L)
            .setMinUpdateIntervalMillis(1_000L)
            .setMinUpdateDistanceMeters(1f)
            .setMaxUpdateDelayMillis(2_000L)
            .setGranularity(Granularity.GRANULARITY_FINE)
            .setWaitForAccurateLocation(false)
            .build()
        val playServicesReady = GoogleApiAvailability.getInstance()
            .isGooglePlayServicesAvailable(this) == ConnectionResult.SUCCESS
        if (playServicesReady) {
            runCatching {
                fusedLocationClient.requestLocationUpdates(request, fusedLocationCallback, Looper.getMainLooper())
                    .addOnFailureListener { registerLegacyLocationProviders(mode) }
            }.onFailure { registerLegacyLocationProviders(mode) }
        } else {
            registerLegacyLocationProviders(mode)
        }
    }

    private fun registerLegacyLocationProviders(mode: ActivityMode) {
        if (activityMode != mode) return
        if (!hasLocationPermission()) return
        runCatching {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1_000L, 1f, this, Looper.getMainLooper())
            }
        }
        runCatching {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2_500L, 4f, this, Looper.getMainLooper())
            }
        }
    }

    private fun registerStepSource(mode: ActivityMode) {
        if (mode.usesSteps && hasActivityRecognitionPermission()) {
            stepCounter?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
        }
    }

    private fun unregisterActivitySources() {
        runCatching { fusedLocationClient.removeLocationUpdates(fusedLocationCallback) }
        runCatching { locationManager.removeUpdates(this) }
        runCatching { sensorManager.unregisterListener(this) }
    }

    override fun onLocationChanged(location: Location) {
        val mode = activityMode ?: return
        val nowElapsed = SystemClock.elapsedRealtime()
        val previous = lastLocation
        val observedFix = location.toGpsFix()
        if (observedFix.latitude.isFinite() && observedFix.latitude in -90.0..90.0 &&
            observedFix.longitude.isFinite() && observedFix.longitude in -180.0..180.0 &&
            observedFix.accuracyMetres.isFinite() && observedFix.accuracyMetres > 0.0
        ) {
            lastObservedLocation = Location(location)
            lastObservedAccuracyMetres = location.accuracy
        }
        // Keep weak/stale fixes visible for signal UX, but never let them poison distance/route.
        if (!GpsFixGate.accepts(observedFix, previous?.toGpsFix(), mode, activityStartedAtElapsedMs, nowElapsed)) {
            publishActivitySnapshot()
            return
        }
        if (previous != null) {
            val deltaMetres = ActivityMetrics.distanceMetres(previous.latitude, previous.longitude, location.latitude, location.longitude)
            val deltaMs = location.elapsedRealtimeNanos / 1_000_000L - previous.elapsedRealtimeNanos / 1_000_000L
            val impliedKph = ActivityMetrics.averageSpeedKph(deltaMetres, deltaMs)
            if (deltaMetres >= 1.0) {
                activityDistanceMetres += deltaMetres
                currentSpeedKph = if (location.hasSpeed()) location.speed * 3.6 else impliedKph
            } else if (deltaMetres < 1.0) {
                currentSpeedKph = 0.0
            }
        }
        lastLocation = Location(location)
        lastAccuracyMetres = location.accuracy
        if (route.size >= MAX_ROUTE_POINTS) route.removeAt(0)
        route += ActivityRoutePoint(
            latitude = location.latitude,
            longitude = location.longitude,
            altitudeMetres = if (location.hasAltitude()) location.altitude else null,
            accuracyMetres = location.accuracy,
            elapsedMs = nowElapsed - activityStartedAtElapsedMs,
        )
        maybeActivateActivity(nowElapsed)
        publishActivitySnapshot()
        saveActivityCheckpoint()
    }

    @Suppress("DEPRECATION")
    private fun Location.toGpsFix() = GpsFix(
        latitude = latitude,
        longitude = longitude,
        accuracyMetres = if (hasAccuracy()) accuracy.toDouble() else Double.NaN,
        elapsedMs = elapsedRealtimeNanos / 1_000_000L,
        mock = if (Build.VERSION.SDK_INT >= 31) isMock else isFromMockProvider,
        speedMps = if (hasSpeed()) speed.toDouble() else null,
    )

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != Sensor.TYPE_STEP_COUNTER || activityMode?.usesSteps != true) return
        val raw = event.values.firstOrNull() ?: return
        if (!raw.isFinite() || raw < 0f) return
        val baseline = activityStepBaseline
        if (baseline == null || raw < baseline) {
            activityStepBaseline = raw
            activityStepDelta = 0
        } else {
            activityStepDelta = max(0, (raw - baseline).toInt())
        }
        maybeActivateActivity(SystemClock.elapsedRealtime())
        publishActivitySnapshot()
        saveActivityCheckpoint()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    private fun maybeActivateActivity(nowElapsed: Long) {
        val mode = activityMode ?: return
        if (activityPhase == ActivitySessionPhase.ACTIVE) return
        if (!ActivityActivationGate.shouldActivate(mode, activityDistanceMetres, activityStepDelta, route.size)) return
        activityPhase = ActivitySessionPhase.ACTIVE
        activityActivatedAtWallMs = System.currentTimeMillis()
        activityActivatedAtElapsedMs = nowElapsed
        saveActivityCheckpoint(force = true)
    }

    private fun buildActivitySnapshot(active: Boolean): ActivitySnapshot {
        val mode = activityMode ?: return lastActivitySnapshot
        return ActivitySnapshotPolicy.build(
            sessionActive = active,
            phase = activityPhase,
            mode = mode,
            armedStartedAtWallMs = activityStartedAtWallMs,
            activatedAtWallMs = activityActivatedAtWallMs,
            activatedAtElapsedMs = activityActivatedAtElapsedMs,
            nowElapsedMs = SystemClock.elapsedRealtime(),
            measuredDistanceMetres = activityDistanceMetres,
            measuredStepDelta = activityStepDelta,
            currentSpeedKph = currentSpeedKph,
            weightKg = activityWeightKg,
            acceptedRoute = route.toList(),
            lastAccuracyMetres = lastAccuracyMetres,
        ).copy(
            gpsFixState = gpsFixState(),
            observedAccuracyMetres = lastObservedAccuracyMetres,
        )
    }

    private fun publishActivitySnapshot() {
        if (activityMode != null) lastActivitySnapshot = buildActivitySnapshot(active = true)
    }

    private fun finishActivityInternal(): ActivitySnapshot {
        if (activityMode == null) return lastActivitySnapshot
        val final = buildActivitySnapshot(active = false)
        lastActivitySnapshot = final
        unregisterActivitySources()
        clearActivityCheckpoint()
        activityMode = null
        notificationHandler.removeCallbacks(notificationTicker)
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        return final
    }

    private fun finishWorkoutInternal(): MotionEvidence? {
        val engine = workoutEngine ?: return lastWorkoutEvidence
        val evidence = engine.stopSession()
        engine.onHostPause()
        workoutEngine = null
        if (evidence != null) lastWorkoutEvidence = evidence
        notificationHandler.removeCallbacks(notificationTicker)
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        return evidence
    }

    private fun stopCurrentSession(keepService: Boolean = false) {
        if (activityMode != null) {
            lastActivitySnapshot = buildActivitySnapshot(active = false)
            unregisterActivitySources()
            clearActivityCheckpoint()
            activityMode = null
        }
        workoutEngine?.let { engine ->
            lastWorkoutEvidence = engine.stopSession() ?: lastWorkoutEvidence
            engine.onHostPause()
        }
        workoutEngine = null
        if (!keepService) {
            notificationHandler.removeCallbacks(notificationTicker)
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }

    private fun saveActivityCheckpoint(force: Boolean = false) {
        val mode = activityMode ?: return
        val nowElapsed = SystemClock.elapsedRealtime()
        if (!force && nowElapsed - lastActivityCheckpointWriteElapsedMs < ACTIVITY_CHECKPOINT_INTERVAL_MS) return
        val checkpoint = ActivitySessionCheckpoint(
            mode = mode,
            weightKg = activityWeightKg,
            startedAtWallMs = activityStartedAtWallMs,
            startedAtElapsedMs = activityStartedAtElapsedMs,
            savedAtElapsedMs = nowElapsed,
            distanceMetres = activityDistanceMetres,
            stepBaseline = activityStepBaseline,
            stepDelta = activityStepDelta,
            lastAccuracyMetres = lastAccuracyMetres,
            route = route.toList(),
            phase = activityPhase,
            activatedAtWallMs = activityActivatedAtWallMs,
            activatedAtElapsedMs = activityActivatedAtElapsedMs,
        )
        getSharedPreferences(ACTIVITY_CHECKPOINT_PREFS, MODE_PRIVATE)
            .edit()
            .putString(ACTIVITY_CHECKPOINT_KEY, ActivitySessionCheckpointCodec.encode(checkpoint))
            .apply()
        lastActivityCheckpointWriteElapsedMs = nowElapsed
    }

    private fun clearActivityCheckpoint() {
        getSharedPreferences(ACTIVITY_CHECKPOINT_PREFS, MODE_PRIVATE)
            .edit()
            .remove(ACTIVITY_CHECKPOINT_KEY)
            .apply()
        lastActivityCheckpointWriteElapsedMs = 0L
    }

    private fun restorePersistedActivity(): Boolean {
        val raw = getSharedPreferences(ACTIVITY_CHECKPOINT_PREFS, MODE_PRIVATE)
            .getString(ACTIVITY_CHECKPOINT_KEY, null)
        val checkpoint = ActivitySessionCheckpointCodec.decode(raw)
        val nowElapsed = SystemClock.elapsedRealtime()
        if (checkpoint == null || !ActivitySessionCheckpointCodec.canRestore(checkpoint, nowElapsed)) {
            clearActivityCheckpoint()
            return false
        }

        activityMode = checkpoint.mode
        activityWeightKg = checkpoint.weightKg
        activityStartedAtWallMs = checkpoint.startedAtWallMs
        sessionStartedAtWallMs = checkpoint.startedAtWallMs
        activityStartedAtElapsedMs = ActivitySessionCheckpointCodec.adjustedStartedAtElapsedMs(checkpoint, nowElapsed)
        activityPhase = checkpoint.phase
        activityActivatedAtWallMs = checkpoint.activatedAtWallMs
        activityActivatedAtElapsedMs = ActivitySessionCheckpointCodec.adjustedActivatedAtElapsedMs(checkpoint, nowElapsed)
        activityDistanceMetres = checkpoint.distanceMetres
        activityStepBaseline = checkpoint.stepBaseline
        activityStepDelta = checkpoint.stepDelta
        currentSpeedKph = 0.0
        lastAccuracyMetres = checkpoint.lastAccuracyMetres
        route.clear()
        route += checkpoint.route.takeLast(MAX_ROUTE_POINTS)
        lastLocation = checkpoint.route.lastOrNull()?.let { point ->
            Location("thf_checkpoint").apply {
                latitude = point.latitude
                longitude = point.longitude
                point.altitudeMetres?.let { altitude = it }
                accuracy = point.accuracyMetres
                elapsedRealtimeNanos = (activityStartedAtElapsedMs + point.elapsedMs) * 1_000_000L
            }
        }
        lastActivityCheckpointWriteElapsedMs = nowElapsed
        startForegroundForCurrentSession(buildNotification())
        registerActivitySources(checkpoint.mode)
        publishActivitySnapshot()
        startNotificationUpdates()
        return true
    }

    private fun buildNotification(): Notification {
        val launchIntent = packageManager.getLaunchIntentForPackage(packageName)?.apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentIntent = launchIntent?.let {
            PendingIntent.getActivity(this, 51009, it, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        }
        val stopIntent = PendingIntent.getService(
            this,
            51010,
            Intent(this, ActivityTrackingService::class.java).setAction(ACTION_STOP_TRACKING),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val snapshot = if (activityMode != null) buildActivitySnapshot(active = true) else null
        val title = when (activityMode) {
            ActivityMode.WALK -> "Top Hero Fit · المشي مستمر"
            ActivityMode.RUN -> "Top Hero Fit · الجري مستمر"
            ActivityMode.CYCLE -> "Top Hero Fit · ركوب الدراجة مستمر"
            null -> "Top Hero Fit · التمرين مستمر"
        }
        val state = workoutEngine?.currentState()
        val evidence = workoutEngine?.snapshot()
        val profile = state?.profile
        val stepAvailable = if (state != null && profile?.showStepMetrics == true) {
            val caps = state.capabilities
            caps.activityRecognitionPermission && (caps.stepCounter || caps.stepDetector)
        } else null
        val content = if (snapshot != null) {
            LiveNotificationText.activity(snapshot, stepCounter != null && hasActivityRecognitionPermission(), gpsStatus())
        } else {
            val profileName = when (profile) {
                MotionSensorProfile.STEP_DRILL -> "تمرين خطوات"
                MotionSensorProfile.IMPACT_JUMP -> "تمرين قفز"
                MotionSensorProfile.STATIC_HOLD -> "تمرين ثبات"
                else -> "تمرين حركة"
            }
            // Counter and detector observe the same steps; never add them together.
            val measuredSteps = evidence?.let { max(it.stepDelta, it.stepDetectorCount) }
            LiveNotificationText.workout(measuredSteps, profileName, stepAvailable)
        }
        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setContentTitle(title)
            .setContentText(content.compact)
            .setStyle(Notification.BigTextStyle().bigText(content.expanded))
            .setWhen(sessionStartedAtWallMs)
            .setShowWhen(true)
            .setUsesChronometer(true)
            .setVisibility(Notification.VISIBILITY_PRIVATE)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(Notification.CATEGORY_SERVICE)
            .setContentIntent(contentIntent)
            .addAction(Notification.Action.Builder(null, "إيقاف", stopIntent).build())
            .build()
    }

    private fun startForegroundForCurrentSession(notification: Notification) {
        if (Build.VERSION.SDK_INT >= 29) {
            val type = when {
                activityMode != null -> ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
                Build.VERSION.SDK_INT >= 34 -> ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH
                else -> ServiceInfo.FOREGROUND_SERVICE_TYPE_NONE
            }
            startForeground(NOTIFICATION_ID, notification, type)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "تتبع النشاط والتمرين",
            NotificationManager.IMPORTANCE_LOW,
        ).apply {
            description = "إشعار دائم أثناء قياس نشاط أو تمرين في الخلفية"
            setShowBadge(false)
        }
        notificationManager.createNotificationChannel(channel)
    }

    private fun hasActivityRecognitionPermission(): Boolean =
        Build.VERSION.SDK_INT < 29 || checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED

    private fun hasLocationPermission(): Boolean =
        checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED

    private fun gpsFixState(): String {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
        ) return "permission"
        val enabled = runCatching {
            locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
        }.getOrDefault(false)
        if (!enabled) return "off"
        val observed = lastObservedLocation ?: return "acquiring"
        val ageMs = SystemClock.elapsedRealtime() - observed.elapsedRealtimeNanos / 1_000_000L
        if (ageMs > 30_000L) return "stale"
        val accepted = lastLocation
        if (accepted == null || accepted.elapsedRealtimeNanos < observed.elapsedRealtimeNanos) return "weak"
        return "ready"
    }

    private fun gpsStatus(): String = when (gpsFixState()) {
        "permission" -> "إذن الموقع غير متاح · المسافة لا تتحدث"
        "off" -> "الموقع مغلق · المسافة لا تتحدث"
        "stale" -> "إشارة الموقع متوقفة · بانتظار تحديث"
        "weak" -> "تم تحديد الموقع · الدقة ضعيفة ±${lastObservedAccuracyMetres?.toInt() ?: 0} م"
        "ready" -> "GPS متصل · دقة ±${lastAccuracyMetres?.toInt() ?: 0} م"
        else -> "جارٍ تثبيت موقع عالي الدقة"
    }
}
