package hu.szaszi.kozutszelveny;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.GnssStatus;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.WindowManager;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * ÚtSzelvény – Android keret.
 * A teljes alkalmazás az assets/index.html; ez az osztály csak megjeleníti,
 * GNSS- és kamera-engedélyt kér, a műholdak állapotát továbbítja az oldalnak, ébren tartja a képernyőt, és a "AndroidBridge"
 * JS-hídon keresztül fájlt ment (fotó → Képek/ÚtSzelvény, CSV → Letöltések/ÚtSzelvény) és megoszt.
 * Az oldal a https://appassets.androidplatform.net címről töltődik (biztonságos környezet),
 * így a helymeghatározás és a kamera működik, és az OpenStreetMap is kap Referer fejlécet.
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + HOST + "/assets/index.html";
    private static final String FOLDER = "ÚtSzelvény";
    private static final int REQ_LOCATION = 1;
    private static final int REQ_CAMERA = 2;
    private static final int REQ_STORAGE = 3;

    private WebView web;
    private GeolocationPermissions.Callback pendingCallback;
    private String pendingOrigin;
    private PermissionRequest pendingCamera;
    private Runnable pendingStorageJob;
    private Runnable pendingStorageFail;

    /* ---------- satellites (GnssStatus) → window.__gnss({v,u,c:[{k,v,u,cn}]}) ---------- */
    private LocationManager lm;
    private boolean gnssWanted = false;   // the page has location tracking on
    private boolean gnssOn = false;       // callback registered
    private long gnssLast = 0;

    private final GnssStatus.Callback gnssCb = new GnssStatus.Callback() {
        @Override
        public void onSatelliteStatusChanged(GnssStatus st) {
            long now = System.currentTimeMillis();
            if (now - gnssLast < 900) return;     // at most ~1 update per second
            gnssLast = now;
            int n = st.getSatelliteCount();
            int[] vis = new int[8];
            int[] used = new int[8];
            float[] cn = new float[8];
            int tv = 0, tu = 0;
            for (int i = 0; i < n; i++) {
                int k = st.getConstellationType(i);   // 1 GPS, 2 SBAS, 3 GLONASS, 4 QZSS, 5 BeiDou, 6 Galileo, 7 NavIC
                if (k < 0 || k > 7) k = 0;
                vis[k]++;
                tv++;
                if (st.usedInFix(i)) {
                    used[k]++;
                    tu++;
                    cn[k] += st.getCn0DbHz(i);
                }
            }
            StringBuilder sb = new StringBuilder();
            sb.append("{\"v\":").append(tv).append(",\"u\":").append(tu).append(",\"c\":[");
            boolean first = true;
            for (int k = 0; k < 8; k++) {
                if (vis[k] == 0) continue;
                if (!first) sb.append(',');
                first = false;
                sb.append("{\"k\":").append(k).append(",\"v\":").append(vis[k]).append(",\"u\":").append(used[k])
                        .append(",\"cn\":").append(used[k] > 0 ? Math.round(cn[k] / used[k]) : 0).append('}');
            }
            sb.append("]}");
            final String js = "window.__gnss&&window.__gnss(" + sb + ")";
            runOnUiThread(() -> {
                if (web != null) web.evaluateJavascript(js, null);
            });
        }

        @Override
        public void onStopped() {
            runOnUiThread(() -> {
                if (web != null) web.evaluateJavascript("window.__gnss&&window.__gnss(null)", null);
            });
        }
    };

    // keeps the satellite receiver running while the page tracks the position (status callbacks need it)
    private final LocationListener keepAlive = new LocationListener() {
        @Override
        public void onLocationChanged(Location location) {
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

    private void startGnss() {
        if (!gnssWanted || gnssOn) return;
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try {
            if (lm == null) lm = (LocationManager) getSystemService(LOCATION_SERVICE);
            if (lm == null) return;
            lm.registerGnssStatusCallback(gnssCb, new Handler(Looper.getMainLooper()));
            if (lm.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 0f, keepAlive, Looper.getMainLooper());
            }
            gnssOn = true;
        } catch (SecurityException | IllegalArgumentException ignored) {
        }
    }

    private void stopGnss() {
        if (!gnssOn || lm == null) return;
        try {
            lm.unregisterGnssStatusCallback(gnssCb);
            lm.removeUpdates(keepAlive);
        } catch (Exception ignored) {
        }
        gnssOn = false;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        web = new WebView(this);
        web.setBackgroundColor(0xFF0F1511);
        setContentView(web);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setGeolocationEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " UtSzelveny/0.8.4");

        web.addJavascriptInterface(new Bridge(), "AndroidBridge");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if (HOST.equals(uri.getHost())) return false;
                // külső hivatkozás (pl. OpenStreetMap copyright) → böngészőben
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (ActivityNotFoundException ignored) {
                }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                if (hasLocationPermission()) {
                    callback.invoke(origin, true, false);
                } else {
                    pendingCallback = callback;
                    pendingOrigin = origin;
                    requestPermissions(new String[]{
                            Manifest.permission.ACCESS_FINE_LOCATION,
                            Manifest.permission.ACCESS_COARSE_LOCATION}, REQ_LOCATION);
                }
            }

            // getUserMedia() of the page (Fotó tab): only the camera, only for our own page
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> handleCameraRequest(request));
            }

            @Override
            public void onPermissionRequestCanceled(PermissionRequest request) {
                if (request == pendingCamera) pendingCamera = null;
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(START_URL);
        }
    }

    private void handleCameraRequest(PermissionRequest request) {
        boolean video = false;
        for (String r : request.getResources()) {
            if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(r)) video = true;
        }
        Uri origin = request.getOrigin();
        if (!video || origin == null || !HOST.equals(origin.getHost())) {
            request.deny();
            return;
        }
        if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
        } else {
            if (pendingCamera != null) pendingCamera.deny();
            pendingCamera = request;
            requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_CAMERA);
        }
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                || checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        boolean granted = grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        if (requestCode == REQ_LOCATION && pendingCallback != null) {
            pendingCallback.invoke(pendingOrigin, hasLocationPermission(), false);
            pendingCallback = null;
            pendingOrigin = null;
            startGnss();
        } else if (requestCode == REQ_CAMERA && pendingCamera != null) {
            if (granted) pendingCamera.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
            else pendingCamera.deny();
            pendingCamera = null;
        } else if (requestCode == REQ_STORAGE) {
            Runnable job = granted ? pendingStorageJob : pendingStorageFail;
            pendingStorageJob = null;
            pendingStorageFail = null;
            if (job != null) job.run();
        }
    }

    /* ---------- JS bridge: window.AndroidBridge ---------- */

    /** Sends the result of a bridge call back to the page: window.__nativeDone(id, ok, msg, uri). */
    private void done(String id, boolean ok, String msg, String uri) {
        final String js = "window.__nativeDone&&window.__nativeDone(" + JSONObject.quote(id) + "," + ok + ","
                + JSONObject.quote(msg == null ? "" : msg) + "," + JSONObject.quote(uri == null ? "" : uri) + ")";
        runOnUiThread(() -> {
            if (web != null) web.evaluateJavascript(js, null);
        });
    }

    /** Status and navigation bar colours for the page theme (Material 3 surface colours). */
    @SuppressWarnings("deprecation")
    private void applyBars(boolean light) {
        android.view.Window w = getWindow();
        w.setStatusBarColor(light ? 0xFFF6FBF4 : 0xFF0F1511);
        w.setNavigationBarColor(light ? 0xFFEAEFE9 : 0xFF1B211D);
        if (web != null) web.setBackgroundColor(light ? 0xFFF6FBF4 : 0xFF0F1511);
        android.view.View d = w.getDecorView();
        int bits = android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        int f = d.getSystemUiVisibility();
        d.setSystemUiVisibility(light ? (f | bits) : (f & ~bits));
    }

    private class Bridge {
        /** The page switched between the dark and light theme ("dark" / "light"). */
        @JavascriptInterface
        public void setTheme(final String theme) {
            runOnUiThread(() -> applyBars("light".equals(theme)));
        }

        /** Saves a base64 file: image/* → Pictures/ÚtSzelvény (gallery), anything else → Download/ÚtSzelvény. */
        @JavascriptInterface
        public void saveFile(String b64, final String name, final String mime, final String id) {
            final byte[] data;
            try {
                data = Base64.decode(b64, Base64.DEFAULT);
            } catch (IllegalArgumentException e) {
                done(id, false, "hibás adat", "");
                return;
            }
            final Runnable job = () -> new Thread(() -> {
                try {
                    Uri u = writeFile(data, safeName(name), mime);
                    done(id, true, "", u.toString());
                } catch (Exception e) {
                    done(id, false, String.valueOf(e.getMessage()), "");
                }
            }).start();
            if (Build.VERSION.SDK_INT >= 29
                    || checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED) {
                job.run();
                return;
            }
            // Android 8–9: storage permission needed for the public folders
            runOnUiThread(() -> {
                if (pendingStorageJob != null) {
                    done(id, false, "engedélykérés folyamatban", "");
                    return;
                }
                pendingStorageJob = job;
                pendingStorageFail = () -> done(id, false, "nincs tárhely-engedély", "");
                requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_STORAGE);
            });
        }

        /** The page started / stopped location tracking: satellite status on / off. */
        @JavascriptInterface
        public void gnssStart() {
            runOnUiThread(() -> {
                gnssWanted = true;
                startGnss();
            });
        }

        @JavascriptInterface
        public void gnssStop() {
            runOnUiThread(() -> {
                gnssWanted = false;
                stopGnss();
            });
        }

        /** Opens the Android share sheet for a file saved before (content:// uri from saveFile). */
        @JavascriptInterface
        public void shareFile(final String uri, final String mime, final String id) {
            runOnUiThread(() -> {
                try {
                    Intent send = new Intent(Intent.ACTION_SEND);
                    send.setType(mime);
                    send.putExtra(Intent.EXTRA_STREAM, Uri.parse(uri));
                    send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    Intent chooser = Intent.createChooser(send, "Megosztás");
                    chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(chooser);
                    done(id, true, "", uri);
                } catch (Exception e) {
                    done(id, false, String.valueOf(e.getMessage()), "");
                }
            });
        }
    }

    private static String safeName(String n) {
        String s = n == null ? "" : n.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        return s.isEmpty() ? "UtSzelveny_" + System.currentTimeMillis() : s;
    }

    private Uri writeFile(byte[] data, String name, String mime) throws IOException {
        boolean image = mime != null && mime.startsWith("image/");
        if (Build.VERSION.SDK_INT >= 29) {
            ContentResolver cr = getContentResolver();
            Uri coll = image
                    ? MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
                    : MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
            ContentValues v = new ContentValues();
            v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
            v.put(MediaStore.MediaColumns.RELATIVE_PATH,
                    (image ? Environment.DIRECTORY_PICTURES : Environment.DIRECTORY_DOWNLOADS) + "/" + FOLDER);
            v.put(MediaStore.MediaColumns.IS_PENDING, 1);
            Uri uri = cr.insert(coll, v);
            if (uri == null) throw new IOException("a fájl nem hozható létre");
            try (OutputStream os = cr.openOutputStream(uri)) {
                if (os == null) throw new IOException("a fájl nem írható");
                os.write(data);
            } catch (IOException e) {
                cr.delete(uri, null, null);
                throw e;
            }
            v.clear();
            v.put(MediaStore.MediaColumns.IS_PENDING, 0);
            cr.update(uri, v, null, null);
            return uri;
        }
        // Android 8–9: public folder + media scanner (gives a shareable content:// uri)
        File dir = new File(Environment.getExternalStoragePublicDirectory(
                image ? Environment.DIRECTORY_PICTURES : Environment.DIRECTORY_DOWNLOADS), FOLDER);
        if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("a mappa nem hozható létre");
        File f = new File(dir, name);
        int dot = name.lastIndexOf('.');
        for (int i = 1; f.exists(); i++) {
            f = new File(dir, dot > 0 ? name.substring(0, dot) + " (" + i + ")" + name.substring(dot) : name + " (" + i + ")");
        }
        try (FileOutputStream os = new FileOutputStream(f)) {
            os.write(data);
        }
        final Uri[] out = new Uri[1];
        final CountDownLatch latch = new CountDownLatch(1);
        MediaScannerConnection.scanFile(this, new String[]{f.getAbsolutePath()}, new String[]{mime},
                (path, uri) -> {
                    out[0] = uri;
                    latch.countDown();
                });
        try {
            latch.await(5, TimeUnit.SECONDS);
        } catch (InterruptedException ignored) {
        }
        if (out[0] == null) throw new IOException("mentve, de a galéria nem látja: " + f.getAbsolutePath());
        return out[0];
    }

    /** Back button: the page closes its topmost layer first (photo viewer, settings, map panel, other tab); the app closes only on the Pozíció page. */
    @Override
    public void onBackPressed() {
        if (web == null) {
            super.onBackPressed();
            return;
        }
        web.evaluateJavascript("(window.__back&&window.__back())?1:0", v -> {
            if ("1".equals(v)) return;
            if (web != null && web.canGoBack()) web.goBack();
            else super.onBackPressed();
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        if (web != null) web.saveState(outState);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) {
            web.onResume();
            web.evaluateJavascript("window.__appResume&&window.__appResume()", null);
        }
        startGnss();
    }

    @Override
    protected void onPause() {
        stopGnss();
        if (web != null) {
            // release the camera while the app is in the background
            web.evaluateJavascript("window.__appPause&&window.__appPause()", null);
            web.onPause();
        }
        super.onPause();
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
