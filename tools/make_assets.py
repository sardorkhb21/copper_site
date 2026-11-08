"""One-time asset generator for copperpos.uz SEO.

Makes the favicon set and the link-preview (Open Graph) images from the
Copper app icon, and re-compresses the site photos. Run from the repo root:
    python3 tools/make_assets.py
Outputs go to static/ (copied into dist/ by build.mjs) and images/ (in place).
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.expanduser("~/development/pos_app/assets/icon/app_icon.png")
OUT = os.path.join(ROOT, "static")
FONT = "/System/Library/Fonts/SFNS.ttf"

icon = Image.open(ICON).convert("RGBA")

# ── Favicons / app icons ────────────────────────────────────
for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"),
                   (512, "icon-512.png"), (48, "favicon-48.png")]:
    icon.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name), optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(
    os.path.join(OUT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# ── Open Graph share images (1200×630), one per language ────
def font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([100, min(96, max(17, size)), 400, weight])
    return f

TEXT = {
    "uz": ("Restoran va kafe uchun", "kassa tizimi",
           "Buyurtma · Stollar · Oshxona · QR menyu · Hisobotlar",
           "O'zbekistonda ishlab chiqilgan"),
    "ru": ("Касса для ресторанов", "и кафе",
           "Заказы · Столы · Кухня · QR-меню · Отчёты",
           "Сделано в Узбекистане"),
    "en": ("POS for restaurants", "and cafes",
           "Orders · Tables · Kitchen · QR menu · Reports",
           "Made in Uzbekistan"),
}
INK, SOFT, FAINT, LINE = (10, 10, 10), (70, 72, 78), (120, 122, 128), (232, 233, 236)
for lang, (l1, l2, feats, made) in TEXT.items():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    # rounded app icon, left
    s = 168
    ic = icon.resize((s, s), Image.LANCZOS)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s, s), radius=38, fill=255)
    im.paste(ic, (80, 84), mask)
    d.text((80, 300), "Copper POS", font=font(44, 700), fill=FAINT)
    d.text((76, 350), l1, font=font(72, 800), fill=INK)
    d.text((76, 432), l2, font=font(72, 800), fill=INK)
    d.line((80, 540, W - 80, 540), fill=LINE, width=2)
    d.text((80, 560), feats, font=font(28, 500), fill=SOFT)
    d.text((W - 80, 112), "copperpos.uz", font=font(30, 700), fill=INK, anchor="ra")
    d.text((W - 80, 156), made, font=font(24, 500), fill=FAINT, anchor="ra")
    im.save(os.path.join(OUT, f"og-{lang}.png"), optimize=True)

# ── Re-compress the photos (same pixels size, much lighter) ─
imgdir = os.path.join(ROOT, "images")
for n in sorted(os.listdir(imgdir)):
    if not n.endswith(".jpg"):
        continue
    p = os.path.join(imgdir, n)
    before = os.path.getsize(p)
    Image.open(p).convert("RGB").save(p, "JPEG", quality=78, optimize=True, progressive=True)
    print(f"{n}: {before//1024} KB -> {os.path.getsize(p)//1024} KB")
