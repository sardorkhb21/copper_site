"""Picture for the QR-ordering section: a phone showing the live Copper QR
menu (Oq Shurva, screenshot of menu.copperpos.uz) and a table QR card.

    python3 tools/make_qr_visual.py   → images/qr-visual.webp (transparent)

Needs: pip install --user segno   (QR drawing)
The card's QR really opens copperpos.uz.
"""
import os
import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = "/System/Library/Fonts/SFNS.ttf"
ICON = os.path.expanduser("~/development/pos_app/assets/icon/app_icon.png")
W, H = 1000, 1120

def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([100, min(96, max(17, size)), 400, weight])
    return f

def shadow(canvas, box, radius, blur, alpha, dy):
    m = Image.new("L", canvas.size, 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), radius, fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 255))
    layer.putalpha(m)
    canvas.alpha_composite(layer)

canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# ── Phone ────────────────────────────────────────────────────
SCREEN_W, BEZEL, R = 520, 18, 62
shot = Image.open(os.path.join(ROOT, "screens", "qr-menu-oqshurva.png")).convert("RGB")
shot = shot.resize((SCREEN_W, round(shot.height * SCREEN_W / shot.width)), Image.LANCZOS)
SCREEN_H = 1010
# Status-bar strip in the header colour, so the camera notch never covers the
# restaurant name.
STATUS = 58
top = Image.new("RGB", (SCREEN_W, SCREEN_H), shot.getpixel((4, 4)))
top.paste(shot.crop((0, 0, SCREEN_W, SCREEN_H - STATUS)), (0, STATUS))
shot = top
pw, ph = SCREEN_W + 2 * BEZEL, SCREEN_H + 2 * BEZEL
px, py = 90, (H - ph) // 2
shadow(canvas, (px, py, px + pw, py + ph), R + BEZEL, 40, 90, 26)
phone = Image.new("RGBA", (pw, ph), (17, 17, 19, 255))
smask = Image.new("L", (SCREEN_W, SCREEN_H), 0)
ImageDraw.Draw(smask).rounded_rectangle((0, 0, SCREEN_W - 1, SCREEN_H - 1), R, fill=255)
phone.paste(shot, (BEZEL, BEZEL), smask)
ImageDraw.Draw(phone).rounded_rectangle((pw // 2 - 62, BEZEL + 14, pw // 2 + 62, BEZEL + 46), 16, fill=(10, 10, 12))
pmask = Image.new("L", (pw, ph), 0)
ImageDraw.Draw(pmask).rounded_rectangle((0, 0, pw - 1, ph - 1), R + BEZEL, fill=255)
canvas.paste(phone, (px, py), pmask)

# ── Table QR card ────────────────────────────────────────────
CW, CH, CR = 330, 430, 34
cx, cy = W - CW - 40, 520
shadow(canvas, (cx, cy, cx + CW, cy + CH), CR, 30, 70, 18)
card = Image.new("RGBA", (CW, CH), (255, 255, 255, 255))
d = ImageDraw.Draw(card)
ic = Image.open(ICON).convert("RGBA").resize((64, 64), Image.LANCZOS)
im = Image.new("L", (64, 64), 0); ImageDraw.Draw(im).rounded_rectangle((0, 0, 63, 63), 15, fill=255)
card.paste(ic, (34, 34), im)
d.text((112, 44), "Copper", font=font(30, 800), fill=(10, 10, 10))
d.text((112, 80), "QR menu", font=font(20, 500), fill=(120, 122, 128))
qr = segno.make("https://copperpos.uz", error="m")
size = 240
qimg = Image.new("L", (qr.symbol_size(border=0)[0],) * 2, 255)
for y, row in enumerate(qr.matrix):
    for x, v in enumerate(row):
        if v:
            qimg.putpixel((x, y), 0)
qimg = qimg.resize((size, size), Image.NEAREST).convert("RGBA")
card.paste(qimg, ((CW - size) // 2, 128))
d.text((CW // 2, 396), "copperpos.uz", font=font(20, 600), fill=(70, 72, 78), anchor="mm")
cmask = Image.new("L", (CW, CH), 0)
ImageDraw.Draw(cmask).rounded_rectangle((0, 0, CW - 1, CH - 1), CR, fill=255)
canvas.paste(card, (cx, cy), cmask)

out = os.path.join(ROOT, "images", "qr-visual.webp")
canvas.save(out, "WEBP", quality=86, method=6)
print("images/qr-visual.webp", os.path.getsize(out) // 1024, "KB")
