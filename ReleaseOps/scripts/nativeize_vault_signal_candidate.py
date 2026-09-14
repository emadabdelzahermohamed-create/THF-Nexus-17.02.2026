#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

if len(sys.argv) != 4:
    raise SystemExit("usage: nativeize_vault_signal_candidate.py <project> <app> <package>")
project = Path(sys.argv[1]).resolve()
app = sys.argv[2].strip().lower()
pkg = sys.argv[3].strip()
if app not in {"vault", "signal"}:
    raise SystemExit("app must be vault or signal")
main = project / "app" / "src" / "main"
if not main.is_dir():
    raise SystemExit(f"missing {main}")

# Derived build overlay only. The authoritative source ZIP is never modified.
for child in (main / "java", main / "kotlin"):
    if child.exists():
        shutil.rmtree(child)
java_dir = main / "java" / Path(*pkg.split("."))
java_dir.mkdir(parents=True, exist_ok=True)

label = "THF Vault" if app == "vault" else "THF Signal"
hint = "Private local vault note" if app == "vault" else "Local signal draft"
manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <application android:allowBackup="false" android:label="{label}" android:supportsRtl="true" android:usesCleartextTraffic="false">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
'''
(main / "AndroidManifest.xml").write_text(manifest, encoding="utf-8")

java = r'''package __PKG__;

import android.Manifest;
import android.app.Activity;
import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Bundle;
import android.provider.Settings;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.net.ssl.HttpsURLConnection;
import android.util.Base64;

public final class MainActivity extends Activity {
    private static final String STORE = "thf_local_secure_store";
    private static final String KEY = "payload";
    private static final String ALIAS = "thf.__APP__.local.v1";
    private TextView status;
    private EditText input;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(20), dp(20), dp(32));
        root.setLayoutDirection(View.LAYOUT_DIRECTION_LOCALE);
        scroll.addView(root);

        TextView title = text("__LABEL__", 26);
        title.setContentDescription("__LABEL__ screen");
        root.addView(title);
        root.addView(text("Native QA surface. Local actions are genuinely on-device. Remote state is never fabricated.", 15));

        status = text("Ready", 15);
        status.setContentDescription("Current status");
        root.addView(status);

        input = new EditText(this);
        input.setHint("__HINT__");
        input.setContentDescription("__HINT__ input");
        input.setMinHeight(dp(56));
        root.addView(input);

        root.addView(button("Save securely on this device", v -> saveLocal()));
        root.addView(button("Load local value", v -> loadLocal()));
        root.addView(button("Clear local value", v -> clearLocal()));
        root.addView(button("Check THF backend health", v -> checkBackend()));
        root.addView(button("Network and Data Saver status", v -> networkStatus()));
        root.addView(button("Notification permission", v -> notificationPermission()));
        root.addView(button("Open THF Pass", v -> openPass()));
        root.addView(button("Open app settings", v -> openSettings()));
        setContentView(scroll);
    }

    private TextView text(String value, int sp) {
        TextView t = new TextView(this); t.setText(value); t.setTextSize(sp); t.setPadding(0, dp(8), 0, dp(8)); return t;
    }
    private Button button(String label, View.OnClickListener l) {
        Button b = new Button(this); b.setText(label); b.setContentDescription(label); b.setMinHeight(dp(48)); b.setOnClickListener(l); return b;
    }
    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
    private void say(String s) { runOnUiThread(() -> status.setText(s)); }

    private SecretKey key() throws Exception {
        KeyStore ks = KeyStore.getInstance("AndroidKeyStore"); ks.load(null);
        if (ks.containsAlias(ALIAS)) return ((KeyStore.SecretKeyEntry) ks.getEntry(ALIAS, null)).getSecretKey();
        KeyGenerator kg = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        kg.init(new KeyGenParameterSpec.Builder(ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
        return kg.generateKey();
    }
    private void saveLocal() {
        try {
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(Cipher.ENCRYPT_MODE, key());
            byte[] cipher = c.doFinal(input.getText().toString().getBytes(StandardCharsets.UTF_8));
            String packed = Base64.encodeToString(c.getIV(), Base64.NO_WRAP) + "." + Base64.encodeToString(cipher, Base64.NO_WRAP);
            getSharedPreferences(STORE, MODE_PRIVATE).edit().putString(KEY, packed).apply();
            say("Saved locally with Android Keystore encryption. No remote/economy/social state changed.");
        } catch (Exception e) { say("Secure local save failed: " + e.getClass().getSimpleName()); }
    }
    private void loadLocal() {
        try {
            String packed = getSharedPreferences(STORE, MODE_PRIVATE).getString(KEY, null);
            if (packed == null) { say("No local value saved."); return; }
            String[] p = packed.split("\\.", 2); if (p.length != 2) throw new IllegalStateException("bad payload");
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
            c.init(Cipher.DECRYPT_MODE, key(), new GCMParameterSpec(128, Base64.decode(p[0], Base64.NO_WRAP)));
            input.setText(new String(c.doFinal(Base64.decode(p[1], Base64.NO_WRAP)), StandardCharsets.UTF_8));
            say("Loaded genuine local value.");
        } catch (Exception e) { say("Secure local load failed: " + e.getClass().getSimpleName()); }
    }
    private void clearLocal() {
        getSharedPreferences(STORE, MODE_PRIVATE).edit().remove(KEY).apply(); input.setText(""); say("Local value cleared.");
    }

    private String configuredBaseUrl() {
        for (String name : new String[]{"API_BASE_URL", "BASE_URL", "API_URL"}) {
            try {
                Field f = BuildConfig.class.getField(name); Object v = f.get(null);
                if (v instanceof String) {
                    String s = ((String)v).trim();
                    if (s.startsWith("https://") && !s.contains("example.") && !s.contains("localhost") && !s.contains("127.0.0.1")) return s;
                }
            } catch (Exception ignored) { }
        }
        return null;
    }
    private void checkBackend() {
        final String base = configuredBaseUrl();
        if (base == null) { say("THF backend NOT PROVEN: no trusted HTTPS endpoint configured in this candidate."); return; }
        say("Checking reachable HTTPS health endpoint…");
        new Thread(() -> {
            HttpsURLConnection c = null;
            try {
                String health = base.endsWith("/") ? base + "health" : base + "/health";
                c = (HttpsURLConnection)new URL(health).openConnection(); c.setConnectTimeout(7000); c.setReadTimeout(7000); c.setRequestMethod("GET");
                int code = c.getResponseCode();
                if (code >= 200 && code < 300) say("THF backend health reachable over HTTPS (HTTP " + code + "). Auth/session proof is still separate.");
                else say("THF backend health not ready (HTTP " + code + ").");
            } catch (Exception e) { say("THF backend health unreachable: " + e.getClass().getSimpleName()); }
            finally { if (c != null) c.disconnect(); }
        }).start();
    }
    private void networkStatus() {
        ConnectivityManager cm = (ConnectivityManager)getSystemService(CONNECTIVITY_SERVICE);
        Network n = cm.getActiveNetwork(); NetworkCapabilities caps = n == null ? null : cm.getNetworkCapabilities(n);
        boolean validated = caps != null && caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED);
        boolean metered = cm.isActiveNetworkMetered();
        int bg = cm.getRestrictBackgroundStatus();
        say("network_validated=" + validated + " metered=" + metered + " data_saver_status=" + bg + ". Remote actions remain fail-closed when backend/auth is unproven.");
    }
    private void notificationPermission() {
        if (android.os.Build.VERSION.SDK_INT < 33 || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
            say("Notification permission is granted or not runtime-gated on this Android version."); return;
        }
        requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 5001);
    }
    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(requestCode, permissions, results);
        if (requestCode == 5001) say(results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED ? "Notification permission granted." : "Notification permission not granted.");
    }
    private void openPass() {
        Intent i = getPackageManager().getLaunchIntentForPackage("com.topherofit.thf.pass");
        if (i == null) { say("THF Pass is not installed/resolvable on this device; no fake handoff performed."); return; }
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); startActivity(i); say("Opened installed THF Pass.");
    }
    private void openSettings() {
        Intent i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, android.net.Uri.parse("package:" + getPackageName())); startActivity(i);
    }
}
'''.replace("__PKG__", pkg).replace("__APP__", app).replace("__LABEL__", label).replace("__HINT__", hint)
(java_dir / "MainActivity.java").write_text(java, encoding="utf-8")
print(f"native_overlay=THF_NATIVE_REAL_FUNCTION_V1 app={app} package={pkg} manifest={main/'AndroidManifest.xml'} java={java_dir/'MainActivity.java'}")
