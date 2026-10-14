package com.topherofit.rescue;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PointF;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.View;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

final class CombatView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Random random = new Random(7);
    private final List<PointF> bullets = new ArrayList<>();
    private final List<PointF> enemies = new ArrayList<>();
    private float playerX = 180f, spawnClock;
    private int score, hp = 3;
    private long previous = SystemClock.uptimeMillis();

    CombatView(Context context) { super(context); }

    private void reset() {
        bullets.clear(); enemies.clear(); score = 0; hp = 3; spawnClock = 0f;
        previous = SystemClock.uptimeMillis(); invalidate();
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.rgb(28, 31, 38));
        long now = SystemClock.uptimeMillis();
        float dt = Math.min(0.05f, (now - previous) / 1000f);
        previous = now;
        if (hp <= 0) {
            paint.setColor(Color.WHITE); paint.setTextAlign(Paint.Align.CENTER); paint.setTextSize(42f);
            canvas.drawText("GAME OVER", getWidth() / 2f, getHeight() / 2f, paint);
            paint.setTextSize(24f); canvas.drawText("Tap to restart", getWidth() / 2f, getHeight() / 2f + 48f, paint);
            return;
        }
        spawnClock += dt;
        if (spawnClock > 1.05f) {
            spawnClock = 0f;
            int width = Math.max(1, getWidth() - 60);
            enemies.add(new PointF(30f + random.nextInt(width), -20f));
        }
        for (PointF bullet : bullets) bullet.y -= 560f * dt;
        for (PointF enemy : enemies) enemy.y += 150f * dt;
        for (int i = enemies.size() - 1; i >= 0; i--) {
            PointF enemy = enemies.get(i);
            boolean hit = false;
            for (int j = bullets.size() - 1; j >= 0; j--) {
                PointF bullet = bullets.get(j);
                float dx = bullet.x - enemy.x, dy = bullet.y - enemy.y;
                if (dx * dx + dy * dy < 32f * 32f) {
                    bullets.remove(j); hit = true; score++; break;
                }
            }
            if (hit) enemies.remove(i);
            else if (enemy.y > getHeight() - 70f) { enemies.remove(i); hp--; }
        }
        for (int i = bullets.size() - 1; i >= 0; i--) if (bullets.get(i).y < 0f) bullets.remove(i);

        paint.setColor(Color.rgb(255, 190, 46));
        for (PointF bullet : bullets) canvas.drawCircle(bullet.x, bullet.y, 7f, paint);
        paint.setColor(Color.rgb(215, 67, 67));
        for (PointF enemy : enemies) canvas.drawCircle(enemy.x, enemy.y, 22f, paint);
        paint.setColor(Color.rgb(0, 180, 160));
        canvas.drawRect(playerX - 34f, getHeight() - 74f, playerX + 34f, getHeight() - 30f, paint);
        paint.setColor(Color.WHITE); paint.setTextAlign(Paint.Align.LEFT); paint.setTextSize(28f);
        canvas.drawText("Score " + score + "  HP " + hp, 18f, 38f, paint);
        postInvalidateOnAnimation();
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        if (hp <= 0 && event.getAction() == MotionEvent.ACTION_DOWN) { reset(); return true; }
        if (event.getAction() == MotionEvent.ACTION_DOWN || event.getAction() == MotionEvent.ACTION_MOVE) {
            playerX = Math.max(36f, Math.min(getWidth() - 36f, event.getX())); invalidate();
        }
        if (event.getAction() == MotionEvent.ACTION_UP) {
            bullets.add(new PointF(playerX, getHeight() - 82f)); invalidate();
        }
        return true;
    }
}
