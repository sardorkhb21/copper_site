"""Remove the two '0 so'm' rows (Шурва, Ок шурва) from the tablet menu screenshot.

    python3 tools/clean_menu_shot.py   → screens/tablet-menu-clean.jpg

Only the menu list (right of the sidebar) is edited: rows 5-6 are cut out and
the rows below move up, exactly like a shorter menu. The blue "Mahsulot
qo'shish" button overlaps the last row, so that row's icons are rebuilt from
the identical row above it and the button is put back at the bottom.
Coordinates are for the 1280x800 original (tablet-menu.jpg).
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = Image.open(os.path.join(ROOT, "screens", "tablet-menu.jpg")).convert("RGB")
BG = (234, 237, 242)
MAIN_X = 222                     # sidebar ends here; only the list is edited
CUT_TOP, CUT_BOT = 429, 572      # Шурва + Ок шурва rows (incl. gaps)
FAB = (1076, 682, 1264, 737)     # "Mahsulot qo'shish" button
SCREEN_BOT = 753                 # Android navigation bar starts below this

# Button, with a rounded mask, taken before anything is touched.
fab = src.crop(FAB)
fmask = Image.new("L", fab.size, 0)
ImageDraw.Draw(fmask).rounded_rectangle((0, 0, fab.width - 1, fab.height - 1), 16, fill=255)

img = src.copy()
# 1. Rebuild the Манти row's right side (hidden under the button) from Сомса's.
img.paste(src.crop((1040, 572, 1280, 641)), (1040, 643))
img.paste(BG, (1040, 712, 1280, SCREEN_BOT))          # button's lower half + shadow
# 2. Cut the two rows: move everything below them up.
shift = CUT_BOT - CUT_TOP
img.paste(img.crop((MAIN_X, CUT_BOT, 1280, SCREEN_BOT)), (MAIN_X, CUT_TOP))
img.paste(BG, (MAIN_X, SCREEN_BOT - shift, 1280, SCREEN_BOT))
# 3. Button back in its place.
img.paste(fab, FAB[:2], fmask)

img.save(os.path.join(ROOT, "screens", "tablet-menu-clean.jpg"), quality=95)
print("screens/tablet-menu-clean.jpg")
