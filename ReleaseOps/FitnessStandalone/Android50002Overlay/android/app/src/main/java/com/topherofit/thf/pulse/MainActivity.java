package com.topherofit.thf.pulse;

import android.app.AlertDialog;
import androidx.activity.ComponentActivity;
import androidx.activity.result.ActivityResultLauncher;
import androidx.health.connect.client.PermissionController;
import androidx.webkit.WebViewAssetLoader;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Locale;
import java.util.Set;

public final class MainActivity extends ComponentActivity {
    private static final String PREFS="thf_ux";
    private WebView web;
    private ProgressBar progress;
    private LinearLayout statusPanel;
    private TextView statusTitle;
    private TextView statusBody;
    private Button retry;
    private SharedPreferences prefs;
    private WebViewAssetLoader assetLoader;
    private HealthConnectBridge healthConnect;
    private ActivityResultLauncher<Set<String>> healthPermissionLauncher;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        healthPermissionLauncher=registerForActivityResult(
            PermissionController.createRequestPermissionResultContract(),
            granted -> { if (healthConnect!=null) healthConnect.onPermissionsResult(granted); }
        );
        healthConnect=new HealthConnectBridge(this,healthPermissionLauncher);
        prefs=getSharedPreferences(PREFS,MODE_PRIVATE);
        buildUi();
        configureWebView();
        Uri incoming=getIntent()!=null?getIntent().getData():null;
        if (incoming!=null) handleDeepLink(incoming); else loadProduct();
    }

    private void buildUi() {
        FrameLayout root=new FrameLayout(this);
        web=new WebView(this);
        root.addView(web,new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,FrameLayout.LayoutParams.MATCH_PARENT));

        progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);
        progress.setMax(100); progress.setVisibility(View.GONE);
        FrameLayout.LayoutParams pp=new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,dp(3)); pp.gravity=Gravity.TOP;
        root.addView(progress,pp);

        ImageButton settings=new ImageButton(this);
        settings.setImageResource(android.R.drawable.ic_menu_preferences);
        settings.setContentDescription(getString(R.string.experience_settings));
        settings.setBackgroundColor(0xCC111827);
        settings.setOnClickListener(v -> showSettings());
        FrameLayout.LayoutParams sp=new FrameLayout.LayoutParams(dp(48),dp(48)); sp.gravity=Gravity.TOP|Gravity.END; sp.setMargins(dp(8),dp(8),dp(8),dp(8));
        root.addView(settings,sp);

        statusPanel=new LinearLayout(this); statusPanel.setOrientation(LinearLayout.VERTICAL); statusPanel.setGravity(Gravity.CENTER); statusPanel.setPadding(dp(28),dp(28),dp(28),dp(28)); statusPanel.setBackgroundColor(0xF5111827);
        statusTitle=new TextView(this); statusTitle.setTextColor(Color.WHITE); statusTitle.setTextSize(22); statusTitle.setGravity(Gravity.CENTER);
        statusBody=new TextView(this); statusBody.setTextColor(0xFFCBD5E1); statusBody.setTextSize(15); statusBody.setGravity(Gravity.CENTER); statusBody.setPadding(0,dp(12),0,dp(18));
        retry=new Button(this); retry.setText(R.string.retry); retry.setContentDescription(getString(R.string.retry_connection)); retry.setOnClickListener(v -> loadProduct());
        statusPanel.addView(statusTitle,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
        statusPanel.addView(statusBody,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));
        statusPanel.addView(retry,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT,LinearLayout.LayoutParams.WRAP_CONTENT));
        statusPanel.setVisibility(View.GONE);
        root.addView(statusPanel,new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);
    }

    private void configureWebView() {
        assetLoader=new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this))
            .build();
        CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);
        WebSettings s=web.getSettings();
        s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(false); s.setAllowContentAccess(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        applyPrefs(false);
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onProgressChanged(WebView view,int newProgress) {
                progress.setProgress(newProgress); progress.setVisibility(newProgress>=100?View.GONE:View.VISIBLE);
            }
        });
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request) {
                Uri url=request.getUrl();
                if (url!=null && "appassets.androidplatform.net".equals(url.getHost())) return assetLoader.shouldInterceptRequest(url);
                return super.shouldInterceptRequest(view,request);
            }
            @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap icon) { hideStatus(); progress.setVisibility(View.VISIBLE); }
            @Override public void onPageFinished(WebView view,String url) { progress.setVisibility(View.GONE); injectNativePrefs(); }
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest req) {
                Uri u=req.getUrl(); String scheme=u.getScheme()==null?"":u.getScheme();
                if ("topherofit".equals(scheme)) { handleDeepLink(u); return true; }
                if ("https".equals(scheme) && isOAuthStart(u)) { openOAuthInSystemBrowser(u); return true; }
                return !"https".equals(scheme);
            }
            @Override public void onReceivedError(WebView view,WebResourceRequest req,WebResourceError error) {
                if (req.isForMainFrame()) showNetworkError();
            }
        });
    }

    private void loadProduct() {
        String base=BuildConfig.THF_BASE_URL==null?"":BuildConfig.THF_BASE_URL.trim();
        if (!isSafeHttps(base)) { showConfigError(getString(R.string.service_endpoint_missing)); return; }
        if (!isOnline()) { showOffline(); return; }
        loadUrl(base);
    }
    private void loadUrl(String url) { hideStatus(); web.loadUrl(url); }
    private boolean isSafeHttps(String value) {
        if (value==null) return false;
        try { Uri u=Uri.parse(value.trim()); return "https".equalsIgnoreCase(u.getScheme()) && u.getHost()!=null && !u.getHost().isBlank() && u.getUserInfo()==null; }
        catch (Exception ignored) { return false; }
    }
    private boolean isOnline() {
        ConnectivityManager cm=(ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm==null) return true;
        Network n=cm.getActiveNetwork(); if (n==null) return false;
        NetworkCapabilities c=cm.getNetworkCapabilities(n); return c!=null && c.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private boolean isOAuthStart(Uri u) {
        if (u==null || u.getPath()==null) return false;
        String path=u.getPath();
        return path.matches("/auth/(google|microsoft)/start");
    }
    private void openOAuthInSystemBrowser(Uri incoming) {
        Uri safe=incoming.buildUpon().clearQuery().appendQueryParameter("client","android").build();
        try { startActivity(new Intent(Intent.ACTION_VIEW,safe)); }
        catch (Exception e) { Toast.makeText(this,getString(R.string.network_error_title),Toast.LENGTH_SHORT).show(); }
    }
    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent); setIntent(intent);
        Uri incoming=intent==null?null:intent.getData();
        if (incoming!=null) handleDeepLink(incoming);
    }

    private void handleDeepLink(Uri u) {
        if (u==null) { loadProduct(); return; }
        if ("retry".equals(u.getHost())) { loadProduct(); return; }
        if ("health".equals(u.getHost())) { handleHealthLink(u); return; }
        if ("auth".equals(u.getHost()) && "/complete".equals(u.getPath())) {
            String ticket=u.getQueryParameter("ticket");
            String base=BuildConfig.THF_BASE_URL==null?"":BuildConfig.THF_BASE_URL.trim();
            if (!isSafeHttps(base) || ticket==null || ticket.isBlank()) { showConfigError(getString(R.string.service_endpoint_missing)); return; }
            Uri dest=Uri.parse(base).buildUpon().appendPath("auth").appendPath("app").appendPath("consume").appendQueryParameter("ticket",ticket).build();
            loadUrl(dest.toString()); return;
        }
        if ("pass".equals(u.getHost())) {
            String pass=BuildConfig.THF_PASS_URL==null?"":BuildConfig.THF_PASS_URL.trim();
            if (!isSafeHttps(pass)) { showConfigError(getString(R.string.pass_endpoint_missing)); return; }
            String ticket=u.getQueryParameter("ticket");
            String target=u.getQueryParameter("target");
            if (target!=null && !BuildConfig.THF_APP_SLUG.equals(target)) { Toast.makeText(this,getString(R.string.handoff_target_mismatch),Toast.LENGTH_SHORT).show(); return; }
            Uri dest=Uri.parse(pass).buildUpon().appendPath("handoff").appendPath("consume").appendQueryParameter("target",BuildConfig.THF_APP_SLUG).appendQueryParameter("ticket",ticket==null?"":ticket).build();
            loadUrl(dest.toString()); return;
        }
        loadProduct();
    }

    private void handleHealthLink(Uri u) {
        String path=u.getPath()==null?"":u.getPath();
        if ("/permissions".equals(path) || "/steps".equals(path)) { healthConnect.requestPermissionsAndReadSteps(); return; }
        if ("/exercise".equals(path)) {
            try {
                long start=Long.parseLong(u.getQueryParameter("start"));
                long end=Long.parseLong(u.getQueryParameter("end"));
                healthConnect.writeExerciseSession(start,end,u.getQueryParameter("title"));
            } catch (Exception ignored) { Toast.makeText(this,"Invalid Health Connect workout payload",Toast.LENGTH_SHORT).show(); }
        }
    }

    private void showOffline() { hideStatus(); web.loadUrl("https://appassets.androidplatform.net/assets/offline.html"); }
    private void showNetworkError() { showStatus(getString(R.string.network_error_title),getString(R.string.network_error_body),true); }
    private void showConfigError(String message) { showStatus(getString(R.string.service_not_configured),message,false); }
    private void showStatus(String title,String body,boolean canRetry) { statusTitle.setText(title); statusBody.setText(body); retry.setVisibility(canRetry?View.VISIBLE:View.GONE); statusPanel.setVisibility(View.VISIBLE); progress.setVisibility(View.GONE); }
    private void hideStatus() { statusPanel.setVisibility(View.GONE); }

    private void showSettings() {
        final String[] items={getString(R.string.data_saver),getString(R.string.reduce_motion),getString(R.string.high_contrast)};
        final boolean[] checked={prefs.getBoolean("data_saver",false),prefs.getBoolean("reduce_motion",false),prefs.getBoolean("high_contrast",false)};
        new AlertDialog.Builder(this).setTitle(R.string.experience_settings).setMultiChoiceItems(items,checked,(d,w,isChecked)->checked[w]=isChecked)
          .setPositiveButton(R.string.apply,(d,w)->{ prefs.edit().putBoolean("data_saver",checked[0]).putBoolean("reduce_motion",checked[1]).putBoolean("high_contrast",checked[2]).apply(); applyPrefs(true); })
          .setNeutralButton(R.string.health_connect,(d,w)->healthConnect.requestPermissionsAndReadSteps())
          .setNegativeButton(R.string.text_size,(d,w)->showTextSize()).show();
    }
    private void showTextSize() {
        new AlertDialog.Builder(this).setTitle(R.string.text_size).setSingleChoiceItems(new String[]{getString(R.string.zoom_100),getString(R.string.zoom_115),getString(R.string.zoom_130)},zoomIndex(),(d,w)->{ prefs.edit().putInt("text_zoom",w==1?115:w==2?130:100).apply(); d.dismiss(); applyPrefs(true); }).setNegativeButton(R.string.cancel,null).show();
    }
    private int zoomIndex() { int z=prefs.getInt("text_zoom",100); return z>=130?2:z>=115?1:0; }
    private void applyPrefs(boolean reload) {
        boolean saver=prefs.getBoolean("data_saver",false);
        WebSettings s=web.getSettings(); s.setLoadsImagesAutomatically(!saver); s.setCacheMode(WebSettings.LOAD_DEFAULT); s.setTextZoom(prefs.getInt("text_zoom",100));
        if (reload && web.getUrl()!=null) { injectNativePrefs(); if (!saver) web.reload(); }
    }
    private void injectNativePrefs() {
        boolean saver=prefs.getBoolean("data_saver",false), motion=prefs.getBoolean("reduce_motion",false), contrast=prefs.getBoolean("high_contrast",false); int zoom=prefs.getInt("text_zoom",100);
        String locale=Locale.getDefault().toLanguageTag().replace("'","_");
        String js="(function(){window.THF_NATIVE_PREFS={dataSaver:"+saver+",reduceMotion:"+motion+",highContrast:"+contrast+",textZoom:"+zoom+",locale:'"+locale+"'};"+
          "var id='thf-native-a11y';var old=document.getElementById(id);if(old)old.remove();var st=document.createElement('style');st.id=id;st.textContent='"+
          (motion?"*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}":"")+
          (contrast?"html{filter:contrast(1.12)}a,button,input,select,textarea{outline-offset:3px}":"")+
          "';document.head&&document.head.appendChild(st);window.dispatchEvent(new CustomEvent('thf:native-prefs',{detail:window.THF_NATIVE_PREFS}));})();";
        web.evaluateJavascript(js,null);
    }
    private int dp(int v) { return Math.round(v*getResources().getDisplayMetrics().density); }
    @Override protected void onResume() { super.onResume(); if (statusPanel!=null && statusPanel.getVisibility()==View.VISIBLE && isOnline()) { /* explicit retry remains user-controlled */ } }
    @Override protected void onDestroy() { if (healthConnect!=null) healthConnect.close(); if (web!=null) web.destroy(); super.onDestroy(); }
    @Override public void onBackPressed() { if (statusPanel!=null && statusPanel.getVisibility()==View.VISIBLE) { hideStatus(); return; } if (web!=null && web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}
