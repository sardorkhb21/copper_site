"""Frame raw app screenshots (screens/*.jpg) as phones for the feature rows.

    python3 tools/make_screens.py      (safe to re-run: reads screens/, writes images/)

Each output is a 1200x900 card — the shape of the .fr-media slot — with the
phone rising from the bottom edge, so only the top ~80% of the screen shows.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = [("waiter-tables.jpg", "app-tables.jpg"), ("waiter-menu.jpg", "app-menu.jpg")]
W, H = 1200, 900
SCREEN_W, BEZEL, TOP, R = 520, 16, 92, 64

for src, out in JOBS:
    shot = Image.open(os.path.join(ROOT, "screens", src)).convert("RGB")
    sh = round(shot.height * SCREEN_W / shot.width)
    shot = shot.resize((SCREEN_W, sh), Image.LANCZOS)

    # soft vertical background, same family as the site's grey surfaces
    card = Image.new("RGB", (W, H))
    top, bot = (246, 246, 248), (234, 235, 239)
    for y in range(H):
        t = y / (H - 1)
        ImageDraw.Draw(card).line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bot)))

    pw, ph = SCREEN_W + 2 * BEZEL, sh + 2 * BEZEL
    x0 = (W - pw) // 2
    # shadow
    shadow = Image.new("L", (W, H + ph), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x0, TOP + 24, x0 + pw, TOP + 24 + ph), R + BEZEL, fill=70)
    shadow = shadow.filter(ImageFilter.GaussianBlur(36)).crop((0, 0, W, H))
    card.paste((0, 0, 0), (0, 0), shadow)
    # bezel + screen
    phone = Image.new("RGB", (pw, ph), (17, 17, 19))
    pmask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(pmask).rounded_rectangle((0, 0, pw - 1, ph - 1), R + BEZEL, fill=255)
    smask = Image.new("L", (SCREEN_W, sh), 0)
    ImageDraw.Draw(smask).rounded_rectangle((0, 0, SCREEN_W - 1, sh - 1), R, fill=255)
    phone.paste(shot, (BEZEL, BEZEL), smask)
    card.paste(phone, (x0, TOP), pmask)

    card.save(os.path.join(ROOT, "images", out), "JPEG", quality=84, optimize=True, progressive=True)
    print(out, os.path.getsize(os.path.join(ROOT, "images", out)) // 1024, "KB")
