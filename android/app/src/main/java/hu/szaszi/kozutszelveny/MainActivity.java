package hu.szaszi.kozutszelveny;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
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
 * GPS- és kamera-engedélyt kér, ébren tartja a képernyőt, és a "AndroidBridge"
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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        web = new WebView(this);
        web.setBackgroundColor(0xFF16181C);
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
        s.setUserAgentString(s.getUserAgentString() + " UtSzelveny/0.6.1");

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

    private class Bridge {
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

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
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
    }

    @Override
    protected void onPause() {
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
