package com.topherofit.rescue;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.MotionEvent;
import android.view.View;

final class WorldView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private float x = 160f, y = 260f, targetX = 160f, targetY = 260f;
    private int food, wood;
    private final float[][] items = {{90,160},{280,210},{160,390},{330,470},{75,520}};
    private final boolean[] collected = new boolean[items.length];

    WorldView(Context context) { super(context); }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.rgb(67, 111, 69));
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.rgb(113, 82, 48));
        canvas.drawRect(18f, 60f, getWidth() * 0.43f, getHeight() * 0.38f, paint);
        paint.setColor(Color.rgb(146, 202, 78));
        for (int i = 0; i < items.length; i++) if (!collected[i]) canvas.drawCircle(items[i][0], items[i][1], 18f, paint);

        float dx = targetX - x, dy = targetY - y;
        float distance = (float) Math.sqrt(dx * dx + dy * dy);
        if (distance > 3f) { x += dx / distance * 6f; y += dy / distance * 6f; }
        x = Math.max(24f, Math.min(getWidth() - 24f, x));
        y = Math.max(24f, Math.min(getHeight() - 24f, y));
        for (int i = 0; i < items.length; i++) {
            if (!collected[i]) {
                float ax = x - items[i][0], ay = y - items[i][1];
                if (ax * ax + ay * ay < 42f * 42f) {
                    collected[i] = true;
                    if (i % 2 == 0) food++; else wood++;
                }
            }
        }
        paint.setColor(Color.rgb(35, 70, 110));
        canvas.drawCircle(x, y, 24f, paint);
        paint.setColor(Color.WHITE);
        canvas.drawCircle(x, y - 7f, 8f, paint);
        paint.setTextSize(28f);
        canvas.drawText("Food " + food + "   Wood " + wood, 18f, 38f, paint);
        paint.setTextSize(21f);
        canvas.drawText("Tap to move and collect", 18f, getHeight() - 20f, paint);
        postInvalidateOnAnimation();
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        if (event.getAction() == MotionEvent.ACTION_DOWN || event.getAction() == MotionEvent.ACTION_MOVE) {
            targetX = event.getX(); targetY = event.getY(); return true;
        }
        return true;
    }
}
