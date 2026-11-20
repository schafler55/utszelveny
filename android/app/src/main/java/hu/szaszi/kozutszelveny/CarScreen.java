package hu.szaszi.kozutszelveny;

import android.graphics.Canvas;
import android.graphics.Rect;
import android.view.Surface;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.car.app.AppManager;
import androidx.car.app.CarContext;
import androidx.car.app.Screen;
import androidx.car.app.SurfaceCallback;
import androidx.car.app.SurfaceContainer;
import androidx.car.app.model.Action;
import androidx.car.app.model.ActionStrip;
import androidx.car.app.model.Template;
import androidx.car.app.navigation.model.NavigationTemplate;

import org.json.JSONObject;

/**
 * Az autó kijelzője: navigációs sablon, a felületre a CarDraw rajzol (B terv: fő kártya + sebességkártya).
 * A jobb felső "Téma" gomb: Auto (az autó nappal / éjjel jelzése) → Sötét → Világos.
 */
final class CarScreen extends Screen {

    private final CarEngine engine;
    private JSONObject data;
    private Surface surface;
    private int sw, sh;
    private Rect visible;
    private int themeMode;   // 0 = auto (car), 1 = dark, 2 = light

    CarScreen(@NonNull CarContext carContext, CarEngine engine) {
        super(carContext);
        this.engine = engine;
        carContext.getCarService(AppManager.class).setSurfaceCallback(new SurfaceCallback() {
            @Override
            public void onSurfaceAvailable(@NonNull SurfaceContainer c) {
                surface = c.getSurface();
                sw = c.getWidth();
                sh = c.getHeight();
                redraw();
            }

            @Override
            public void onVisibleAreaChanged(@NonNull Rect r) {
                visible = new Rect(r);
                redraw();
            }

            @Override
            public void onStableAreaChanged(@NonNull Rect r) {
                if (visible == null) visible = new Rect(r);
                redraw();
            }

            @Override
            public void onSurfaceDestroyed(@NonNull SurfaceContainer c) {
                surface = null;
            }
        });
    }

    void onData(JSONObject o) {
        data = o;
        redraw();
    }

    boolean dark() {
        if (themeMode == 1) return true;
        if (themeMode == 2) return false;
        return getCarContext().isDarkMode();
    }

    void redraw() {
        Surface s = surface;
        if (s == null || !s.isValid() || sw <= 0 || sh <= 0) return;
        Canvas c = null;
        try {
            c = s.lockCanvas(null);
            Rect a = visible != null && !visible.isEmpty() ? visible : new Rect(0, 0, sw, sh);
            CarDraw.draw(c, sw, sh, a, data, dark());
        } catch (Exception ignored) {
        } finally {
            if (c != null) {
                try {
                    s.unlockCanvasAndPost(c);
                } catch (Exception ignored) {
                }
            }
        }
    }

    @NonNull
    @Override
    public Template onGetTemplate() {
        String label = themeMode == 0 ? "Téma: Auto" : themeMode == 1 ? "Téma: Sötét" : "Téma: Világos";
        Action theme = new Action.Builder()
                .setTitle(label)
                .setOnClickListener(() -> {
                    themeMode = (themeMode + 1) % 3;
                    invalidate();
                    redraw();
                })
                .build();
        return new NavigationTemplate.Builder()
                .setActionStrip(new ActionStrip.Builder().addAction(theme).build())
                .build();
    }

    @Nullable
    JSONObject data() {
        return data;
    }
}
