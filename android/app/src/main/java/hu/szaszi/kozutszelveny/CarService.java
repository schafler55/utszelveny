package hu.szaszi.kozutszelveny;

import android.content.Intent;
import android.content.res.Configuration;

import androidx.annotation.NonNull;
import androidx.car.app.CarAppService;
import androidx.car.app.Screen;
import androidx.car.app.Session;
import androidx.car.app.validation.HostValidator;
import androidx.lifecycle.Lifecycle;
import androidx.lifecycle.LifecycleEventObserver;

/**
 * Android Auto belépési pont (navigációs kategória, Car App Library).
 * Az autó kijelzőjén a CarScreen rajzol; az adatokat a CarEngine adja
 * (ugyanaz az index.html egy rejtett WebView-ban, ?car=1 módban).
 */
public class CarService extends CarAppService {

    @NonNull
    @Override
    public HostValidator createHostValidator() {
        // The APK is installed outside Google Play (GitHub / F-Droid): Android Auto shows it only with
        // "Unknown sources" switched on in its developer settings, so any host is accepted here.
        return HostValidator.ALLOW_ALL_HOSTS_VALIDATOR;
    }

    @NonNull
    @Override
    public Session onCreateSession() {
        return new CarSessionImpl();
    }

    static final class CarSessionImpl extends Session {
        private CarScreen screen;
        private CarEngine engine;

        CarSessionImpl() {
            getLifecycle().addObserver((LifecycleEventObserver) (source, event) -> {
                if (event == Lifecycle.Event.ON_DESTROY) {
                    if (engine != null) engine.stop();
                    engine = null;
                    CarKeepAlive.stop(getCarContext());
                }
            });
        }

        @NonNull
        @Override
        public Screen onCreateScreen(@NonNull Intent intent) {
            engine = new CarEngine(getCarContext().getApplicationContext());
            screen = new CarScreen(getCarContext(), engine);
            engine.setListener(screen::onData);
            engine.start();
            CarKeepAlive.start(getCarContext());
            return screen;
        }

        @Override
        public void onCarConfigurationChanged(@NonNull Configuration newConfiguration) {
            if (screen != null) screen.redraw();   // day / night switch of the car
        }
    }
}
