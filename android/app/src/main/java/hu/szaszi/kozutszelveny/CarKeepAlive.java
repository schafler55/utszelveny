package hu.szaszi.kozutszelveny;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;

/**
 * Előtérszolgáltatás (helymeghatározás típusú), amíg az ÚtSzelvény az autó kijelzőjén fut:
 * így a zárolt telefonon is kap GNSS-pozíciót. Nem csinál mást, csak egy értesítést mutat.
 */
public class CarKeepAlive extends Service {

    private static final String CH = "car";
    private static final int ID = 7;

    static void start(Context c) {
        if (c.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try {
            c.startForegroundService(new Intent(c, CarKeepAlive.class));
        } catch (Exception ignored) {
            // not allowed right now (background start limits): the car screen still works while the app may use location
        }
    }

    static void stop(Context c) {
        try {
            c.stopService(new Intent(c, CarKeepAlive.class));
        } catch (Exception ignored) {
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        try {
            NotificationManager nm = getSystemService(NotificationManager.class);
            if (nm != null && nm.getNotificationChannel(CH) == null) {
                nm.createNotificationChannel(new NotificationChannel(CH, "Android Auto", NotificationManager.IMPORTANCE_LOW));
            }
            Notification n = new Notification.Builder(this, CH)
                    .setSmallIcon(R.mipmap.ic_launcher)
                    .setContentTitle("ÚtSzelvény az autó kijelzőjén")
                    .setContentText("GNSS-követés fut")
                    .setOngoing(true)
                    .build();
            if (Build.VERSION.SDK_INT >= 29) startForeground(ID, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION);
            else startForeground(ID, n);
        } catch (Exception e) {
            stopSelf();
        }
        return START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
