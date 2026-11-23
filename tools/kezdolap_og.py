#!/usr/bin/env python3
"""Builds the link-preview picture of the landing page (site/kepek/og.jpg, 1200×630).

Layout, centred so that every crop the apps make still shows the logo, the name and the
main screenshot (Facebook / Messenger use the full 1.91:1 picture, WhatsApp and some others
cut a centred square, i.e. x 285–915):
  - logo + "ÚtSzelvény" in one centred row, the slogan under it
  - three phones (Térkép, Pozíció, Mérés) rising from the bottom edge, the middle one in front
  - the landing page's road-network background (site/hatter.svg)
Everything important stays at least 48 px from the edges.

Needs: Pillow, rsvg-convert (librsvg), the Roboto variable font.
    python3 tools/kezdolap_og.py
"""
import os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W, H = 1200, 630
BG = (229, 235, 228)            # #E5EBE4
INK = (15, 20, 15)              # #0F140F
GREEN = (43, 106, 70)           # #2B6A46
FONT = "/usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf"

def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight, 100])      # weight, width
    except Exception:
        pass
    return f

def shadowed(canvas, im, x, y, blur=16, dy=14, alpha=.30):
    sh = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: int(v * alpha))
    dark = Image.new("RGBA", im.size, (15, 20, 15, 255))
    dark.putalpha(a)
    sh.alpha_composite(dark, (2 * blur, 2 * blur))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh, (x - 2 * blur, y - 2 * blur + dy))
    canvas.alpha_composite(im, (x, y))

def phone(name, width):
    im = Image.open(os.path.join(ROOT, "site", "kepek", name)).convert("RGBA")
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)

# background: the landing page's road network
with tempfile.TemporaryDirectory() as t:
    png = os.path.join(t, "bg.png")
    subprocess.run(["rsvg-convert", "-w", "1440", "-b", "#E5EBE4", os.path.join(ROOT, "site", "hatter.svg"), "-o", png], check=True)
    bg = Image.open(png).convert("RGBA").crop((120, 1160, 120 + W, 1160 + H))
canvas = Image.new("RGBA", (W, H), BG + (255,))
canvas.alpha_composite(bg)

# phones rising from the bottom edge: sides first, the middle one in front
left, mid, right = phone("terkep.webp", 250), phone("pozicio.webp", 300), phone("meres.webp", 250)
shadowed(canvas, left, 600 - 150 - 250 + 30, 338)
shadowed(canvas, right, 600 + 150 - 30, 338)
shadowed(canvas, mid, 600 - 150, 268, blur=20, dy=16, alpha=.36)

# logo + name, centred; slogan under it
d = ImageDraw.Draw(canvas)
title_f, slogan_f = font(84, 700), font(30, 500)
logo = Image.open(os.path.join(ROOT, "web", "icon-512.png")).convert("RGBA").resize((104, 104), Image.LANCZOS)
tw = d.textlength("ÚtSzelvény", font=title_f)
gap = 22
x0 = round((W - (logo.width + gap + tw)) / 2)
top = 52
shadowed(canvas, logo, x0, top, blur=8, dy=4, alpha=.25)
d.text((x0 + logo.width + gap, top + logo.height / 2), "ÚtSzelvény", font=title_f, fill=INK, anchor="lm")
d.text((W / 2, top + logo.height + 40), "Kilométerkő minden méteren – a zsebedben.", font=slogan_f, fill=GREEN, anchor="mm")

out = os.path.join(ROOT, "site", "kepek", "og.jpg")
canvas.convert("RGB").save(out, quality=88, optimize=True, progressive=True)
print(f"{out}: {os.path.getsize(out) // 1024} KB")
