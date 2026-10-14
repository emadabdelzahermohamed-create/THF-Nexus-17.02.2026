package com.topherofit.rescue;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.VideoView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Enumeration;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MainActivity extends Activity {
    private static final int PICK_VIDEO = 701;
    private static final int BG = Color.rgb(15, 24, 32);
    private static final int CARD = Color.rgb(28, 41, 52);
    private static final int TEXT = Color.WHITE;
    private static final int MUTED = Color.rgb(190, 204, 214);

    private final Handler handler = new Handler(Looper.getMainLooper());
    private VideoView waveVideo;
    private ServerSocket lanServer;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        String key = BuildConfig.PRODUCT_KEY;
        if ("hub".equals(key)) showHub();
        else if ("fitness".equals(key)) showFitness();
        else if ("wave".equals(key)) showWave();
        else if ("arena".equals(key)) showArena();
        else if ("publisher".equals(key)) showPublisher();
        else if ("vault".equals(key)) showVault();
        else if ("tokenops".equals(key)) showTokenOps();
        else if ("ruinsciv".equals(key)) showRuinsCiv();
        else if ("endciv".equals(key)) showEndCiv();
        else showFatal("Unsupported product: " + key);
    }

    private LinearLayout page(String title, String subtitle) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(18), dp(16), dp(18));
        root.setBackgroundColor(BG);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        TextView h = text(title, 27, TEXT);
        h.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(h);
        TextView sub = text(subtitle, 14, MUTED);
        sub.setPadding(0, dp(4), 0, dp(12));
        root.addView(sub);
        return root;
    }

    private ScrollView scrollPage(String title, String subtitle, LinearLayout[] out) {
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = page(title, subtitle);
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));
        out[0] = root;
        return scroll;
    }

    private TextView text(String value, float sp, int color) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(sp);
        v.setTextColor(color);
        v.setGravity(Gravity.START);
        v.setLineSpacing(0f, 1.08f);
        return v;
    }

    private TextView card(String value) {
        TextView v = text(value, 16, TEXT);
        v.setBackgroundColor(CARD);
        v.setPadding(dp(14), dp(14), dp(14), dp(14));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(5), 0, dp(5));
        v.setLayoutParams(lp);
        return v;
    }

    private Button button(String label) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(15);
        return b;
    }

    private EditText input(String hint) {
        EditText e = new EditText(this);
        e.setHint(hint);
        e.setHintTextColor(MUTED);
        e.setTextColor(TEXT);
        e.setBackgroundColor(CARD);
        e.setPadding(dp(12), dp(10), dp(12), dp(10));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(5), 0, dp(5));
        e.setLayoutParams(lp);
        return e;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void showFatal(String message) {
        LinearLayout root = page("THF Rescue", "خطأ في اختيار المنتج");
        root.addView(card(message));
        setContentView(root);
    }

    private void showHub() {
        LinearLayout[] out = new LinearLayout[1];
        ScrollView scroll = scrollPage("THF Hub", "بوابة المنظومة: تكتشف التطبيقات المثبتة وتفتحها فعليًا.", out);
        LinearLayout root = out[0];
        root.addView(card("نسخة Rescue: كل خدمة مستقلة؛ التطبيقات غير المثبتة تظهر بوضوح بدل أزرار وهمية."));
        for (ProductRegistry.Product product : ProductRegistry.all().values()) {
            if ("hub".equals(product.key)) continue;
            Intent launch = getPackageManager().getLaunchIntentForPackage(product.packageId);
            Button b = button((launch == null ? "○ " : "● ") + product.title + (launch == null ? " — غير مثبت" : " — فتح"));
            b.setEnabled(launch != null);
            if (launch != null) b.setOnClickListener(v -> startActivity(launch));
            root.addView(b, new LinearLayout.LayoutParams(-1, dp(52)));
        }
        setContentView(scroll);
    }

    private void showFitness() {
        LinearLayout root = page("THF Fitness", "دليل تمرين متحرك تلقائيًا + مؤقت؛ يعمل أوفلاين بدون الضغط لتغيير الوضعية.");
        ExerciseView exercise = new ExerciseView(this);
        root.addView(exercise, new LinearLayout.LayoutParams(-1, 0, 1f));
        TextView status = card("جاهز — Jumping Jack — 00:30");
        root.addView(status);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        Button start = button("ابدأ / إيقاف");
        Button next = button("التالي");
        row.addView(start, new LinearLayout.LayoutParams(0, dp(52), 1f));
        row.addView(next, new LinearLayout.LayoutParams(0, dp(52), 1f));
        root.addView(row);

        final String[] names = {"Jumping Jack", "Squat", "High Knees", "Arm Raise"};
        final int[] index = {0};
        final int[] left = {30};
        final boolean[] running = {false};
        final Runnable[] ticker = new Runnable[1];
        ticker[0] = () -> {
            if (!running[0]) return;
            left[0]--;
            if (left[0] <= 0) {
                index[0] = (index[0] + 1) % names.length;
                left[0] = 30;
                exercise.setMode(index[0]);
            }
            status.setText("نشط — " + names[index[0]] + " — 00:" + String.format(Locale.US, "%02d", left[0]));
            handler.postDelayed(ticker[0], 1000);
        };
        start.setOnClickListener(v -> {
            running[0] = !running[0];
            exercise.setRunning(running[0]);
            handler.removeCallbacks(ticker[0]);
            if (running[0]) {
                status.setText("نشط — " + names[index[0]]);
                handler.postDelayed(ticker[0], 1000);
            } else status.setText("متوقف — " + names[index[0]]);
        });
        next.setOnClickListener(v -> {
            index[0] = (index[0] + 1) % names.length;
            left[0] = 30;
            exercise.setMode(index[0]);
            status.setText((running[0] ? "نشط — " : "جاهز — ") + names[index[0]] + " — 00:30");
        });
        setContentView(root);
    }

    private void showWave() {
        LinearLayout root = page("WAVE MAWJA", "مسار تشغيل حقيقي من ملفات الهاتف لاختبار المشاهدة الأساسية بدون الاعتماد على السيرفر.");
        waveVideo = new VideoView(this);
        waveVideo.setBackgroundColor(Color.BLACK);
        root.addView(waveVideo, new LinearLayout.LayoutParams(-1, 0, 1f));
        TextView status = card("اختر فيديو من الهاتف.");
        root.addView(status);
        Button choose = button("اختيار فيديو وتشغيله");
        Button toggle = button("تشغيل / إيقاف مؤقت");
        choose.setOnClickListener(v -> {
            Intent pick = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            pick.addCategory(Intent.CATEGORY_OPENABLE);
            pick.setType("video/*");
            startActivityForResult(pick, PICK_VIDEO);
        });
        toggle.setOnClickListener(v -> {
            if (waveVideo == null) return;
            if (waveVideo.isPlaying()) waveVideo.pause(); else waveVideo.start();
        });
        waveVideo.setOnPreparedListener(mp -> {
            status.setText("الفيديو جاهز — " + Math.max(0, waveVideo.getDuration() / 1000) + " ثانية");
            waveVideo.start();
        });
        waveVideo.setOnErrorListener((mp, what, extra) -> {
            status.setText("تعذر تشغيل هذا الملف على الجهاز.");
            return true;
        });
        root.addView(choose, new LinearLayout.LayoutParams(-1, dp(50)));
        root.addView(toggle, new LinearLayout.LayoutParams(-1, dp(50)));
        setContentView(root);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_VIDEO && resultCode == RESULT_OK && data != null && data.getData() != null && waveVideo != null) {
            Uri uri = data.getData();
            try { getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION); } catch (Exception ignored) {}
            waveVideo.setVideoURI(uri);
            waveVideo.requestFocus();
        }
    }

    private void showArena() {
        LinearLayout[] out = new LinearLayout[1];
        ScrollView scroll = scrollPage("Arena", "مجتمع محلي يعمل أوفلاين: كتابة منشورات وحفظها على الهاتف.", out);
        LinearLayout root = out[0];
        SharedPreferences prefs = getSharedPreferences("arena", MODE_PRIVATE);
        EditText compose = input("اكتب منشورًا...");
        Button post = button("نشر محلي");
        TextView feed = card(prefs.getString("feed", "لا توجد منشورات بعد."));
        post.setOnClickListener(v -> {
            String body = compose.getText().toString().trim();
            if (body.isEmpty()) return;
            String previous = prefs.getString("feed", "");
            String updated = "• " + body + "\n\n" + previous;
            prefs.edit().putString("feed", updated).apply();
            feed.setText(updated);
            compose.setText("");
        });
        root.addView(compose);
        root.addView(post, new LinearLayout.LayoutParams(-1, dp(50)));
        root.addView(feed);
        setContentView(scroll);
    }

    private void showPublisher() {
        LinearLayout[] out = new LinearLayout[1];
        ScrollView scroll = scrollPage("THF Publisher", "اكتب المحتوى مرة واحدة ثم أرسله فعليًا لأي تطبيق مشاركة مثبت على الهاتف.", out);
        LinearLayout root = out[0];
        EditText body = input("النص / الكابشن...");
        Button share = button("فتح منصات المشاركة");
        share.setOnClickListener(v -> {
            String value = body.getText().toString().trim();
            if (value.isEmpty()) { toast("اكتب محتوى أولًا"); return; }
            Intent send = new Intent(Intent.ACTION_SEND);
            send.setType("text/plain");
            send.putExtra(Intent.EXTRA_TEXT, value);
            startActivity(Intent.createChooser(send, "اختر منصة النشر"));
        });
        root.addView(body);
        root.addView(share, new LinearLayout.LayoutParams(-1, dp(52)));
        root.addView(card("هذه النسخة تستخدم Android Sharesheet الحقيقي. النشر التلقائي الصامت يحتاج API رسمي وصلاحيات كل منصة."));
        setContentView(scroll);
    }

    private void showVault() {
        LinearLayout[] out = new LinearLayout[1];
        ScrollView scroll = scrollPage("THF Vault", "دفتر أصول وملاحظات محلي مستمر؛ البيانات تبقى بعد إغلاق التطبيق.", out);
        LinearLayout root = out[0];
        SharedPreferences prefs = getSharedPreferences("vault", MODE_PRIVATE);
        EditText note = input("ملاحظة / أصل / عنوان محفظة عام...");
        note.setText(prefs.getString("note", ""));
        TextView state = card("جاهز للحفظ المحلي.");
        Button save = button("حفظ");
        save.setOnClickListener(v -> {
            prefs.edit().putString("note", note.getText().toString()).apply();
            state.setText("تم الحفظ على الجهاز.");
        });
        root.addView(note);
        root.addView(save, new LinearLayout.LayoutParams(-1, dp(50)));
        root.addView(state);
        root.addView(card("لا تدخل seed phrase أو private key هنا؛ Rescue لا يدّعي أنه مخزن مفاتيح مشفرة."));
        setContentView(scroll);
    }

    private void showTokenOps() {
        LinearLayout[] out = new LinearLayout[1];
        ScrollView scroll = scrollPage("THF TokenOps", "Solana Mainnet قراءة فقط؛ لا يطلب التطبيق أي مفتاح خاص.", out);
        LinearLayout root = out[0];
        EditText address = input("Public Solana address");
        address.setSingleLine(true);
        Button lookup = button("قراءة رصيد SOL");
        TextView result = card("أدخل عنوانًا عامًا صالحًا.");
        lookup.setOnClickListener(v -> {
            String value = address.getText().toString().trim();
            if (!value.matches("[1-9A-HJ-NP-Za-km-z]{32,44}")) {
                result.setText("العنوان لا يطابق صيغة Base58 المتوقعة.");
                return;
            }
            result.setText("جارٍ الاتصال بـSolana Mainnet...");
            new Thread(() -> querySolBalance(value, result)).start();
        });
        root.addView(address);
        root.addView(lookup, new LinearLayout.LayoutParams(-1, dp(50)));
        root.addView(result);
        root.addView(card("التحويل والسيولة والتوقيع غير مفعلة في Rescue حتى لا نتعامل مع مفاتيح خاصة قبل طبقة أمان إنتاجية."));
        setContentView(scroll);
    }

    private void querySolBalance(String address, TextView result) {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL("https://api.mainnet-beta.solana.com").openConnection();
            connection.setConnectTimeout(8000);
            connection.setReadTimeout(8000);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            String payload = "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getBalance\",\"params\":[\"" + address + "\",{\"commitment\":\"confirmed\"}]}";
            try (OutputStream os = connection.getOutputStream()) {
                os.write(payload.getBytes(StandardCharsets.UTF_8));
            }
            int code = connection.getResponseCode();
            BufferedReader reader = new BufferedReader(new InputStreamReader(
                    code >= 200 && code < 300 ? connection.getInputStream() : connection.getErrorStream(), StandardCharsets.UTF_8));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) response.append(line);
            Matcher matcher = Pattern.compile("\\\"value\\\"\\s*:\\s*(\\d+)").matcher(response.toString());
            if (code >= 200 && code < 300 && matcher.find()) {
                double sol = Long.parseLong(matcher.group(1)) / 1_000_000_000d;
                runOnUiThread(() -> result.setText(String.format(Locale.US, "الرصيد: %.9f SOL\nMainnet — read only", sol)));
            } else {
                runOnUiThread(() -> result.setText("تعذرت قراءة الرصيد. HTTP " + code));
            }
        } catch (Exception error) {
            runOnUiThread(() -> result.setText("فشل الاتصال: " + error.getClass().getSimpleName()));
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void showRuinsCiv() {
        LinearLayout root = page("RuinsCiv", "عالم/مزرعة محلية قابلة للعب: المس للتحرك واجمع الموارد، ويمكن إنشاء جلسة LAN مباشرة.");
        root.addView(new WorldView(this), new LinearLayout.LayoutParams(-1, 0, 1f));
        addLanControls(root);
        setContentView(root);
    }

    private void showEndCiv() {
        LinearLayout root = page("EndCiv", "قتال أوفلاين: اسحب للتحرك وارفع إصبعك لإطلاق النار؛ LAN مباشر متاح للاكتشاف.");
        root.addView(new CombatView(this), new LinearLayout.LayoutParams(-1, 0, 1f));
        addLanControls(root);
        setContentView(root);
    }

    private void addLanControls(LinearLayout root) {
        TextView state = card("LAN: غير متصل");
        EditText ip = input("IP الهاتف المضيف — مثال 192.168.1.5");
        ip.setSingleLine(true);
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        Button host = button("استضافة");
        Button join = button("انضمام");
        row.addView(host, new LinearLayout.LayoutParams(0, dp(48), 1f));
        row.addView(join, new LinearLayout.LayoutParams(0, dp(48), 1f));
        root.addView(state);
        root.addView(ip);
        root.addView(row);
        host.setOnClickListener(v -> new Thread(() -> hostLan(state)).start());
        join.setOnClickListener(v -> {
            String target = ip.getText().toString().trim();
            if (target.isEmpty()) { toast("اكتب IP المضيف"); return; }
            new Thread(() -> joinLan(target, state)).start();
        });
    }

    private void hostLan(TextView state) {
        try {
            if (lanServer != null) try { lanServer.close(); } catch (Exception ignored) {}
            lanServer = new ServerSocket();
            lanServer.setReuseAddress(true);
            lanServer.bind(new InetSocketAddress(7777));
            String local = localIpv4();
            runOnUiThread(() -> state.setText("LAN HOST — " + local + ":7777\nفي انتظار هاتف آخر..."));
            try (Socket socket = lanServer.accept()) {
                BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
                String hello = reader.readLine();
                socket.getOutputStream().write(("THF-LAN-OK:" + BuildConfig.PRODUCT_KEY + "\n").getBytes(StandardCharsets.UTF_8));
                socket.getOutputStream().flush();
                runOnUiThread(() -> state.setText("LAN متصل فعليًا — " + hello));
            }
        } catch (Exception error) {
            if (!isFinishing()) runOnUiThread(() -> state.setText("LAN host error: " + error.getClass().getSimpleName()));
        }
    }

    private void joinLan(String target, TextView state) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(target, 7777), 4000);
            socket.getOutputStream().write(("THF-LAN:" + BuildConfig.PRODUCT_KEY + "\n").getBytes(StandardCharsets.UTF_8));
            socket.getOutputStream().flush();
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            String reply = reader.readLine();
            runOnUiThread(() -> state.setText("LAN متصل — " + reply));
        } catch (Exception error) {
            runOnUiThread(() -> state.setText("تعذر الاتصال المحلي: " + error.getClass().getSimpleName()));
        }
    }

    private String localIpv4() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            for (NetworkInterface network : Collections.list(interfaces)) {
                for (InetAddress address : Collections.list(network.getInetAddresses())) {
                    if (!address.isLoopbackAddress() && address instanceof Inet4Address) return address.getHostAddress();
                }
            }
        } catch (Exception ignored) {}
        return "0.0.0.0";
    }

    private void toast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    @Override protected void onDestroy() {
        super.onDestroy();
        handler.removeCallbacksAndMessages(null);
        if (lanServer != null) try { lanServer.close(); } catch (Exception ignored) {}
    }
}
