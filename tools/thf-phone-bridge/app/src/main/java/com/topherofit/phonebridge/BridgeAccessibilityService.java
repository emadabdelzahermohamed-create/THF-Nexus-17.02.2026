package com.topherofit.phonebridge;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Bundle;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONArray;
import org.json.JSONObject;

import java.security.SecureRandom;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class BridgeAccessibilityService extends AccessibilityService {
    static final String TAG = "THFPhoneBridge";
    private static final Set<String> ALLOWED_PACKAGES = new HashSet<>(Arrays.asList(
            "com.topherofit.phonebridge",
            "com.topherofit.thf.pulse",
            "com.android.vending",
            "com.android.settings",
            "com.google.android.packageinstaller",
            "com.samsung.android.packageinstaller",
            "com.google.android.permissioncontroller",
            "com.android.permissioncontroller",
            "com.google.android.apps.healthdata",
            "com.sec.android.app.shealth"
    ));

    private static volatile BridgeAccessibilityService instance;
    private static volatile String sessionToken;

    static BridgeAccessibilityService getInstance() {
        return instance;
    }

    static String getSessionToken() {
        return sessionToken;
    }

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        sessionToken = newToken();
        Log.i(TAG, "READY");
        Log.i(TAG, "TOKEN " + sessionToken);
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        // Commands are explicit. We deliberately do not stream UI events or content.
    }

    @Override
    public void onInterrupt() {
        Log.i(TAG, "INTERRUPTED");
    }

    @Override
    public void onDestroy() {
        if (instance == this) instance = null;
        sessionToken = null;
        super.onDestroy();
    }

    JSONObject status() throws Exception {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        String pkg = packageOf(root);
        return new JSONObject()
                .put("ready", true)
                .put("package", pkg)
                .put("allowed", isAllowed(pkg));
    }

    String dumpAllowedWindow() throws Exception {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        requireAllowed(root);
        int[] count = new int[]{0};
        JSONObject result = new JSONObject()
                .put("package", packageOf(root))
                .put("tree", nodeToJson(root, count, 0))
                .put("nodeCount", count[0]);
        return result.toString();
    }

    boolean clickText(String text) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!allowed(root) || text == null || text.isBlank()) return false;
        List<AccessibilityNodeInfo> nodes = root.findAccessibilityNodeInfosByText(text);
        if (nodes == null) return false;
        for (AccessibilityNodeInfo node : nodes) {
            AccessibilityNodeInfo cursor = node;
            for (int depth = 0; cursor != null && depth < 5; depth++) {
                if (cursor.isClickable() && cursor.performAction(AccessibilityNodeInfo.ACTION_CLICK)) return true;
                cursor = cursor.getParent();
            }
        }
        return false;
    }

    boolean setText(String selector, String value) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!allowed(root) || selector == null || selector.isBlank() || value == null) return false;
        AccessibilityNodeInfo target = null;
        try {
            List<AccessibilityNodeInfo> byId = root.findAccessibilityNodeInfosByViewId(selector);
            if (byId != null && !byId.isEmpty()) target = byId.get(0);
        } catch (Exception ignored) {
            // Some windows do not expose view IDs.
        }
        if (target == null) {
            List<AccessibilityNodeInfo> byText = root.findAccessibilityNodeInfosByText(selector);
            if (byText != null && !byText.isEmpty()) target = byText.get(0);
        }
        if (target == null) return false;
        Bundle args = new Bundle();
        args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, value);
        return target.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args);
    }

    boolean tap(int x, int y) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!allowed(root)) return false;
        Path path = new Path();
        path.moveTo(x, y);
        GestureDescription gesture = new GestureDescription.Builder()
                .addStroke(new GestureDescription.StrokeDescription(path, 0, 60))
                .build();
        return dispatchGesture(gesture, null, null);
    }

    boolean global(int action) {
        AccessibilityNodeInfo root = getRootInActiveWindow();
        if (!allowed(root)) return false;
        return performGlobalAction(action);
    }

    private JSONObject nodeToJson(AccessibilityNodeInfo node, int[] count, int depth) throws Exception {
        if (node == null || count[0] >= 350 || depth >= 40) return new JSONObject().put("truncated", true);
        count[0]++;
        Rect bounds = new Rect();
        node.getBoundsInScreen(bounds);
        JSONObject out = new JSONObject()
                .put("class", safe(node.getClassName()))
                .put("text", safe(node.getText()))
                .put("desc", safe(node.getContentDescription()))
                .put("id", safe(node.getViewIdResourceName()))
                .put("clickable", node.isClickable())
                .put("enabled", node.isEnabled())
                .put("editable", node.isEditable())
                .put("bounds", bounds.flattenToString());
        JSONArray children = new JSONArray();
        for (int i = 0; i < node.getChildCount() && count[0] < 350; i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) children.put(nodeToJson(child, count, depth + 1));
        }
        out.put("children", children);
        return out;
    }

    private void requireAllowed(AccessibilityNodeInfo root) {
        String pkg = packageOf(root);
        if (!isAllowed(pkg)) throw new SecurityException("active package not in QA allowlist: " + pkg);
    }

    private boolean allowed(AccessibilityNodeInfo root) {
        return root != null && isAllowed(packageOf(root));
    }

    private static String packageOf(AccessibilityNodeInfo root) {
        return root == null || root.getPackageName() == null ? "" : root.getPackageName().toString();
    }

    private static boolean isAllowed(String pkg) {
        return pkg != null && ALLOWED_PACKAGES.contains(pkg);
    }

    private static String safe(CharSequence value) {
        return value == null ? "" : value.toString();
    }

    private static String newToken() {
        byte[] bytes = new byte[24];
        new SecureRandom().nextBytes(bytes);
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) out.append(String.format("%02x", b & 0xff));
        return out.toString();
    }
}
