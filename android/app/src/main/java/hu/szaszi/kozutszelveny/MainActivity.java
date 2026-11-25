package hu.szaszi.kozutszelveny;

import android.Manifest;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ActivityNotFoundException;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
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
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.KeyEvent;
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
 * ÚtSzelvény – Android wrapper.
 * The whole app is assets/index.html (the same file as the web app); this class only shows it,
 * asks for the location (GNSS) and camera permissions, passes the satellite status to the page, keeps the screen on,
 * and through the "AndroidBridge" JS bridge saves files (photo → the folder chosen in the Fotó settings, by default
 * DCIM/ÚtSzelvény; CSV → Download), shares them and copies text to the clipboard.
 * HUD mode: full screen, maximum brightness and a locked orientation (setHud).
 * The page is loaded from https://appassets.androidplatform.net (a secure context), so geolocation and the camera
 * work, and OpenStreetMap gets a Referer header.
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + HOST + "/assets/index.html";
    private static final String FOLDER = "ÚtSzelvény";
    private static final int REQ_LOCATION = 1;
    private static final int REQ_CAMERA = 2;
    private static final int REQ_STORAGE = 3;
    private static final int REQ_TREE = 4;

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
        // OpenStreetMap tile usage policy: an app must identify itself (name/version + project URL)
        s.setUserAgentString(s.getUserAgentString() + " UtSzelveny/1.2.2 (+https://github.com/schafler55/utszelveny)");

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
                // any other link (e.g. OpenStreetMap copyright, Google Street View) → the browser / the app that handles it
                // every failure is caught (no app for it, a file:// link that Android refuses, …): the app stays open
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception ignored) {
                }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                // the location only for our own page, like the camera (security audit L4)
                Uri o = origin == null ? null : Uri.parse(origin);
                if (o == null || !"https".equals(o.getScheme()) || !HOST.equals(o.getHost())) {
                    callback.invoke(origin, false, false);
                    return;
                }
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
        barsLight = light;
        if (hudOn) return;   // HUD mode: bars stay hidden and black; restored on exit
        android.view.Window w = getWindow();
        w.setStatusBarColor(light ? 0xFFE5EBE4 : 0xFF0F1511);
        w.setNavigationBarColor(light ? 0xFFE5EBE4 : 0xFF1B211D);
        if (web != null) web.setBackgroundColor(light ? 0xFFE5EBE4 : 0xFF0F1511);
        android.view.View d = w.getDecorView();
        int bits = android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        int f = d.getSystemUiVisibility();
        d.setSystemUiVisibility(light ? (f | bits) : (f & ~bits));
    }

    /* ---------- HUD mode: full screen, black bars, max brightness, rotation locked ---------- */
    private boolean barsLight = false;
    private boolean hudOn = false;
    private boolean hudMax = false;

    @SuppressWarnings("deprecation")
    private void applyHud() {
        android.view.Window w = getWindow();
        WindowManager.LayoutParams lp = w.getAttributes();
        lp.screenBrightness = hudOn && hudMax ? 1f : WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;
        w.setAttributes(lp);
        android.view.View d = w.getDecorView();
        int imm = android.view.View.SYSTEM_UI_FLAG_FULLSCREEN
                | android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION;
        int f = d.getSystemUiVisibility();
        if (hudOn) {
            w.setStatusBarColor(0xFF000000);
            w.setNavigationBarColor(0xFF000000);
            if (web != null) web.setBackgroundColor(0xFF000000);
            d.setSystemUiVisibility(f | imm);
            // a phone lying flat rotates at random; the page turns the picture itself
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LOCKED);
        } else {
            d.setSystemUiVisibility(f & ~imm);
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
            applyBars(barsLight);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus && hudOn) applyHud();   // immersive mode is lost after dialogs / the notification shade
    }

    /* ---------- volume keys as the shutter while the Fotó camera is live (set by the page) ---------- */
    private volatile boolean volShutter = false;

    @Override
    public boolean dispatchKeyEvent(KeyEvent e) {
        int k = e.getKeyCode();
        if (volShutter && web != null && (k == KeyEvent.KEYCODE_VOLUME_UP || k == KeyEvent.KEYCODE_VOLUME_DOWN)) {
            // one photo per press (no burst when held); the key is consumed: no volume change, no volume panel
            if (e.getAction() == KeyEvent.ACTION_DOWN && e.getRepeatCount() == 0)
                web.evaluateJavascript("window.__volShot&&window.__volShot()", null);
            return true;
        }
        return super.dispatchKeyEvent(e);
    }

    private class Bridge {
        /** First-start notice → Kilépés: closes the app (and removes it from the recent apps list). */
        @JavascriptInterface
        public void exitApp() {
            runOnUiThread(() -> finishAndRemoveTask());
        }

        /** Fotó page: camera live and the option on → the volume keys take the photo. */
        @JavascriptInterface
        public void setVolShutter(final boolean on) {
            volShutter = on;
        }

        /** Képernyő ébren tartása switch (and HUD mode): keep the screen on, on every page of the app. */
        @JavascriptInterface
        public void setKeepScreen(final boolean on) {
            runOnUiThread(() -> {
                if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            });
        }

        /** HUD mode on / off; max = full screen brightness while it is on. */
        @JavascriptInterface
        public void setHud(final boolean on, final boolean max) {
            runOnUiThread(() -> {
                hudOn = on;
                hudMax = max;
                applyHud();
            });
        }

        /** Long press on a coordinate: copies the text to the system clipboard (label = "WGS84" / "EOV"). */
        @JavascriptInterface
        public void copyText(final String label, final String text) {
            // on the UI thread: the clipboard service may create a Handler, which needs a Looper
            runOnUiThread(() -> {
                try {
                    ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                    if (cm != null) cm.setPrimaryClip(ClipData.newPlainText(label, text));
                } catch (Exception ignored) {
                }
            });
        }

        /** The page switched between the dark and light theme ("dark" / "light"). */
        @JavascriptInterface
        public void setTheme(final String theme) {
            runOnUiThread(() -> applyBars("light".equals(theme)));
        }

        /** Saves a base64 file: image/* → the photo folder (default DCIM/ÚtSzelvény, see setPhotoDir), anything else → Download. */
        @JavascriptInterface
        public void saveFile(final String b64, final String name, final String mime, final String id) {
            // returns at once: decoding and writing run on a worker thread (the page waits for this call otherwise)
            final Runnable job = () -> new Thread(() -> {
                final byte[] data;
                try {
                    data = Base64.decode(b64, Base64.DEFAULT);
                } catch (IllegalArgumentException e) {
                    done(id, false, "hibás adat", "");
                    return;
                }
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

        /** Photo folder: dcim = DCIM/ÚtSzelvény (default), pictures = Pictures/ÚtSzelvény, custom = folder picked with pickPhotoDir. */
        @JavascriptInterface
        public void setPhotoDir(String key) {
            prefs().edit().putString("photoDir", key == null ? "dcim" : key).apply();
        }

        /** Readable name of the picked folder, "" when none (or its permission is gone). */
        @JavascriptInterface
        public String photoDirLabel() {
            Uri t = photoTree();
            return t == null ? "" : treeLabel(t);
        }

        /** Opens the Android folder picker; the result comes back via __nativeDone (msg = folder name). */
        @JavascriptInterface
        public void pickPhotoDir(final String id) {
            runOnUiThread(() -> {
                if (pendingTreeId != null) {
                    done(id, false, "a mappaválasztó már nyitva van", "");
                    return;
                }
                try {
                    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
                    i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                            | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
                    pendingTreeId = id;
                    startActivityForResult(i, REQ_TREE);
                } catch (ActivityNotFoundException e) {
                    pendingTreeId = null;
                    done(id, false, "nincs mappaválasztó a telefonon", "");
                }
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

    /* ---------- photo folder ---------- */
    private String pendingTreeId = null;

    private SharedPreferences prefs() {
        return getSharedPreferences("utszelveny", MODE_PRIVATE);
    }

    /** The picked folder, if the app still holds write permission to it. */
    private Uri photoTree() {
        String t = prefs().getString("photoTree", "");
        if (t.isEmpty()) return null;
        Uri u = Uri.parse(t);
        for (android.content.UriPermission p : getContentResolver().getPersistedUriPermissions()) {
            if (p.getUri().equals(u) && p.isWritePermission()) return u;
        }
        return null;
    }

    /** "primary:DCIM/Munka" → "DCIM / Munka"; other volumes → "SD-kártya: …". */
    private static String treeLabel(Uri tree) {
        String d;
        try {
            d = DocumentsContract.getTreeDocumentId(tree);
        } catch (Exception e) {
            return "választott mappa";
        }
        int c = d.indexOf(':');
        String vol = c > 0 ? d.substring(0, c) : "";
        String path = (c >= 0 ? d.substring(c + 1) : d).replace("/", " / ");
        if ("primary".equals(vol)) return path.isEmpty() ? "Belső tárhely" : path;
        return "SD-kártya" + (path.isEmpty() ? "" : ": " + path);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_TREE) return;
        String id = pendingTreeId;
        pendingTreeId = null;
        if (id == null) return;
        Uri tree = resultCode == RESULT_OK && data != null ? data.getData() : null;
        if (tree == null) {
            done(id, false, "", "");   // cancelled: the page keeps the previous choice
            return;
        }
        int fl = Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION;
        try {
            getContentResolver().takePersistableUriPermission(tree, fl);
            String old = prefs().getString("photoTree", "");
            if (!old.isEmpty() && !old.equals(tree.toString())) {
                try {
                    getContentResolver().releasePersistableUriPermission(Uri.parse(old), fl);
                } catch (Exception ignored) {
                }
            }
            prefs().edit().putString("photoTree", tree.toString()).putString("photoDir", "custom").apply();
            done(id, true, treeLabel(tree), tree.toString());
        } catch (Exception e) {
            done(id, false, String.valueOf(e.getMessage()), "");
        }
    }

    /** Writes into the folder picked with the Android folder picker. */
    private Uri writeTree(Uri tree, byte[] data, String name, String mime) throws IOException {
        ContentResolver cr = getContentResolver();
        Uri doc;
        try {
            Uri dir = DocumentsContract.buildDocumentUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree));
            doc = DocumentsContract.createDocument(cr, dir, mime, name);
        } catch (Exception e) {
            throw new IOException("a választott mappa nem érhető el – válassz újat a Fotó beállításokban");
        }
        if (doc == null) throw new IOException("a fájl nem hozható létre a választott mappában");
        try (OutputStream os = cr.openOutputStream(doc)) {
            if (os == null) throw new IOException("a fájl nem írható");
            os.write(data);
        } catch (IOException e) {
            try {
                DocumentsContract.deleteDocument(cr, doc);
            } catch (Exception ignored) {
            }
            throw e;
        }
        return doc;
    }

    private static String safeName(String n) {
        String s = n == null ? "" : n.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        return s.isEmpty() ? "UtSzelveny_" + System.currentTimeMillis() : s;
    }

    private Uri writeFile(byte[] data, String name, String mime) throws IOException {
        boolean image = mime != null && mime.startsWith("image/");
        // photos: folder chosen in the Fotó settings (default and any other key, e.g. an old "camera" choice: DCIM/ÚtSzelvény);
        // anything else (CSV): Download
        String key = image ? prefs().getString("photoDir", "dcim") : "";
        if ("custom".equals(key)) {
            Uri tree = photoTree();
            if (tree != null) return writeTree(tree, data, name, mime);
            key = "dcim";
        }
        String base = !image ? Environment.DIRECTORY_DOWNLOADS
                : "pictures".equals(key) ? Environment.DIRECTORY_PICTURES : Environment.DIRECTORY_DCIM;
        String sub = image ? FOLDER : "";
        if (Build.VERSION.SDK_INT >= 29) {
            ContentResolver cr = getContentResolver();
            Uri coll = image
                    ? MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
                    : MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
            ContentValues v = new ContentValues();
            v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
            v.put(MediaStore.MediaColumns.RELATIVE_PATH, sub.isEmpty() ? base : base + "/" + sub);
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
        File dir = sub.isEmpty() ? Environment.getExternalStoragePublicDirectory(base) : new File(Environment.getExternalStoragePublicDirectory(base), sub);
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
        if (hudOn) applyHud();
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
