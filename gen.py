#!/usr/bin/env python3
"""news-image-20261121 — deterministic broadsheet front page for 21 Nov 2026.

Renders at 2048x2048 with Pillow, then downscales (LANCZOS) to 1024x1024.
No network, no timestamps, no randomness: re-running produces byte-identical
entry.png. Every headline is a verified 21 November 2026 event (see
../dev/STORY-POOL.md); one-party claims stay attributed; Friday/Thursday
lookalikes are named in the DATE CHECK box, not on the page.
Winner-pattern layout (from the 20261119 top-5 autopsy, applied again in
20261120): 44 stories, 3 heroes, stat strip, numbered stories, world map
with pins, per-story sources, DATE CHECK box.
"""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2048
M = 36

PAPER = (246, 241, 230)
INK = (24, 24, 30)
NAVY = (18, 38, 74)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
GOLD = (201, 162, 39)
TEAL = (16, 96, 110)
GREY = (110, 110, 116)
LIGHT = (255, 255, 255)
CREAM = (252, 248, 238)
DARK = (16, 26, 40)
MAPSEA = (24, 52, 92)
MAPLAND = (120, 160, 110)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(w, h, top, bottom):
    """Vertical gradient, built by stretching a 1x256 strip: deterministic."""
    strip = Image.new("RGB", (1, 256))
    px = strip.load()
    for i in range(256):
        t = i / 255.0
        px[0, i] = tuple(int(top[c] + (bottom[c] - top[c]) * t)
                         for c in range(3))
    return strip.resize((w, h), Image.BILINEAR)


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    lines = wrap(d, text, fnt, max_w)
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y, len(lines)


def rule(d, x0, y, x1, color=INK, width=4):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def kicker(d, x, y, text, color=RED, size=28):
    d.text((x, y), text, font=font(F_SANS, size), fill=color)


def num_badge(d, x, y, n, r=24, fill=RED, fg=LIGHT, size=30):
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=INK, width=3)
    d.text((x, y), str(n), font=font(F_SANS, size), fill=fg, anchor="mm")


def masthead(d, w):
    rule(d, M, 46, w - M, INK, 6)
    d.text((w // 2, 56), "THE WORLD IN ONE PICTURE",
           font=font(F_SERIF, 88), fill=INK, anchor="ma")
    d.text((w // 2, 146),
           "S A T U R D A Y   2 1   N O V E M B E R   2 0 2 6   \u00b7   "
           "4 4   S T O R I E S   \u00b7   O N E   P A G E",
           font=font(F_SANS, 40), fill=RED, anchor="ma")
    d.text((w // 2, 202),
           "MIDDLE EAST 6  \u00b7  EUROPE 10  \u00b7  ASIA 12  \u00b7  "
           "AMERICAS 6  \u00b7  AFRICA 2  \u00b7  OCEANIA 3  \u00b7  SPACE 3  "
           "\u00b7  GLOBAL 2",
           font=font(F_SANS, 26), fill=GREY, anchor="ma")
    rule(d, M, 238, w - M, RED, 5)


STATS = [
    ("148", "drones at Ukraine"),
    ("$55,130", "Bitcoin's Saturday low"),
    ("352", "overtakes in Las Vegas"),
    ("18.8 ft", "St. Johns flood record"),
    ("82,500", "march in France"),
    ("90.4%", "tariff lines go to zero"),
    ("129", "bodies from Gaza rubble"),
]


def stat_strip(d, y0, y1):
    d.rectangle([M, y0, S - M, y1], fill=NAVY, outline=INK, width=4)
    n = len(STATS)
    w = (S - 2 * M) / n
    for i, (big, label) in enumerate(STATS):
        x = M + i * w
        if i:
            d.line([(x, y0 + 12), (x, y1 - 12)], fill=(90, 120, 170), width=3)
        d.text((x + w / 2, y0 + 10), big, font=font(F_SERIF, 48),
               fill=GOLD, anchor="ma")
        d.text((x + w / 2, y0 + 66), label, font=font(F_SANS_R, 21),
               fill=(215, 220, 230), anchor="ma")


# ---- heroes ---------------------------------------------------------------
# Each hero: illustration strip on top (158px), then kicker, headline
# (serif 38, max 2 lines), dek (sans 24, max 2 lines). Box height 356.

def hero_frame(img, d, box, n, kick, head, dek, illu):
    x0, y0, x1, y1 = box
    tmp = Image.new("RGB", (x1 - x0, 158), PAPER)
    d2 = ImageDraw.Draw(tmp, "RGBA")
    illu(tmp, d2, (0, 0, x1 - x0, 158))
    img.paste(tmp, (x0, y0))
    d.rectangle([x0, y0 + 158, x1, y1], fill=PAPER)
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)
    num_badge(d, x0 + 40, y0 + 180, n)
    kicker(d, x0 + 76, y0 + 166, kick, RED, 26)
    _, hl = text_block(d, x0 + 24, y0 + 206, head, font(F_SERIF, 38), INK,
                       x1 - x0 - 48, leading=42)
    assert hl <= 2, f"hero headline overflow: {head}"
    _, dl = text_block(d, x0 + 24, y0 + 294, dek,
                       font(F_SANS_R, 24), INK, x1 - x0 - 48, leading=28)
    assert dl <= 2, f"hero dek overflow: {dek}"
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)


def hero_hormuz(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 158, (20, 18, 40), (150, 70, 30))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 112, x1, y0 + 158], fill=(22, 48, 76))
    # two tankers, one burning at the stern
    d.polygon([(x0 + 60, y0 + 88), (x0 + 300, y0 + 88), (x0 + 284, y0 + 118),
               (x0 + 76, y0 + 118)], fill=(150, 32, 32))
    d.rectangle([x0 + 250, y0 + 56, x0 + 292, y0 + 88], fill=(210, 210, 205))
    d.polygon([(x0 + 400, y0 + 96), (x0 + 590, y0 + 96), (x0 + 576, y0 + 122),
               (x0 + 414, y0 + 122)], fill=(120, 30, 30))
    d.rectangle([x0 + 430, y0 + 66, x0 + 466, y0 + 96], fill=(210, 210, 205))
    for fx, fh in [(96, 52), (130, 68), (164, 48), (440, 56), (470, 70)]:
        d.polygon([(x0 + fx - 16, y0 + 90), (x0 + fx, y0 + 90 - fh),
                   (x0 + fx + 16, y0 + 90)], fill=(255, 120, 20))
        d.polygon([(x0 + fx - 8, y0 + 90), (x0 + fx, y0 + 90 - fh // 2),
                   (x0 + fx + 8, y0 + 90)], fill=(255, 210, 60))
    for sx in (340, 420, 520):
        d.ellipse([x0 + sx, y0 + 128, x0 + sx + 26, y0 + 142],
                  fill=(60, 66, 70))
    d.text((x0 + 24, y0 + 10), "STRAIT OF HORMUZ",
           font=font(F_SANS, 30), fill=(255, 220, 150))


def hero_vegas(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 158, (12, 8, 40), (90, 20, 110))
    img.paste(sky, (x0, y0))
    # neon skyline + lit track
    for bx, bh, col in [(30, 70, (25, 20, 60)), (110, 100, (35, 20, 70)),
                        (210, 80, (25, 20, 60)), (300, 110, (40, 20, 75)),
                        (420, 90, (25, 20, 60)), (520, 70, (35, 20, 70))]:
        d.rectangle([x0 + bx, y0 + 130 - bh, x0 + bx + 60, y0 + 130],
                    fill=col)
        for wy in range(0, bh - 12, 16):
            d.rectangle([x0 + bx + 8, y0 + 130 - bh + wy, x0 + bx + 22,
                         y0 + 130 - bh + wy + 8], fill=(255, 220, 100))
    d.rectangle([x0, y0 + 130, x1, y0 + 158], fill=(14, 14, 20))
    # two race cars, headlights and speed lines
    for cx, col in [(140, (220, 30, 30)), (330, (40, 120, 220))]:
        d.rectangle([x0 + cx, y0 + 118, x0 + cx + 110, y0 + 134], fill=col)
        d.ellipse([x0 + cx + 18, y0 + 132, x0 + cx + 38, y0 + 146], fill=INK)
        d.ellipse([x0 + cx + 72, y0 + 132, x0 + cx + 92, y0 + 146], fill=INK)
        d.line([(x0 + cx - 60, y0 + 126), (x0 + cx - 6, y0 + 126)],
               fill=(255, 240, 160), width=4)
    d.text((x0 + 24, y0 + 10), "LAS VEGAS  \u00b7  352 OVERTAKES",
           font=font(F_SANS, 30), fill=(255, 220, 150))


def hero_mercury(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 158, (6, 6, 16), (60, 40, 20))
    img.paste(sky, (x0, y0))
    # Mercury: cratered crescent low, sun glare top right, spacecraft
    d.ellipse([x0 + 500, y0 + 20, x0 + 580, y0 + 100], fill=(255, 230, 150))
    d.ellipse([x0 + 514, y0 + 34, x0 + 566, y0 + 86], fill=(255, 200, 90))
    d.ellipse([x0 + 60, y0 + 78, x0 + 560, y0 + 260], fill=(150, 135, 120))
    for cx, cy, cr in [(180, 130, 14), (260, 108, 9), (330, 140, 18),
                       (430, 120, 10), (500, 138, 12), (220, 150, 8)]:
        d.ellipse([x0 + cx - cr, y0 + cy - cr, x0 + cx + cr, y0 + cy + cr],
                  fill=(110, 98, 86))
    # BepiColombo: bus + two solar wings
    d.rectangle([x0 + 250, y0 + 52, x0 + 330, y0 + 92], fill=(200, 200, 210),
                outline=INK, width=3)
    d.rectangle([x0 + 160, y0 + 62, x0 + 250, y0 + 82], fill=(30, 60, 140))
    d.rectangle([x0 + 330, y0 + 62, x0 + 420, y0 + 82], fill=(30, 60, 140))
    d.text((x0 + 24, y0 + 10), "MERCURY  \u00b7  8 YEARS IN TRANSIT",
           font=font(F_SANS, 28), fill=(255, 220, 150))

# ---- generic panel -------------------------------------------------------
# Box height 238: illustration strip 74px, kicker, headline (max 2 lines),
# dek (max 2 lines). Illustrations are drawn at 140px height then scaled.

def panel(img, d, box, n, kick, head, dek, src, illu, hsize=29, dsize=22,
          illu_h=74):
    x0, y0, x1, y1 = box
    tmp = Image.new("RGB", (x1 - x0, 140), PAPER)
    d2 = ImageDraw.Draw(tmp, "RGBA")
    illu(tmp, d2, (0, 0, x1 - x0, 140))
    img.paste(tmp.resize((x1 - x0, illu_h), Image.LANCZOS), (x0, y0))
    d.rectangle([x0, y0 + illu_h, x1, y1], fill=PAPER)
    d.rounded_rectangle(box, radius=12, outline=INK, width=4)
    num_badge(d, x0 + 30, y0 + illu_h + 22, n, r=19, size=25)
    kicker(d, x0 + 58, y0 + illu_h + 12, kick, RED, 22)
    _, hl = text_block(d, x0 + 18, y0 + illu_h + 42, head,
                       font(F_SERIF, hsize), INK, x1 - x0 - 36,
                       leading=int(hsize * 1.2))
    assert hl <= 2, f"panel headline overflow: {head}"
    _, dl = text_block(d, x0 + 18, y0 + illu_h + 42 + 2 * int(hsize * 1.2) + 2,
                       dek + " \u2014 " + src, font(F_SANS_R, dsize), INK,
                       x1 - x0 - 36, leading=int(dsize * 1.22))
    assert dl <= 2, f"panel dek overflow: {dek}"
    d.rounded_rectangle(box, radius=12, outline=INK, width=4)


def illu_truck(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (200, 170, 130), (120, 90, 70))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 108, x1, y1], fill=(110, 95, 70))
    # aid truck with boxes, smoke column
    d.rectangle([x0 + 90, y0 + 60, x0 + 300, y0 + 112], fill=(240, 235, 220),
                outline=INK, width=3)
    d.rectangle([x0 + 300, y0 + 76, x0 + 360, y0 + 112], fill=(200, 60, 40))
    for bx in (120, 170, 220):
        d.rectangle([x0 + bx, y0 + 72, x0 + bx + 36, y0 + 100],
                    fill=(220, 190, 120), outline=INK, width=2)
    d.ellipse([x0 + 120, y0 + 112, x0 + 150, y0 + 140], fill=INK)
    d.ellipse([x0 + 310, y0 + 112, x0 + 340, y0 + 140], fill=INK)
    for sx, sy, sr in [(390, 50, 16), (410, 30, 20), (430, 52, 14)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(80, 76, 74))


def illu_march(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (150, 170, 200), (220, 210, 190))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 112, x1, y1], fill=(140, 135, 125))
    # crowd: heads + shoulders, two placards
    for hx in range(30, 460, 44):
        d.ellipse([x0 + hx, y0 + 66, x0 + hx + 26, y0 + 92], fill=(60, 50, 45))
        d.rectangle([x0 + hx - 4, y0 + 92, x0 + hx + 30, y0 + 112],
                    fill=((hx * 7) % 3 == 0) and (180, 60, 50) or (50, 70, 110))
    d.rectangle([x0 + 60, y0 + 22, x0 + 180, y0 + 58], fill=LIGHT,
                outline=INK, width=3)
    d.text((x0 + 120, y0 + 40), "NON", font=font(F_SANS, 24), fill=RED,
           anchor="mm")
    d.rectangle([x0 + 280, y0 + 16, x0 + 400, y0 + 52], fill=LIGHT,
                outline=INK, width=3)
    d.text((x0 + 340, y0 + 34), "82 500", font=font(F_SANS, 22), fill=INK,
           anchor="mm")


def illu_bitcoin(img, d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=DARK)
    # plunging then rebounding chart
    pts = [(x0 + 30, y0 + 40), (x0 + 120, y0 + 70), (x0 + 210, y0 + 100),
           (x0 + 290, y0 + 118), (x0 + 370, y0 + 60), (x0 + 440, y0 + 44)]
    d.line(pts, fill=(255, 90, 90), width=7, joint="curve")
    d.ellipse([x0 + 278, y0 + 106, x0 + 302, y0 + 130], fill=(255, 90, 90))
    # coin
    d.ellipse([x0 + 380, y0 + 78, x0 + 440, y0 + 138], fill=GOLD,
              outline=(140, 100, 20), width=3)
    d.text((x0 + 410, y0 + 108), "B", font=font(F_SANS, 40), fill=(120, 80, 10),
           anchor="mm")
    d.text((x0 + 24, y0 + 12), "$55,130", font=font(F_SANS, 30),
           fill=(255, 120, 120))
    d.text((x0 + 24, y0 + 116), "$60,000", font=font(F_SANS, 24),
           fill=(120, 220, 140))


def illu_handshake(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (70, 100, 170), (210, 215, 230))
    img.paste(sky, (x0, y0))
    # EU flag + Indonesian flag on poles, clasped hands below
    d.line([(x0 + 110, y0 + 16), (x0 + 110, y0 + 96)], fill=(220, 220, 220),
           width=5)
    d.rectangle([x0 + 116, y0 + 20, x0 + 216, y0 + 72], fill=(20, 40, 120))
    for i in range(6):
        a = math.radians(i * 60 - 90)
        d.ellipse([x0 + 166 + 18 * math.cos(a) - 3,
                   y0 + 46 + 18 * math.sin(a) - 3,
                   x0 + 166 + 18 * math.cos(a) + 3,
                   y0 + 46 + 18 * math.sin(a) + 3], fill=GOLD)
    d.line([(x0 + 340, y0 + 16), (x0 + 340, y0 + 96)], fill=(220, 220, 220),
           width=5)
    d.rectangle([x0 + 346, y0 + 20, x0 + 446, y0 + 72], fill=(210, 30, 30))
    d.rectangle([x0 + 346, y0 + 46, x0 + 446, y0 + 72], fill=LIGHT)
    d.rectangle([x0, y0 + 120, x1, y1], fill=(95, 115, 85))
    d.ellipse([x0 + 190, y0 + 96, x0 + 270, y0 + 132], fill=(220, 180, 140))
    d.ellipse([x0 + 210, y0 + 96, x0 + 290, y0 + 132], fill=(200, 160, 125))


def illu_clock(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (30, 60, 90), (120, 170, 200))
    img.paste(sky, (x0, y0))
    d.rectangle([x0 + 50, y0 + 76, x0 + 210, y0 + 140], fill=(40, 50, 66))
    d.polygon([(x0 + 42, y0 + 78), (x0 + 130, y0 + 40), (x0 + 218, y0 + 78)],
              fill=(28, 36, 50))
    # big clock face, hands past midnight
    d.ellipse([x0 + 300, y0 + 20, x0 + 420, y0 + 140], fill=LIGHT,
              outline=INK, width=4)
    d.line([(x0 + 360, y0 + 80), (x0 + 360, y0 + 36)], fill=INK, width=6)
    d.line([(x0 + 360, y0 + 80), (x0 + 396, y0 + 100)], fill=INK, width=6)
    d.ellipse([x0 + 354, y0 + 74, x0 + 366, y0 + 86], fill=RED)


def illu_flood(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (120, 140, 160), (200, 200, 190))
    img.paste(sky, (x0, y0))
    # houses half-submerged, gauge post with 18.8 ft mark
    for hx in (60, 200, 330):
        d.rectangle([x0 + hx, y0 + 60, x0 + hx + 90, y0 + 110],
                    fill=(190, 170, 140))
        d.polygon([(x0 + hx - 8, y0 + 62), (x0 + hx + 45, y0 + 30),
                   (x0 + hx + 98, y0 + 62)], fill=(150, 60, 50))
    d.rectangle([x0, y0 + 104, x1, y1], fill=(40, 90, 130))
    for wy in range(0, 460, 60):
        d.line([(x0 + wy, y0 + 122), (x0 + wy + 34, y0 + 122)],
               fill=(140, 200, 230), width=4)
    d.rectangle([x0 + 430, y0 + 30, x0 + 442, y0 + 140], fill=LIGHT,
                outline=INK, width=2)
    d.line([(x0 + 418, y0 + 44), (x0 + 442, y0 + 44)], fill=RED, width=5)
    d.text((x0 + 424, y0 + 20), "18.8", font=font(F_SANS, 20), fill=RED,
           anchor="ra")


def illu_fire(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (40, 30, 30), (140, 60, 30))
    img.paste(sky, (x0, y0))
    d.rectangle([x0 + 70, y0 + 70, x0 + 330, y0 + 140], fill=(170, 160, 150))
    d.rectangle([x0 + 70, y0 + 70, x0 + 330, y0 + 92], fill=(120, 40, 40))
    for wx in (100, 170, 240, 300):
        d.rectangle([x0 + wx, y0 + 100, x0 + wx + 22, y0 + 126],
                    fill=(255, 210, 90))
    for fx, fh in [(120, 60), (180, 84), (250, 64), (310, 50)]:
        d.polygon([(x0 + fx - 18, y0 + 74), (x0 + fx, y0 + 74 - fh),
                   (x0 + fx + 18, y0 + 74)], fill=(255, 120, 20))
        d.polygon([(x0 + fx - 9, y0 + 74), (x0 + fx, y0 + 74 - fh // 2),
                   (x0 + fx + 9, y0 + 74)], fill=(255, 210, 60))
    for sx, sy, sr in [(380, 30, 20), (410, 52, 26), (440, 28, 18)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(70, 66, 66))


def illu_ship(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (60, 80, 110), (180, 180, 170))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 100, x1, y1], fill=(40, 80, 110))
    # cargo ship listing, smoke and flame, two drone dots
    d.polygon([(x0 + 70, y0 + 78), (x0 + 360, y0 + 70), (x0 + 340, y0 + 106),
               (x0 + 90, y0 + 106)], fill=(90, 90, 96))
    d.rectangle([x0 + 240, y0 + 44, x0 + 300, y0 + 72], fill=(200, 60, 40))
    for fx, fh in [(150, 46), (200, 60)]:
        d.polygon([(x0 + fx - 14, y0 + 76), (x0 + fx, y0 + 76 - fh),
                   (x0 + fx + 14, y0 + 76)], fill=(255, 120, 20))
    for dx, dy in [(380, 26), (420, 44)]:
        d.ellipse([x0 + dx - 6, y0 + dy - 6, x0 + dx + 6, y0 + dy + 6],
                  fill=INK)
        d.line([(x0 + dx - 16, y0 + dy), (x0 + dx + 16, y0 + dy)], fill=INK,
               width=3)


def illu_quake(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (140, 130, 110), (220, 210, 190))
    img.paste(sky, (x0, y0))
    # cracked ground + seismograph trace
    d.polygon([(x0, y0 + 140), (x0 + 180, y0 + 100), (x0 + 460, y0 + 140)],
              fill=(120, 95, 65))
    d.line([(x0 + 200, y0 + 100), (x0 + 230, y0 + 122), (x0 + 260, y0 + 108),
            (x0 + 300, y0 + 140)], fill=(60, 45, 30), width=5)
    d.rectangle([x0 + 40, y0 + 30, x0 + 420, y0 + 92], fill=LIGHT,
                outline=INK, width=3)
    pts = [(x0 + 60, y0 + 62), (x0 + 110, y0 + 62), (x0 + 140, y0 + 40),
           (x0 + 170, y0 + 84), (x0 + 200, y0 + 62), (x0 + 250, y0 + 62),
           (x0 + 280, y0 + 46), (x0 + 310, y0 + 80), (x0 + 340, y0 + 62),
           (x0 + 400, y0 + 62)]
    d.line(pts, fill=RED, width=4, joint="curve")


def illu_hospital(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (200, 210, 220), (170, 180, 190))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 116, x1, y1], fill=(120, 130, 135))
    # bed + monitor with flat-ish trace
    d.rectangle([x0 + 60, y0 + 88, x0 + 300, y0 + 116], fill=(240, 240, 235),
                outline=INK, width=3)
    d.ellipse([x0 + 76, y0 + 66, x0 + 112, y0 + 92], fill=(220, 180, 140))
    d.rectangle([x0 + 76, y0 + 88, x0 + 250, y0 + 100], fill=(90, 140, 190))
    d.rectangle([x0 + 330, y0 + 30, x0 + 430, y0 + 96], fill=DARK,
                outline=INK, width=3)
    d.line([(x0 + 340, y0 + 64), (x0 + 362, y0 + 64), (x0 + 372, y0 + 44),
            (x0 + 382, y0 + 82), (x0 + 392, y0 + 64), (x0 + 420, y0 + 64)],
           fill=(80, 220, 120), width=4)


def illu_robot(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (40, 50, 70), (120, 130, 150))
    img.paste(sky, (x0, y0))
    # UN-style building + robot silhouette with red eye
    d.rectangle([x0 + 60, y0 + 56, x0 + 200, y0 + 140], fill=(200, 200, 195))
    for wy in range(64, 132, 16):
        d.rectangle([x0 + 72, y0 + wy, x0 + 188, y0 + wy + 8],
                    fill=(120, 130, 140))
    d.rectangle([x0 + 300, y0 + 60, x0 + 380, y0 + 140], fill=(90, 95, 105))
    d.ellipse([x0 + 318, y0 + 28, x0 + 362, y0 + 66], fill=(60, 65, 75))
    d.ellipse([x0 + 330, y0 + 42, x0 + 350, y0 + 54], fill=RED)
    d.rectangle([x0 + 330, y0 + 66, x0 + 350, y0 + 90], fill=(60, 65, 75))
    d.text((x0 + 262, y0 + 10), "NO RULES", font=font(F_SANS, 20),
           fill=RED)


def illu_camera(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (90, 60, 110), (200, 160, 190))
    img.paste(sky, (x0, y0))
    # film camera + pink ribbon
    d.rectangle([x0 + 90, y0 + 50, x0 + 300, y0 + 120], fill=(40, 40, 48))
    d.ellipse([x0 + 150, y0 + 60, x0 + 230, y0 + 120], fill=(120, 140, 170),
              outline=LIGHT, width=4)
    d.ellipse([x0 + 172, y0 + 76, x0 + 208, y0 + 104], fill=(30, 60, 100))
    d.rectangle([x0 + 300, y0 + 66, x0 + 340, y0 + 104], fill=(60, 60, 70))
    d.ellipse([x0 + 380, y0 + 40, x0 + 430, y0 + 90], fill=(230, 120, 170))
    d.rectangle([x0 + 396, y0 + 84, x0 + 414, y0 + 130], fill=(230, 120, 170))
    d.text((x0 + 24, y0 + 12), "HEAL", font=font(F_SERIF, 34), fill=LIGHT)


def illu_goal(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (40, 90, 50), (140, 180, 120))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 110, x1, y1], fill=(50, 110, 55))
    # goal net + ball in the net, scoreboard "4"
    d.rectangle([x0 + 280, y0 + 30, x0 + 430, y0 + 110], fill=LIGHT,
                outline=INK, width=4)
    for gx in range(292, 430, 22):
        d.line([(x0 + gx, y0 + 32), (x0 + gx, y0 + 108)], fill=GREY, width=2)
    for gy in range(42, 110, 20):
        d.line([(x0 + 282, y0 + gy), (x0 + 428, y0 + gy)], fill=GREY, width=2)
    d.ellipse([x0 + 330, y0 + 66, x0 + 372, y0 + 108], fill=LIGHT,
              outline=INK, width=3)
    d.text((x0 + 40, y0 + 30), "4 GOALS", font=font(F_SERIF, 40), fill=LIGHT)
    d.text((x0 + 40, y0 + 84), "ROMA 5\u20131 PARMA", font=font(F_SANS, 24),
           fill=(255, 230, 120))

# ---- world map -----------------------------------------------------------

CONTINENTS = [
    [(-170, 70), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
     (-60, -40), (-70, -55), (-75, -35), (-80, -15)],
    [(-10, 35), (10, 37), (30, 32), (35, 28), (43, 12), (51, 10), (40, -5),
     (35, -20), (20, -35), (15, -20), (10, -5), (-5, 5), (-17, 15),
     (-17, 25)],
    [(-10, 36), (-9, 43), (0, 48), (-5, 50), (5, 53), (8, 57), (18, 56),
     (21, 55), (28, 60), (30, 70), (40, 68), (45, 55), (40, 45), (30, 36),
     (23, 36), (19, 40), (12, 44), (3, 42), (-2, 37)],
    [(40, 68), (60, 70), (90, 75), (120, 77), (160, 70), (180, 66),
     (162, 60), (158, 52), (142, 45), (135, 35), (127, 35), (120, 30),
     (110, 20), (105, 10), (100, 8), (95, 16), (90, 22), (80, 8), (75, 20),
     (65, 25), (55, 25), (50, 29), (43, 12), (40, 30)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -17)],
]

# (story number, longitude, latitude); 3 is at Mercury and 6 is Bitcoin,
# so neither has an Earth pin — the note under the map says so.
PINS = [(1, 56.5, 26.5), (2, -115.1, 36.2), (4, 34.5, 31.5), (5, 2.35, 48.85),
        (7, 4.35, 50.85), (8, 30.7, 36.9), (9, -80.7, 28.4),
        (10, 106.2, -6.0), (11, 25.0, 59.5), (12, 128.5, -7.8),
        (13, -47.9, -15.8), (14, 6.1, 46.2), (15, -0.1, 51.5),
        (16, 12.5, 41.9)]
# Marker nudges (px) for pins that would otherwise sit on top of each
# other; a thin leader line joins the marker to its true spot.
PIN_OFFSETS = {7: (22, -18)}


def world_map(img, d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=MAPSEA, outline=INK, width=4)
    d.text((x0 + 20, y0 + 10), "WHERE IT HAPPENED",
           font=font(F_SANS, 30), fill=GOLD)
    mx0, my0, mx1, my1 = x0 + 16, y0 + 50, x1 - 16, y1 - 44
    mw, mh = mx1 - mx0, my1 - my0

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (90 - lat) / 180 * mh)

    for cont in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in cont],
                  fill=MAPLAND, outline=(200, 210, 190))
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        dx, dy = PIN_OFFSETS.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([(px, py), (px + dx, py + dy)], fill=LIGHT, width=3)
            px, py = px + dx, py + dy
        d.ellipse([px - 15, py - 15, px + 15, py + 15], fill=RED,
                  outline=LIGHT, width=3)
        d.text((px, py), str(n), font=font(F_SANS, 20), fill=LIGHT,
               anchor="mm")
    d.text((x0 + 20, y1 - 36),
           "3: Mercury. 6: Bitcoin \u2014 everywhere.",
           font=font(F_SANS_R, 20), fill=(215, 220, 230))


BRIEFS = [
    (17, "Russia fires 148 drones at Ukraine overnight \u2014 Kyiv"),
    (18, "Zelensky seeks ceasefires to evacuate 15 villages \u2014 Ukrinform"),
    (19, "Zelensky: Trump told Europe it overspends on Ukraine \u2014 Reuters"),
    (20, "UK signs drone-production deal with Ukraine \u2014 UK MoD"),
    (21, "Lebanon's Aoun: end occupation, disarm Hezbollah \u2014 AFP"),
    (22, "Board of Peace may hand Gaza back to UN \u2014 Ynet"),
    (23, "Iraq, Kata'ib Hezbollah agree joint presence \u2014 Al Jazeera"),
    (24, "Eritrean forces reported back in disputed Badme \u2014 ACLED"),
    (25, "129 bodies pulled from Gaza rubble \u2014 Anadolu"),
    (26, "Dragon splashes down with broken robot arm \u2014 NASA"),
    (27, "SpaceX launches classified USSF-317 mission \u2014 Army Recog."),
    (28, "Cyclone Akvan weakens to a low over Odisha \u2014 IMD"),
    (29, "Peru quake toll: 1 dead, 16 hurt, 93,000 cut off \u2014 Bus. Mirror"),
    (30, "Cyclone Xavier weakens; NZ relief lands \u2014 Cook Islands PM"),
    (31, "Qinghai quake M5.9 felt in Xining and Lanzhou \u2014 Xinhua"),
    (32, "Deep Sulu Sea quake M5.9, no damage \u2014 VolcanoDiscovery"),
    (33, "Australia edge England in MCG T20I thriller \u2014 SportsBriefly"),
    (34, "Rahul 136, Gill 98 as India reach 486-4 \u2014 IANS"),
    (35, "Zverev, Alcaraz reach ATP Finals decider \u2014 Reuters"),
    (36, "Chile rally 4-2; debutants earn historic point \u2014 Concacaf"),
    (37, "Royals win Nepal league final by 10 wickets \u2014 ESPNcricinfo"),
    (38, "MI Emirates win ILT20 opener by 52 runs \u2014 ScoreBlink"),
    (39, "Paciones edges Iimura by split decision \u2014 Powcast"),
    (40, "Modi opens 9.7 km Nitish Setu bridge \u2014 PMO India"),
    (41, "Storm kills 4, injures 162 in southern Brazil \u2014 AFP"),
    (42, "NSW rushes coalmine law to save 400 jobs \u2014 Guardian"),
    (43, "GTA VI festival rocks Miami with Travis Scott \u2014 PSU"),
    (44, "Nigeria boat toll rises to 24 after Friday capsize \u2014 Reuters"),
]


def briefs_band(d, x0, y0, x1, y1):
    d.text((x0, y0 + 6), "IN BRIEF  \u2014  17\u201344",
           font=font(F_SERIF, 32), fill=INK)
    rule(d, x0, y0 + 50, x1, RED, 4)
    col_w = (x1 - x0 - 40) / 2
    fnt = font(F_SANS_R, 19)
    for i, (n, text) in enumerate(BRIEFS):
        col = i // 14
        row = i % 14
        bx = x0 + col * (col_w + 40)
        by = y0 + 60 + row * 20
        line = f"{n}. {text}"
        assert d.textlength(line, font=fnt) <= col_w, \
            f"brief overflow: {line}"
        d.text((bx, by), line, font=fnt, fill=INK)


EXCLUDED_LEFT = [
    "Wall Street correction \u2014 Friday 20 Nov close",
    "ICJ Myanmar genocide ruling \u2014 Thursday 19 Nov",
    "Shenzhen summit (Trump\u2013Xi\u2013Putin) \u2014 Thursday 19 Nov",
    "GTA VI $3.79bn day-one sales \u2014 announced Friday 20 Nov",
]
EXCLUDED_RIGHT = [
    "Cyclone Akvan landfall \u2014 Friday 20 Nov",
    "Peru M6.7 quake (the quake itself) \u2014 Friday 20 Nov",
    "Palisades Fire verdict \u2014 Friday 20 Nov",
    "UK\u2013EU post-Brexit deals signed \u2014 Friday 20 Nov",
]


def date_check(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=(232, 226, 208), outline=INK,
                        width=4)
    d.text((x0 + 24, y0 + 10), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=font(F_SANS, 28), fill=DARKRED)
    fnt = font(F_SANS_R, 23)
    for i, t in enumerate(EXCLUDED_LEFT):
        d.text((x0 + 24, y0 + 48 + i * 25), "\u2715  " + t, font=fnt, fill=INK)
    for i, t in enumerate(EXCLUDED_RIGHT):
        d.text((x0 + 1010, y0 + 48 + i * 25), "\u2715  " + t, font=fnt,
               fill=INK)
    d.text((x0 + 24, y0 + 152),
           "Every story on this page happened, or was first reported, on "
           "Saturday 21 November 2026.",
           font=font(F_SANS, 23), fill=INK)
    d.text((x0 + 24, y0 + 180),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 NPR \u00b7 Nature "
           "\u00b7 NASA \u00b7 ANTARA \u00b7 IMD \u00b7 NWS \u00b7 USGS \u00b7 IANS "
           "\u00b7 ESPNcricinfo \u00b7 Concacaf \u00b7 Football-Italia "
           "\u00b7 Crypto.news \u00b7 Xinhua \u00b7 UKMTO",
           font=font(F_SANS, 18), fill=GREY)


def main():
    img = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    masthead(d, S)
    stat_strip(d, 250, 342)
    # three heroes
    hero_frame(img, d, (M, 354, 700, 710), 1, "STRAIT OF HORMUZ \u2014 UKMTO",
               "Two tankers struck in the Strait of Hormuz",
               "Hits 50 minutes apart, no casualties; Iran blames a mine "
               "\u2014 unverified. \u2014 UKMTO",
               hero_hormuz)
    hero_frame(img, d, (716, 354, 1380, 710), 2, "LAS VEGAS \u2014 FORMULA 1",
               "Verstappen wins wild Las Vegas Grand Prix",
               "75th career win; 352 overtakes, 35 lead changes; Norris "
               "0.639s back. \u2014 Formula1.com",
               hero_vegas)
    hero_frame(img, d, (1396, 354, 2012, 710), 3, "MERCURY \u2014 ESA / JAXA",
               "BepiColombo reaches Mercury after eight years",
               "37-minute burn puts it in orbit; only the second mission "
               "ever to do it. \u2014 Nature",
               hero_mercury)
    # panel row 1: four panels
    xs1 = [36, 534, 1032, 1530]
    xe1 = [518, 1016, 1514, 2012]
    panel(img, d, (xs1[0], 722, xe1[0], 960), 4, "GAZA \u2014 AID",
          "Food-truck strike kills three aid workers",
          "Israel: the dead were Islamic Jihad; WCK denies any link.",
          "Reuters", illu_truck)
    panel(img, d, (xs1[1], 722, xe1[1], 960), 5, "PARIS \u2014 PROTEST",
          "France marches for a sixth Saturday",
          "82,500 counted by police, 150,000 by organisers; 144 arrests.",
          "Reuters", illu_march)
    panel(img, d, (xs1[2], 722, xe1[2], 960), 6, "CRYPTO \u2014 SATURDAY",
          "Bitcoin dives to $55,130, then retakes $60,000",
          "Saturday's $2.7bn liquidation wave was the 11th-largest ever.",
          "Crypto.news", illu_bitcoin)
    panel(img, d, (xs1[3], 722, xe1[3], 960), 7, "BRUSSELS \u2014 TRADE",
          "EU and Indonesia sign landmark trade deal",
          "Zero tariffs on 90.4% of lines from day one; \u20ac600m a year "
          "saved.",
          "ANTARA", illu_handshake)
    # panel row 2: four panels
    panel(img, d, (xs1[0], 972, xe1[0], 1210), 8, "ANTALYA \u2014 COP31",
          "COP31 drags into a second day of overtime",
          "Fossil-fuel deadlock; EU says \u201ca good deal or no deal\u201d.",
          "Reuters", illu_clock)
    panel(img, d, (xs1[1], 972, xe1[1], 1210), 9, "FLORIDA \u2014 FLOOD",
          "St. Johns River breaks its 1953 flood record",
          "18.8 ft at Cocoa; 270 rescued as water may stay up for months.",
          "NWS", illu_flood)
    panel(img, d, (xs1[2], 972, xe1[2], 1210), 10, "BANTEN \u2014 FIRE",
          "Candy factory fire kills 3, 36 missing",
          "Blaze at the Milkita maker in Cikande; 15 rescued alive.",
          "Reuters", illu_fire)
    panel(img, d, (xs1[3], 972, xe1[3], 1210), 11, "GULF OF FINLAND \u2014 SHIP",
          "Drones set Russian cargo ship ablaze",
          "Sparta II hit twice; 16 crew out; Finland says Ukraine likely "
          "behind it.",
          "Reuters", illu_ship)
    # panel row 3: five panels
    xs3 = [36, 434, 832, 1230, 1628]
    xe3 = [418, 816, 1214, 1612, 2012]
    panel(img, d, (xs3[0], 1222, xe3[0], 1460), 12, "MALUKU \u2014 QUAKE",
          "M6.8 quake shakes Maluku islands",
          "BMKG first said 7.2; felt in Kupang; no tsunami.",
          "USGS", illu_quake, hsize=28, dsize=21)
    panel(img, d, (xs3[1], 1222, xe3[1], 1460), 13, "BRAS\u00cdLIA \u2014 ICU",
          "Bolsonaro in intensive care",
          "Bowel obstruction; stable at 71; serving 27 years.",
          "Reuters", illu_hospital, hsize=28, dsize=21)
    panel(img, d, (xs3[2], 1222, xe3[2], 1460), 14, "GENEVA \u2014 UN TALKS",
          "Killer-robot talks end with no binding rules",
          "Two more years of talks; US, Russia opposed.",
          "NPR", illu_robot, hsize=28, dsize=21)
    panel(img, d, (xs3[3], 1222, xe3[3], 1460), 15, "LONDON \u2014 FILM",
          "Princess of Wales reveals film \u2018Heal\u2019",
          "BBC film on her recovery; premieres 29 Nov.",
          "Reuters", illu_camera, hsize=28, dsize=21)
    panel(img, d, (xs3[4], 1222, xe3[4], 1460), 16, "ROME \u2014 SERIE A",
          "Malen hits four in Roma's 5-1 rout",
          "26 Serie A goals in 2026; equals a 1960 record.",
          "Football-Italia", illu_goal, hsize=28, dsize=21)
    # map + briefs band
    world_map(img, d, (M, 1472, 560, 1816))
    briefs_band(d, 580, 1472, 2012, 1816)
    # date check footer
    date_check(d, (M, 1828, 2012, 2036))
    small = img.resize((1024, 1024), Image.LANCZOS)
    small.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
