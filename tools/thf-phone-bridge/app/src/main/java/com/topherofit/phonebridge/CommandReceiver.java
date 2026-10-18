package com.topherofit.phonebridge;

import android.accessibilityservice.AccessibilityService;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

import org.json.JSONObject;

import java.util.UUID;

public final class CommandReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String requestId = UUID.randomUUID().toString().substring(0, 8);
        try {
            BridgeAccessibilityService service = BridgeAccessibilityService.getInstance();
            if (service == null) {
                emit(requestId, new JSONObject().put("ok", false).put("error", "SERVICE_NOT_ENABLED").toString());
                return;
            }
            String supplied = intent.getStringExtra("token");
            String expected = BridgeAccessibilityService.getSessionToken();
            if (expected == null || !expected.equals(supplied)) {
                emit(requestId, new JSONObject().put("ok", false).put("error", "TOKEN_REJECTED").toString());
                return;
            }

            String command = intent.getStringExtra("command");
            if (command == null) command = "status";
            JSONObject result = new JSONObject().put("ok", true).put("command", command);
            switch (command) {
                case "status":
                    result.put("status", service.status());
                    emit(requestId, result.toString());
                    break;
                case "dump":
                    result.put("window", new JSONObject(service.dumpAllowedWindow()));
                    emitChunked(requestId, result.toString());
                    break;
                case "click_text":
                    result.put("performed", service.clickText(intent.getStringExtra("text")));
                    emit(requestId, result.toString());
                    break;
                case "set_text":
                    result.put("performed", service.setText(intent.getStringExtra("selector"), intent.getStringExtra("value")));
                    emit(requestId, result.toString());
                    break;
                case "tap":
                    result.put("performed", service.tap(intent.getIntExtra("x", -1), intent.getIntExtra("y", -1)));
                    emit(requestId, result.toString());
                    break;
                case "back":
                    result.put("performed", service.global(AccessibilityService.GLOBAL_ACTION_BACK));
                    emit(requestId, result.toString());
                    break;
                case "home":
                    result.put("performed", service.global(AccessibilityService.GLOBAL_ACTION_HOME));
                    emit(requestId, result.toString());
                    break;
                case "recents":
                    result.put("performed", service.global(AccessibilityService.GLOBAL_ACTION_RECENTS));
                    emit(requestId, result.toString());
                    break;
                default:
                    emit(requestId, new JSONObject().put("ok", false).put("error", "UNKNOWN_COMMAND").put("command", command).toString());
                    break;
            }
        } catch (Throwable error) {
            try {
                emit(requestId, new JSONObject()
                        .put("ok", false)
                        .put("error", error.getClass().getSimpleName())
                        .put("message", String.valueOf(error.getMessage()))
                        .toString());
            } catch (Exception ignored) {
                Log.e(BridgeAccessibilityService.TAG, "RESULT " + requestId + " fatal");
            }
        }
    }

    private static void emit(String requestId, String payload) {
        Log.i(BridgeAccessibilityService.TAG, "RESULT " + requestId + " " + payload);
    }

    private static void emitChunked(String requestId, String payload) {
        final int chunkSize = 2800;
        int total = Math.max(1, (payload.length() + chunkSize - 1) / chunkSize);
        Log.i(BridgeAccessibilityService.TAG, "DUMP_BEGIN " + requestId + " " + total);
        for (int i = 0; i < payload.length(); i += chunkSize) {
            int end = Math.min(payload.length(), i + chunkSize);
            Log.i(BridgeAccessibilityService.TAG, "DUMP_CHUNK " + requestId + " " + (i / chunkSize) + " " + payload.substring(i, end));
        }
        Log.i(BridgeAccessibilityService.TAG, "DUMP_END " + requestId);
    }
}
