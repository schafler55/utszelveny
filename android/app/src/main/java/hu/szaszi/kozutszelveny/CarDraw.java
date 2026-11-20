package hu.szaszi.kozutszelveny;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.Typeface;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * Az autós kijelző rajzolása ("B · Material 3 kártyák" terv).
 * Balra a fő kártya (útszámtábla, km+m, irány, pontosság, út neve), jobbra a sebességkártya
 * (korlátozás tábla, saját sebesség, helységnévtábla / Külterület, szakasz jellege, következő változás).
 * Nincs jel / úthálózaton kívül / Budapest: piros vagy narancs kártya, mint a telefonon.
 * Méretek a 1280×720-as terv képpontjaiban, k-val szorozva (k = a látható terület / a terv mérete).
 * Színek: az index.html Material 3 tokenjei (sötét téma és a "Fehér kártyák" világos téma).
 */
final class CarDraw {

    private CarDraw() {
    }

    static final class Pal {
        int bg, hero, heroOn, heroCh, heroSub, pill, card, on, onv, ok, mid, bad, over;
        int red, redOn, redSub, redIco, redIcoFg, org, orgOn, orgSub, orgIco, orgIcoFg;
        int kuBg, kuOn, buBg, buOn, naBg, naOn;
    }

    private static final Pal DARK = new Pal();
    private static final Pal LIGHT = new Pal();

    static {
        Pal d = DARK;
        d.bg = 0xFF0F1511; d.hero = 0xFF12452B; d.heroOn = 0xFFCDEFD7; d.heroCh = 0xFFF1FFF4; d.heroSub = 0xFFA7CFB3;
        d.pill = 0xFF1E5A3A; d.card = 0xFF1B211D; d.on = 0xFFDEE4DD; d.onv = 0xFFBFC9C0;
        d.ok = 0xFF6BE28F; d.mid = 0xFFF2C46D; d.bad = 0xFFFFB4AB; d.over = 0xFFFF6B4A;
        d.red = 0xFF4D1D1A; d.redOn = 0xFFFFDAD6; d.redSub = 0xFFF2B8B2; d.redIco = 0xFF6E2A25; d.redIcoFg = 0xFFFFB4AB;
        d.org = 0xFF4F2D0C; d.orgOn = 0xFFFFDCC2; d.orgSub = 0xFFF5BF95; d.orgIco = 0xFF6E4119; d.orgIcoFg = 0xFFFFB77C;
        d.kuBg = 0xFF374B3D; d.kuOn = 0xFFD2E8D6; d.buBg = 0xFF4A3A10; d.buOn = 0xFFFFE6B0; d.naBg = 0xFF303632; d.naOn = 0xFFBFC9C0;

        Pal l = LIGHT;
        l.bg = 0xFFE5EBE4; l.hero = 0xFFB0F1C3; l.heroOn = 0xFF002111; l.heroCh = 0xFF002111; l.heroSub = 0xFF24452F;
        l.pill = 0xFF95DDAB; l.card = 0xFFFFFFFF; l.on = 0xFF0F140F; l.onv = 0xFF2E352F;
        l.ok = 0xFF0B7A3A; l.mid = 0xFF7A5300; l.bad = 0xFFBA1A1A; l.over = 0xFFC62828;
        l.red = 0xFFFFDAD6; l.redOn = 0xFF410002; l.redSub = 0xFF73302B; l.redIco = 0xFFFFB4AB; l.redIcoFg = 0xFF93000A;
        l.org = 0xFFFFDCC2; l.orgOn = 0xFF2E1500; l.orgSub = 0xFF6E3D10; l.orgIco = 0xFFFFB77C; l.orgIcoFg = 0xFF8A4500;
        l.kuBg = 0xFFA3DBB4; l.kuOn = 0xFF00210F; l.buBg = 0xFFFFDEA6; l.buOn = 0xFF271900; l.naBg = 0xFFDFE6DE; l.naOn = 0xFF2E352F;
    }

    private static final Typeface T_REG = Typeface.create("sans-serif", Typeface.NORMAL);
    private static final Typeface T_MED = Typeface.create("sans-serif-medium", Typeface.NORMAL);
    private static final Typeface T_BOLD = Typeface.create("sans-serif", Typeface.BOLD);
    private static final Typeface T_COND = Typeface.create("sans-serif-condensed", Typeface.BOLD);

    static void draw(Canvas c, int w, int h, Rect a, JSONObject o, boolean dark) {
        Pal p = dark ? DARK : LIGHT;
        c.drawColor(p.bg);
        float k = Math.min(a.height() / 672f, a.width() / 1064f);
        k = Math.max(k, 0.3f);
        float pad = 20 * k;
        RectF area = new RectF(a.left + pad, a.top + pad, a.right - pad, a.bottom - pad);
        String st = o == null ? "search" : o.optString("st", "search");
        boolean ok = "ok".equals(st);
        boolean card = ok && o.optBoolean("spdCard", false);
        boolean narrow = area.width() < area.height() * 1.3f;
        RectF hero = area, spd = null;
        if (card && !narrow) {
            float cw = Math.min(400 * k, area.width() * 0.42f);
            hero = new RectF(area.left, area.top, area.right - cw - pad, area.bottom);
            spd = new RectF(area.right - cw, area.top, area.right, area.bottom);
        }
        if (ok) drawHero(c, hero, o, p);
        else drawState(c, hero, o, st, p);
        if (spd != null) drawSpeed(c, spd, o, p, k);
        else if (card) {   // narrow screen: only the speed-limit sign in the corner of the main tile
            float kh = Math.min(hero.height() / 672f, hero.width() / 600f);
            float sz = 110 * kh;
            if (o.has("lim") && !o.isNull("lim")) {
                drawLimit(c, hero.right - 24 * kh - sz, hero.bottom - 24 * kh - sz, sz, String.valueOf(o.optInt("lim")));
            }
        }
    }

    // ---------- main tile ----------
    private static void drawHero(Canvas c, RectF r, JSONObject o, Pal p) {
        float k = Math.min(r.height() / 672f, r.width() / 600f);
        Paint f = fill(p.hero);
        c.drawRoundRect(r, 32 * k, 32 * k, f);
        int dir = o.optInt("dir", 0);
        if (dir != 0) pill(c, r.left + 20 * k, r.top + 20 * k, dir > 0 ? "↑ növekvő" : "↓ csökkenő", 0, p.pill, p.heroOn, k, false);
        String q = o.optString("q", "");
        if (!q.isEmpty()) {
            String qc = o.optString("qc", "");
            int dot = "good".equals(qc) ? p.ok : "mid".equals(qc) ? p.mid : "bad".equals(qc) ? p.bad : p.onv;
            pill(c, r.right - 20 * k, r.top + 20 * k, q, dot, p.pill, p.heroOn, k, true);
        }

        String num = o.optString("num", "");
        String ch = o.optString("ch", "");
        String name = o.optString("name", "");
        String sub = o.optString("sub", "");
        float top = r.top + 76 * k, bottom = r.bottom - 24 * k, avail = bottom - top;
        float maxW = r.width() - 48 * k;

        Paint chP = text(T_COND, 150 * k, p.heroCh, Paint.Align.CENTER);
        float chS = 150 * k;
        float tw = chP.measureText(ch);
        if (tw > maxW) {
            chS = chS * maxW / tw;
            chP.setTextSize(chS);
        }
        float shieldH = 111 * k, nameS = 28 * k, subS = 20 * k;
        float total = shieldH + 12 * k + chS * 0.74f + 22 * k + (name.isEmpty() ? 0 : nameS * 1.25f) + subS * 1.3f;
        if (total > avail) {
            float s = avail / total;
            shieldH *= s; chS *= s; nameS *= s; subS *= s; total = avail;
            chP.setTextSize(chS);
        }
        float cx = r.centerX();
        float y = top + (avail - total) / 2;
        drawShield(c, cx, y, shieldH, num, o.optInt("kut", 0));
        y += shieldH + 12 * k + chS * 0.74f;
        c.drawText(ch, cx, y, chP);
        y += 22 * k;
        if (!name.isEmpty()) {
            Paint nP = text(T_MED, nameS, p.heroOn, Paint.Align.CENTER);
            c.drawText(ellipsize(name, nP, maxW), cx, y + nameS * 0.95f, nP);
            y += nameS * 1.25f;
        }
        Paint sP = text(T_REG, subS, p.heroSub, Paint.Align.CENTER);
        c.drawText(ellipsize(sub, sP, maxW), cx, y + subS * 0.95f, sP);
    }

    // ---------- no fix / off the network / Budapest ----------
    private static void drawState(Canvas c, RectF r, JSONObject o, String st, Pal p) {
        float k = Math.min(r.height() / 672f, r.width() / 600f);
        boolean red = "off".equals(st) || "lost".equals(st) || "noperm".equals(st);
        int bg = red ? p.red : p.org, fg = red ? p.redOn : p.orgOn, sub = red ? p.redSub : p.orgSub;
        int ico = red ? p.redIco : p.orgIco, icoFg = red ? p.redIcoFg : p.orgIcoFg;
        c.drawRoundRect(r, 32 * k, 32 * k, fill(bg));
        String t = o == null ? "ÚtSzelvény indul…" : o.optString("t", "");
        String s = o == null ? "" : o.optString("s", "");
        Paint tP = text(T_MED, 44 * k, fg, Paint.Align.CENTER);
        Paint sP = text(T_REG, 24 * k, sub, Paint.Align.CENTER);
        float maxW = r.width() - 80 * k;
        List<String> lines = wrap(s, sP, maxW, 3);
        float icoR = 44 * k;
        float total = icoR * 2 + 28 * k + 44 * k + 16 * k + lines.size() * 24 * k * 1.35f;
        float y = r.centerY() - total / 2;
        float cx = r.centerX(), cy = y + icoR;
        c.drawCircle(cx, cy, icoR, fill(ico));
        Paint g = stroke(icoFg, 3.2f * k);
        if ("bp".equals(st)) {   // city: three buildings
            c.drawRect(cx - 17 * k, cy - 4 * k, cx - 6 * k, cy + 16 * k, g);
            c.drawRect(cx - 6 * k, cy - 16 * k, cx + 6 * k, cy + 16 * k, g);
            c.drawRect(cx + 6 * k, cy - 8 * k, cx + 17 * k, cy + 16 * k, g);
        } else {                 // location pin
            Path pin = new Path();
            pin.addCircle(cx, cy - 5 * k, 6 * k, Path.Direction.CW);
            c.drawPath(pin, g);
            Path drop = new Path();
            drop.moveTo(cx, cy + 18 * k);
            drop.cubicTo(cx - 6 * k, cy + 11 * k, cx - 15 * k, cy + 3 * k, cx - 15 * k, cy - 5 * k);
            drop.cubicTo(cx - 15 * k, cy - 14 * k, cx - 8 * k, cy - 20 * k, cx, cy - 20 * k);
            drop.cubicTo(cx + 8 * k, cy - 20 * k, cx + 15 * k, cy - 14 * k, cx + 15 * k, cy - 5 * k);
            drop.cubicTo(cx + 15 * k, cy + 3 * k, cx + 6 * k, cy + 11 * k, cx, cy + 18 * k);
            c.drawPath(drop, g);
            if ("off".equals(st) || "noperm".equals(st)) c.drawLine(cx - 20 * k, cy - 22 * k, cx + 20 * k, cy + 22 * k, g);
            if ("search".equals(st)) {
                Paint arc = stroke(icoFg, 4 * k);
                c.drawArc(new RectF(cx - icoR + 3 * k, cy - icoR + 3 * k, cx + icoR - 3 * k, cy + icoR - 3 * k), -90, 110, false, arc);
            }
        }
        y += icoR * 2 + 28 * k;
        c.drawText(ellipsize(t, tP, maxW), cx, y + 44 * k * 0.8f, tP);
        y += 44 * k + 16 * k;
        for (String l : lines) {
            c.drawText(l, cx, y + 24 * k * 0.95f, sP);
            y += 24 * k * 1.35f;
        }
    }

    // ---------- speed card ----------
    private static void drawSpeed(Canvas c, RectF r, JSONObject o, Pal p, float k0) {
        float k = Math.min(k0, r.width() / 400f);
        c.drawRoundRect(r, 32 * k, 32 * k, fill(p.card));
        float pad = 28 * k, x0 = r.left + pad, inner = r.width() - 2 * pad;
        float y = r.top + pad;
        Paint lab = text(T_MED, 20 * k, p.onv, Paint.Align.LEFT);
        c.drawText("Sebességkorlátozás", x0, y + 20 * k * 0.8f, lab);
        y += 20 * k + 20 * k;

        boolean both = o.has("limInc") && o.has("limDec");
        float rowH, signsRight;
        if (both) {
            float sz = 88 * k;
            drawLimit(c, x0, y, sz, String.valueOf(o.optInt("limInc")));
            drawLimit(c, x0 + sz + 12 * k, y, sz, String.valueOf(o.optInt("limDec")));
            Paint sm = text(T_REG, 15 * k, p.onv, Paint.Align.CENTER);
            c.drawText("↑ növekvő", x0 + sz / 2, y + sz + 18 * k, sm);
            c.drawText("↓ csökkenő", x0 + sz * 1.5f + 12 * k, y + sz + 18 * k, sm);
            rowH = sz + 24 * k;
            signsRight = x0 + sz * 2 + 12 * k;
        } else {
            float sz = 132 * k;
            drawLimit(c, x0, y, sz, o.isNull("lim") || !o.has("lim") ? "–" : String.valueOf(o.optInt("lim")));
            rowH = sz;
            signsRight = x0 + sz;
        }
        // own speed
        float sx = signsRight + 18 * k, mid = y + (both ? 88 * k : rowH) / 2;
        Paint sl = text(T_REG, 18 * k, p.onv, Paint.Align.LEFT);
        c.drawText("Sebességed", sx, mid - 18 * k, sl);
        boolean hasSpd = o.has("spd") && !o.isNull("spd");
        int spd = o.optInt("spd", 0);
        int lim = o.optInt("lim", 0);
        boolean over = hasSpd && o.has("lim") && !o.isNull("lim") && !both && spd > lim + 3;
        Paint sv = text(T_BOLD, 52 * k, over ? p.over : p.on, Paint.Align.LEFT);
        String v = hasSpd ? String.valueOf(spd) : "–";
        c.drawText(v, sx, mid + 34 * k, sv);
        Paint su = text(T_MED, 22 * k, p.onv, Paint.Align.LEFT);
        c.drawText(" km/h", sx + sv.measureText(v), mid + 34 * k, su);
        y += rowH + 20 * k;

        // town sign or area label
        String town = o.optString("town", "");
        if (!town.isEmpty()) {
            y += drawTown(c, x0, y, inner, town, k) + 16 * k;
        } else {
            String area = o.optString("area", "na");
            String t = "bu".equals(area) ? "Belterület" : "ku".equals(area) ? "Külterület" : "Nincs adat";
            int bg = "bu".equals(area) ? p.buBg : "ku".equals(area) ? p.kuBg : p.naBg;
            int fg = "bu".equals(area) ? p.buOn : "ku".equals(area) ? p.kuOn : p.naOn;
            Paint tp = text(T_BOLD, 26 * k, fg, Paint.Align.LEFT);
            float cw = tp.measureText(t) + 28 * k, chH = 48 * k;
            c.drawRoundRect(new RectF(x0, y, x0 + cw, y + chH), 8 * k, 8 * k, fill(bg));
            c.drawText(t, x0 + 14 * k, centerBase(y, chH, tp), tp);
            y += chH + 16 * k;
        }

        // bottom lines (átkelési szakasz / KRESZ alapérték / Következő …), anchored to the bottom
        JSONArray arr = o.optJSONArray("lines");
        if (arr != null && arr.length() > 0) {
            Paint lp = text(T_REG, 19 * k, p.onv, Paint.Align.LEFT);
            float lh = 27 * k;
            int n = arr.length();
            int fit = (int) Math.floor((r.bottom - pad - y) / lh);
            n = Math.max(0, Math.min(n, fit));
            float ly = r.bottom - pad - n * lh;
            for (int i = 0; i < n; i++) {
                c.drawText(ellipsize(arr.optString(i), lp, inner), x0, ly + 19 * k * 0.95f, lp);
                ly += lh;
            }
        }
    }

    /** Hungarian town sign: white plate, red border, black name; shrinks the type for long names. Returns its height. */
    private static float drawTown(Canvas c, float x, float y, float maxW, String name, float k) {
        float fs = 34 * k;
        Paint tp = text(T_BOLD, fs, 0xFF151515, Paint.Align.LEFT);
        float padX = 22 * k, border = 4 * k, outer = 4 * k;
        float need = tp.measureText(name) + 2 * (padX + border + outer);
        while (need > maxW && fs > 14 * k) {
            fs -= k;
            tp.setTextSize(fs);
            need = tp.measureText(name) + 2 * (padX + border + outer);
        }
        float w = Math.min(need, maxW), h = fs * 1.1f + 15 * k + 2 * (border + outer);
        c.drawRoundRect(new RectF(x, y, x + w, y + h), 12 * k, 12 * k, fill(0xFFFFFFFF));
        Paint b = stroke(0xFFD2232A, border);
        float o = outer + border / 2;
        c.drawRoundRect(new RectF(x + o, y + o, x + w - o, y + h - o), 8 * k, 8 * k, b);
        c.drawText(ellipsize(name, tp, w - 2 * (padX + border + outer)), x + outer + border + padX, centerBase(y, h, tp), tp);
        return h;
    }

    /** Round speed-limit sign (white, red ring, black number), like signSVG("s") in index.html. */
    private static void drawLimit(Canvas c, float x, float y, float size, String txt) {
        float s = size / 100f, cx = x + 50 * s, cy = y + 50 * s;
        c.drawCircle(cx, cy, 44 * s, fill(0xFFFFFFFF));
        c.drawCircle(cx, cy, 44 * s, stroke(0xFFD62020, 11 * s));
        float fs = (txt.length() <= 2 ? 40 : txt.length() <= 3 ? 34 : 27) * s;
        Paint tp = text(T_BOLD, fs, 0xFF111111, Paint.Align.CENTER);
        c.drawText(txt, cx, cy + 0.35f * fs, tp);
    }

    /** Hungarian road-number sign, same shapes and colours as shieldSVG() in index.html. */
    private static void drawShield(Canvas c, float cx, float top, float hgt, String num, int kut) {
        float s = hgt / 74f;
        int len = num.length();
        boolean isM = num.startsWith("M") || kut == 1 || kut == 2;
        boolean main = kut == 3 || kut == 4;
        float fs = len <= 2 ? 46 : len == 3 ? 44 : len == 4 ? 36 : 30;
        Paint tp = text(T_BOLD, fs, 0xFFFFFFFF, Paint.Align.CENTER);
        tp.setTextScaleX(0.8f);
        c.save();
        if (isM || main) {
            c.translate(cx - 50 * s, top);
            c.scale(s, s);
            Path sh = new Path();
            sh.moveTo(8, 4);
            sh.lineTo(92, 4);
            sh.quadTo(95, 4, 95, 7);
            sh.lineTo(95, 48);
            sh.quadTo(95, 54, 89.5f, 56);
            sh.lineTo(52.5f, 68.9f);
            sh.quadTo(50, 69.8f, 47.5f, 68.9f);
            sh.lineTo(10.5f, 56);
            sh.quadTo(5, 54, 5, 48);
            sh.lineTo(5, 7);
            sh.quadTo(5, 4, 8, 4);
            sh.close();
            c.drawPath(sh, fill(isM ? 0xFF1D4FBF : 0xFF1F7A3A));
            c.drawPath(sh, stroke(0xFFFFFFFF, 5));
            c.drawText(num, 50, 34 + 0.36f * fs, tp);
        } else {
            float W = len >= 4 ? (len == 4 ? 124 : 146) : 100;
            if (len >= 4) {
                fs = 46;
                tp.setTextSize(fs);
            }
            c.translate(cx - W / 2 * s, top);
            c.scale(s, s);
            RectF pl = new RectF(4, 11, W - 4, 61);
            c.drawRoundRect(pl, 7, 7, fill(0xFFF8FAFC));
            c.drawRoundRect(pl, 7, 7, stroke(0xFF111111, 4));
            tp.setColor(0xFF111111);
            c.drawText(num, W / 2, 36 + 0.36f * fs, tp);
        }
        c.restore();
    }

    /** Rounded pill with optional coloured dot; anchored at its left edge, or its right edge when right == true. */
    private static void pill(Canvas c, float x, float y, String t, int dot, int bg, int fg, float k, boolean right) {
        Paint tp = text(T_BOLD, 22 * k, fg, Paint.Align.LEFT);
        float h = 44 * k, padL = (dot != 0 ? 36 : 16) * k, padR = 18 * k;
        float w = padL + tp.measureText(t) + padR;
        float l = right ? x - w : x;
        c.drawRoundRect(new RectF(l, y, l + w, y + h), h / 2, h / 2, fill(bg));
        if (dot != 0) c.drawCircle(l + 20 * k, y + h / 2, 6 * k, fill(dot));
        c.drawText(t, l + padL, centerBase(y, h, tp), tp);
    }

    // ---------- helpers ----------
    private static Paint fill(int color) {
        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.FILL);
        p.setColor(color);
        return p;
    }

    private static Paint stroke(int color, float width) {
        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(width);
        p.setStrokeCap(Paint.Cap.ROUND);
        p.setStrokeJoin(Paint.Join.ROUND);
        p.setColor(color);
        return p;
    }

    private static Paint text(Typeface tf, float size, int color, Paint.Align align) {
        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.SUBPIXEL_TEXT_FLAG);
        p.setTypeface(tf);
        p.setTextSize(size);
        p.setColor(color);
        p.setTextAlign(align);
        return p;
    }

    private static float centerBase(float top, float h, Paint p) {
        Paint.FontMetrics fm = p.getFontMetrics();
        return top + h / 2 - (fm.ascent + fm.descent) / 2;
    }

    private static String ellipsize(String s, Paint p, float maxW) {
        if (s == null) return "";
        if (p.measureText(s) <= maxW) return s;
        int n = s.length();
        while (n > 1 && p.measureText(s.substring(0, n) + "…") > maxW) n--;
        return s.substring(0, n).trim() + "…";
    }

    private static List<String> wrap(String s, Paint p, float maxW, int maxLines) {
        List<String> out = new ArrayList<>();
        if (s == null || s.isEmpty()) return out;
        String[] words = s.split(" ");
        StringBuilder line = new StringBuilder();
        for (String w : words) {
            String test = line.length() == 0 ? w : line + " " + w;
            if (p.measureText(test) <= maxW || line.length() == 0) {
                line.setLength(0);
                line.append(test);
            } else {
                out.add(line.toString());
                line.setLength(0);
                line.append(w);
                if (out.size() == maxLines) break;
            }
        }
        if (out.size() < maxLines && line.length() > 0) out.add(line.toString());
        if (out.size() == maxLines) out.set(maxLines - 1, ellipsize(out.get(maxLines - 1), p, maxW));
        return out;
    }
}
