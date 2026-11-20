package hu.szaszi.kozutszelveny;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import org.json.JSONObject;

import java.util.Locale;

/**
 * Az autós kijelző adatforrása.
 * Ugyanazt az assets/index.html-t tölti be egy rejtett (képernyőn nem látható) WebView-ba, "?car=1" módban.
 * A GNSS-pozíciót a LocationManager adja (window.__carFix), az oldal kiszámolja az utat, a szelvényt,
 * a sebességkorlátozást stb., és JSON-ban visszaküldi (AndroidBridge.carUpdate). Itt semmi nincs újraszámolva.
 */
final class CarEngine {

    interface Listener {
        void onData(JSONObject data);
    }

    private static final String HOST = "appassets.androidplatform.net";
    private static final String CAR_URL = "https://" + HOST + "/assets/index.html?car=1";

    private final Context ctx;
    private final Handler main = new Handler(Looper.getMainLooper());
    private WebView web;
    private Listener listener;
    private boolean pageReady;
    private boolean locOn;
    private LocationManager lm;

    private final LocationListener locListener = new LocationListener() {
        @Override
        public void onLocationChanged(Location l) {
            sendFix(l);
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {
        }

        @Override
        public void onProviderEnabled(String provider) {
        }

        @Override
        public void onProviderDisabled(String provider) {
        }
    };

    CarEngine(Context appContext) {
        ctx = appContext;
    }

    void setListener(Listener l) {
        listener = l;
    }

    boolean hasLocationPermission() {
        return ctx.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    @SuppressLint("SetJavaScriptEnabled")
    void start() {
        if (web != null) return;
        if (!hasLocationPermission()) {
            post(msg("noperm", "Helyhozzáférés szükséges",
                    "Nyisd meg az ÚtSzelvényt a telefonon, és engedélyezd a helyadatokat."));
            // try again later: the user may grant it on the phone meanwhile
            main.postDelayed(this::retryStart, 3000);
            return;
        }
        post(msg("search", "ÚtSzelvény indul…", "Úthálózati adatok betöltése"));

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(ctx))
                .build();
        web = new WebView(ctx);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);      // same origin as the phone app → reads its settings (the car page never writes)
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " UtSzelveny/0.19 UtSzelvenyCar");
        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !HOST.equals(request.getUrl().getHost());
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                pageReady = true;
            }
        });
        web.onResume();
        web.resumeTimers();
        web.loadUrl(CAR_URL);
        startLocation();
    }

    private void retryStart() {
        if (web == null && listener != null) start();
    }

    void stop() {
        main.removeCallbacksAndMessages(null);
        stopLocation();
        if (web != null) {
            web.destroy();
            web = null;
        }
        pageReady = false;
        listener = null;
    }

    @SuppressLint("MissingPermission")
    private void startLocation() {
        if (locOn || !hasLocationPermission()) return;
        lm = (LocationManager) ctx.getSystemService(Context.LOCATION_SERVICE);
        if (lm == null) return;
        try {
            lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 0, locListener, Looper.getMainLooper());
            locOn = true;
        } catch (Exception e) {
            post(msg("off", "GNSS nem érhető el", "Kapcsold be a telefonon a helymeghatározást."));
        }
    }

    private void stopLocation() {
        if (lm != null && locOn) {
            try {
                lm.removeUpdates(locListener);
            } catch (Exception ignored) {
            }
        }
        locOn = false;
    }

    private void sendFix(Location l) {
        if (web == null || !pageReady) return;
        String js = String.format(Locale.US,
                "window.__carFix&&window.__carFix({lat:%.7f,lon:%.7f,acc:%.1f,spd:%s,hdg:%s})",
                l.getLatitude(), l.getLongitude(), l.hasAccuracy() ? l.getAccuracy() : 30f,
                l.hasSpeed() ? String.format(Locale.US, "%.2f", l.getSpeed()) : "null",
                l.hasBearing() ? String.format(Locale.US, "%.1f", l.getBearing()) : "null");
        web.evaluateJavascript(js, null);
    }

    private static JSONObject msg(String st, String t, String s) {
        JSONObject o = new JSONObject();
        try {
            o.put("st", st);
            o.put("t", t);
            o.put("s", s);
        } catch (Exception ignored) {
        }
        return o;
    }

    private void post(final JSONObject o) {
        main.post(() -> {
            if (listener != null) listener.onData(o);
        });
    }

    private final class Bridge {
        @JavascriptInterface
        public void carUpdate(String json) {
            try {
                post(new JSONObject(json));
            } catch (Exception ignored) {
            }
        }
    }
}
