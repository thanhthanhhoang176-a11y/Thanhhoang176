#!/usr/bin/env python3
"""Dựng quảng cáo CHANI's House 1080x1920 @30fps từ ảnh/logo thật của shop + giọng ElevenLabs + nhạc/SFX tự tổng hợp.
  python3 audio.py                 # tạo mix.wav
  python3 build.py                 # dựng chani_house_ad.mp4
  python3 build.py <giây> [...]    # xuất khung xem thử prev_<giây>.png"""
import math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import LEAD, TOTAL, SC, TRANS, PHRASES

W, H, FPS = 1080, 1920, 30
OUT = "chani_house_ad.mp4"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fc = {}


def F(size, bold=True):
    k = (max(2, int(size)), bold)
    if k not in _fc: _fc[k] = ImageFont.truetype(B if bold else R, k[0])
    return _fc[k]


# bảng màu lấy từ logo/ảnh bìa của shop
CREAM, GREEN, ORANGE, CORAL = (253, 246, 236), (95, 150, 50), (214, 110, 25), (255, 107, 87)
YELLOW, SKY, PURPLE, PINK = (255, 205, 60), (90, 200, 230), (150, 90, 215), (255, 150, 180)
BROWN, WHITE, SHOPEE, FB = (74, 44, 10), (255, 255, 255), (238, 77, 45), (24, 119, 242)
OUTLINE = (70, 30, 60)

IMG = {k: Image.open(f"assets/{k}.jpg").convert("RGB") for k in ("abc", "kaleido", "scissors", "cover")}
LOGO = Image.open("assets/logo_clean.png").convert("RGB")
CROP = {  # vùng cắt (x0, y0, x1, y1) trên ảnh gốc 1024x1024
    "letters": ("abc", (10, 10, 720, 720)), "numbers": ("abc", (260, 240, 990, 970)),
    "abc": ("abc", (0, 0, 1024, 1024)), "kaleido": ("kaleido", (0, 0, 1024, 1024)), "scissors": ("scissors", (0, 0, 1024, 1024)),
}
THEMES = [None, (CREAM, YELLOW), (PINK, CORAL), (SKY, (140, 225, 245)), (PURPLE, (200, 150, 255)),
          (GREEN, (150, 205, 100)), (YELLOW, ORANGE), (CORAL, PINK), (CREAM, (190, 230, 150))]


def ease_back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def ease_io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def pop(t, t0, dur=0.45):
    return ease_back((t - t0) / dur) if t >= t0 else 0.0


_gcache = {}


def gradient(c1, c2):
    k = (c1, c2)
    if k not in _gcache:
        y = np.linspace(0, 1, H)[:, None, None]
        a = np.array(c1, float)[None, None, :]; b = np.array(c2, float)[None, None, :]
        _gcache[k] = np.repeat((a * (1 - y) + b * y).astype(np.uint8), W, axis=1)
    return Image.fromarray(_gcache[k])


def star(d, cx, cy, r, fill, rot=0.0):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4; rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def confetti(d, t, seed, colors):
    for i in range(16):
        x0 = (i * 211 + seed * 97) % W; sp = 40 + (i * 29 + seed * 13) % 70
        y = (H + 200 - ((t * sp + i * 173 + seed * 311) % (H + 400)))
        x = x0 + 40 * math.sin(t * 1.2 + i)
        r = 18 + (i * 7) % 26; col = colors[i % len(colors)]
        kind = (i + seed) % 4
        if kind == 0: d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        elif kind == 1: star(d, x, y, r * 1.3, col, t * 0.8 + i)
        elif kind == 2: d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=7)
        else:
            a = t * 0.9 + i
            d.polygon([(x + r * math.cos(a + k * math.pi / 2), y + r * math.sin(a + k * math.pi / 2)) for k in range(4)], fill=col)


def background(t, idx):
    c1, c2 = THEMES[idx] if idx < len(THEMES) and THEMES[idx] else (CREAM, YELLOW)
    img = gradient(c1, c2).copy(); d = ImageDraw.Draw(img)
    lite = tuple(min(255, int(v * 0.4 + 255 * 0.6)) for v in c2)
    confetti(d, t, idx, [lite, WHITE, tuple(min(255, int(v * 0.5 + 128)) for v in c1)])
    return img


def stext(d, xy, text, size, fill=WHITE, sw=10, bold=True, anchor="mm", stroke=OUTLINE):
    d.text(xy, text, font=F(size, bold), fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=stroke)


def chip(d, cx, cy, text, size, fill, fg=WHITE, k=1.0, pad=60, sw=0):
    if k <= 0.05: return
    f = F(size * k); w = d.textlength(text, font=f) + pad * 2 * k; h = size * 1.75 * k
    d.rounded_rectangle([cx - w / 2, cy - h / 2 + 8, cx + w / 2, cy + h / 2 + 8], int(h / 2), fill=(0, 0, 0, 0) if False else tuple(int(v * 0.6) for v in fill))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], int(h / 2), fill=fill)
    d.text((cx, cy + 2), text, font=f, fill=fg, anchor="mm", stroke_width=sw, stroke_fill=OUTLINE)


def crop_img(key, zoom=1.0, shift=(0.0, 0.0)):
    src, (x0, y0, x1, y1) = CROP[key]; im = IMG[src]
    cx, cy = (x0 + x1) / 2 + shift[0] * (x1 - x0), (y0 + y1) / 2 + shift[1] * (y1 - y0)
    s = (x1 - x0) / zoom
    return im.crop((int(cx - s / 2), int(cy - s / 2), int(cx + s / 2), int(cy + s / 2)))


_mcache = {}


def rmask(size, r):
    k = (size, r)
    if k not in _mcache:
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], r, fill=255); _mcache[k] = m
    return _mcache[k]


def sticker(img, key, t, t0, cx, cy, size=860, rot=-3.0, zoom=(1.0, 1.1), shift=(0.0, 0.0), dur=3.5, k_override=None):
    """Ảnh sản phẩm dạng sticker viền trắng, bật nảy vào, lơ lửng nhẹ, zoom Ken Burns bên trong."""
    k = pop(t, t0, 0.55) if k_override is None else k_override
    if k <= 0.03: return
    z = zoom[0] + (zoom[1] - zoom[0]) * min(1, max(0, (t - t0) / dur))
    inner = crop_img(key, z, shift).resize((size, size), Image.LANCZOS)
    b = 22; tot = size + 2 * b
    card = Image.new("RGBA", (tot + 80, tot + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 62, 40 + tot, 62 + tot], 90, fill=(40, 20, 50, 110))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    cd = ImageDraw.Draw(card); cd.rounded_rectangle([40, 40, 40 + tot, 40 + tot], 90, fill=WHITE)
    card.paste(inner, (40 + b, 40 + b), rmask(size, 70))
    ang = rot + 1.6 * math.sin(t * 2.0) + (1 - k) * 12
    s = max(0.05, k) * (1 + 0.012 * math.sin(t * 3.0))
    card = card.resize((int(card.width * s), int(card.height * s)), Image.BICUBIC).rotate(ang, Image.BICUBIC, expand=True)
    fy = 10 * math.sin(t * 2.2)
    img.paste(card, (int(cx - card.width / 2), int(cy + fy - card.height / 2)), card)


def bursts(d, t, t0, cx, cy, r0=420, n=10, life=0.9):
    x = (t - t0) / life
    if x < 0 or x > 1: return
    for i in range(n):
        a = i * 2 * math.pi / n + 0.4; rr = r0 * (0.5 + 0.7 * ease_io(x))
        s = 34 * (1 - x) + 6
        star(d, cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.9, s, YELLOW if i % 2 else WHITE, a)


def logo_card(t, t0, width, sweep=True):
    k = pop(t, t0, 0.6)
    w = int(width * max(0.01, k)); h = int(LOGO.height * w / LOGO.width); pad = int(36 * k)
    if w < 20: return None
    lg = LOGO.resize((w, h), Image.LANCZOS)
    card = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (255, 255, 255, 255)); card.paste(lg, (pad, pad))
    if sweep:  # light sweep chạy ngang qua logo
        x = (t - t0 - 0.7) / 0.7
        if 0 <= x <= 1:
            arr = np.array(card).astype(np.float32); hh, ww = arr.shape[:2]
            xs = np.arange(ww)[None, :] - (x * (ww + 300) - 150) - np.arange(hh)[:, None] * 0.5
            band = np.clip(1 - np.abs(xs) / 70, 0, 1)[..., None]
            arr[..., :3] = arr[..., :3] * (1 - 0.65 * band) + 255 * 0.65 * band
            card = Image.fromarray(arr.astype(np.uint8), "RGBA")
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], 60, fill=255)
    out = Image.new("RGBA", card.size, (0, 0, 0, 0)); out.paste(card, (0, 0), m)
    return out


def paste_rgba(img, card, cx, cy, ang=0.0):
    if card is None: return
    if ang: card = card.rotate(ang, Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    sh.paste((40, 20, 50, 100), (40, 60), card.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(18))
    img.paste(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)), sh)
    img.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), card)


# ---------------------------- CẢNH ----------------------------
def scene_hook(t, tv):
    shots = [("abc", -1, 0.7), ("kaleido", 0.7, 1.5), ("scissors", 1.5, 3)]
    for key, a, b in shots:
        if a <= tv < b: break
    ts = tv - a
    bgi = crop_img(key).resize((54, 54), Image.BILINEAR).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    img = Image.blend(bgi, Image.new("RGB", (W, H), YELLOW), 0.25); d = ImageDraw.Draw(img)
    confetti(d, t, 3, [WHITE, YELLOW, CORAL])
    punch = 1.28 - 0.28 * ease_io(ts / 0.35)  # zoom-in punch mỗi cú cắt
    sticker(img, key, t, 0, W // 2, 990, int(820 * punch), rot=-2 + (a * 7) % 5, zoom=(1.0, 1.08), dur=1.0, k_override=1.0)
    d = ImageDraw.Draw(img)
    k1 = pop(tv, -0.1, 0.4); k2 = pop(tv, 0.35, 0.4)
    if k1 > 0: stext(d, (W // 2, 270), "THẾ GIỚI ĐỒ CHƠI", 84 * k1, YELLOW, 14)
    if k2 > 0: stext(d, (W // 2, 400), "SIÊU THÚ VỊ!", 118 * k2, WHITE, 16)
    bursts(d, tv, a + 0.05, W // 2, 990, 470, 8, 0.6)
    return img


def scene_logo(t, tv):
    t0 = SC[1]; img = background(t, 1); d = ImageDraw.Draw(img)
    card = logo_card(tv, t0 + 0.05, 860)
    paste_rgba(img, card, W // 2, 700, -2 * (1 - pop(tv, t0, 0.6)) * 8)
    d = ImageDraw.Draw(img)
    bursts(d, tv, t0 + 0.1, W // 2, 700, 560, 12, 1.0)
    chip(d, W // 2, 1140, "ĐỒ CHƠI GIÁO DỤC CHÍNH HÃNG", 40, GREEN, WHITE, pop(tv, t0 + 1.0, 0.5), 50)
    chip(d, W // 2, 1260, "In dấu tuổi thơ con", 44, ORANGE, WHITE, pop(tv, t0 + 1.4, 0.5), 60)
    return img


def scene_product(t, tv, i, key, title, sub, rot, shift=(0, 0), tag=None):
    t0 = SC[i]; img = background(t, i); d = ImageDraw.Draw(img)
    sticker(img, key, tv, t0 + 0.05, W // 2, 690, 800, rot, (1.0, 1.12), shift)
    d = ImageDraw.Draw(img)
    bursts(d, tv, t0 + 0.35, W // 2, 690, 560, 10, 0.9)
    k = pop(tv, t0 + 0.4, 0.45)
    if k > 0: stext(d, (W // 2, 1180), title, 104 * k, WHITE, 14)
    chip(d, W // 2, 1275, sub, 40, CORAL if i != 2 else PURPLE, WHITE, pop(tv, t0 + 0.75, 0.45), 50)
    if tag:
        kk = pop(tv, t0 + 0.9, 0.5)
        if kk > 0: chip(d, 800, 330, tag, 50, ORANGE, WHITE, kk, 50)
    return img


def scene_brands(t, tv):
    t0 = SC[6]; img = background(t, 6); d = ImageDraw.Draw(img)
    for i, key in enumerate(["abc", "kaleido", "scissors"]):
        sticker(img, key, tv, t0 + 0.15 + i * 0.12, 220 + i * 320, 1010, 300, (-6, 3, -4)[i], (1.0, 1.1), (0, 0), 3)
    d = ImageDraw.Draw(img)
    stext(d, (W // 2, 330), "ĐỦ THƯƠNG HIỆU", 86 * pop(tv, t0 + 0.2, 0.4), WHITE, 14)
    stext(d, (W // 2, 440), "CAO CẤP", 110 * pop(tv, t0 + 0.4, 0.4), BROWN, 0, stroke=None) if False else stext(d, (W // 2, 440), "CAO CẤP", 110 * pop(tv, t0 + 0.4, 0.4), YELLOW, 14)
    brands = [("Mideer", 19.26, GREEN, (300, 620)), ("Joan Miró", 19.85, PURPLE, (780, 620)),
              ("TopBright", 20.68, CORAL, (300, 790)), ("Boby", 21.56, SKY, (780, 790))]
    for name, ts, col, (x, y) in brands:
        chip(d, x, y, name, 56, col, WHITE, pop(tv, ts - 0.1, 0.45), 52)
        if 0 <= tv - ts < 0.7: bursts(d, tv, ts, x, y, 150, 6, 0.7)
    return img


def draw_gift(d, cx, cy, s):
    d.rectangle([cx - 38 * s, cy - 10 * s, cx + 38 * s, cy + 40 * s], fill=WHITE)
    d.rectangle([cx - 44 * s, cy - 30 * s, cx + 44 * s, cy - 8 * s], fill=WHITE)
    d.rectangle([cx - 7 * s, cy - 30 * s, cx + 7 * s, cy + 40 * s], fill=CORAL)
    d.ellipse([cx - 30 * s, cy - 58 * s, cx - 2 * s, cy - 28 * s], outline=CORAL, width=int(8 * s))
    d.ellipse([cx + 2 * s, cy - 58 * s, cx + 30 * s, cy - 28 * s], outline=CORAL, width=int(8 * s))


def draw_swap(d, cx, cy, s):
    f = F(60 * s); d.text((cx, cy), "1:1", font=f, fill=WHITE, anchor="mm")
    d.arc([cx - 50 * s, cy - 50 * s, cx + 50 * s, cy + 50 * s], 200, 340, fill=WHITE, width=int(7 * s))
    d.arc([cx - 50 * s, cy - 50 * s, cx + 50 * s, cy + 50 * s], 20, 160, fill=WHITE, width=int(7 * s))


def draw_truck(d, cx, cy, s):
    d.rectangle([cx - 52 * s, cy - 30 * s, cx + 8 * s, cy + 22 * s], fill=WHITE)
    d.polygon([(cx + 12 * s, cy - 14 * s), (cx + 40 * s, cy - 14 * s), (cx + 54 * s, cy + 6 * s), (cx + 54 * s, cy + 22 * s), (cx + 12 * s, cy + 22 * s)], fill=WHITE)
    for x in (-30, 30):
        d.ellipse([cx + (x - 12) * s, cy + 12 * s, cx + (x + 12) * s, cy + 36 * s], fill=BROWN, outline=WHITE, width=int(4 * s))


def scene_perks(t, tv):
    t0 = SC[7]; img = background(t, 7); d = ImageDraw.Draw(img)
    stext(d, (W // 2, 330), "TẠI CHANI'S HOUSE", 80 * pop(tv, t0 + 0.1, 0.45), WHITE, 14)
    cards = [("Miễn phí gói quà", 22.66, GREEN, draw_gift, 66), ("1 đổi 1 nếu lỗi từ nhà sản xuất", 24.40, ORANGE, draw_swap, 50),
             ("Giao hỏa tốc nội thành", 26.70, PURPLE, draw_truck, 60)]
    for i, (txt, ts, col, icon, fs) in enumerate(cards):
        k = pop(tv, ts - 0.1, 0.5); cy = 620 + i * 245
        if k <= 0.03: continue
        w, h = 940 * k, 200 * k
        d.rounded_rectangle([W / 2 - w / 2 + 8, cy - h / 2 + 12, W / 2 + w / 2 + 8, cy + h / 2 + 12], 60, fill=tuple(int(v * .55) for v in col))
        d.rounded_rectangle([W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2], 60, fill=col)
        if k > 0.8:
            d.ellipse([150 - 70, cy - 70, 150 + 70, cy + 70], fill=tuple(min(255, int(v * 0.75 + 40)) for v in col))
            icon(d, 150, cy, 1.0)
            d.text((260, cy), txt, font=F(fs * (0.8 if len(txt) > 24 else 1)), fill=WHITE, anchor="lm", stroke_width=6, stroke_fill=OUTLINE)
        if 0 <= tv - ts < 0.8: bursts(d, tv, ts, W // 2, cy, 380, 8, 0.8)
    return img


def scene_cta(t, tv):
    t0 = SC[8]; img = background(t, 8); d = ImageDraw.Draw(img)
    lines = [("KHÁM PHÁ ĐỒ CHƠI", 82, GREEN), ("YÊU THÍCH NGAY", 82, ORANGE), ("HÔM NAY!", 112, CORAL)]
    for i, (txt, sz, col) in enumerate(lines):
        k = pop(tv, t0 + 0.15 + i * 0.18, 0.45)
        if k > 0: stext(d, (W // 2, 280 + i * 118), txt, sz * k, col, 12, stroke=WHITE)
    card = logo_card(tv, t0 + 0.6, 380, sweep=True)
    paste_rgba(img, card, W // 2, 790)
    d = ImageDraw.Draw(img)
    pulse = 1 + 0.04 * math.sin(tv * 7)
    for (name, sub, col, y, ts) in [("SHOPEE", "CHANI's House", SHOPEE, 1035, 29.0), ("FACEBOOK", "CHANI's House", FB, 1180, 29.6)]:
        k = pop(tv, ts - 0.1, 0.45)
        if k <= 0.03: continue
        k *= pulse if tv > ts + 0.5 else 1
        w, h = 900 * k, 130 * k
        d.rounded_rectangle([W / 2 - w / 2 + 6, y - h / 2 + 10, W / 2 + w / 2 + 6, y + h / 2 + 10], 65, fill=tuple(int(v * .55) for v in col))
        d.rounded_rectangle([W / 2 - w / 2, y - h / 2, W / 2 + w / 2, y + h / 2], 65, fill=col)
        if k > 0.8:
            d.text((W / 2 - 400 * k, y), name, font=F(46 * k), fill=WHITE, anchor="lm")
            d.text((W / 2 + 430 * k, y), sub, font=F(40 * k), fill=WHITE, anchor="rm")
        if 0 <= tv - ts < 0.7: bursts(d, tv, ts, W // 2, y, 560, 8, 0.7)
    if tv > 30.2:
        d.text((W // 2, 1295), "Hotline: 08.28.10.3579", font=F(40, False), fill=BROWN, anchor="mm")
    return img


def render_scene(i, tv):
    t = tv + LEAD
    if i == 0: return scene_hook(t, tv)
    if i == 1: return scene_logo(t, tv)
    if i == 2: return scene_product(t, tv, 2, "letters", "BẢNG CHỮ CÁI", "Đầy màu sắc cho bé", -3)
    if i == 3: return scene_product(t, tv, 3, "numbers", "BẢNG SỐ", "Đếm 1 – 2 – 3 thật dễ", 3, (0.0, 0.0))
    if i == 4: return scene_product(t, tv, 4, "kaleido", "KÍNH VẠN HOA", "Xoay một vòng, hoa văn đổi liền", -2, (0.0, 0.0), "MIDEER")
    if i == 5: return scene_product(t, tv, 5, "scissors", "KÉO CHO BÉ", "Tập cắt giấy", 2)
    if i == 6: return scene_brands(t, tv)
    if i == 7: return scene_perks(t, tv)
    return scene_cta(t, tv)


def scene_index(tv):
    for i in range(len(SC) - 1):
        if SC[i] <= tv < SC[i + 1]: return i
    return len(SC) - 2


def motion_blur(arr, px):
    if px < 2: return arr
    n = int(min(9, max(3, px // 12))); acc = np.zeros_like(arr, dtype=np.float32)
    for k in range(n): acc += np.roll(arr, int((k - n / 2) * px / n), axis=1)
    return (acc / n).astype(np.uint8)


def compose(tv):
    i = scene_index(tv)
    # chuyển cảnh quanh điểm biên sắp tới / vừa qua
    for j in (i, i + 1):
        if 1 <= j <= 8:
            tb = SC[j]; half = 0.14 if TRANS[j] == "whip" else 0.10
            if abs(tv - tb) < half:
                a = render_scene(j - 1, tv); b = render_scene(j, tv); p = (tv - (tb - half)) / (2 * half)
                if TRANS[j] == "flash":
                    f = 1 - abs(2 * p - 1)  # sáng dần rồi tắt
                    base = a if p < 0.5 else b
                    return Image.blend(base, Image.new("RGB", (W, H), WHITE), min(1, f * 1.15))
                off = int(ease_io(p) * W); sign = -1 if j % 2 == 0 else 1
                A = np.array(a); Bm = np.array(b); bl = int(260 * math.sin(math.pi * p))
                A = motion_blur(np.roll(A, sign * off, axis=1), bl); Bm = motion_blur(np.roll(Bm, sign * (off - W), axis=1), bl)
                out = np.zeros_like(A)
                if sign < 0: out[:, :W - off] = A[:, :W - off]; out[:, W - off:] = Bm[:, W - off:]
                else: out[:, off:] = A[:, off:]; out[:, :off] = Bm[:, :off]
                return Image.fromarray(out)
    return render_scene(i, tv)


def captions(img, tv):
    d = ImageDraw.Draw(img)
    for a, b, text in PHRASES:
        if a - 0.05 <= tv <= b + 0.22:
            toks = text.split(); n = len(toks)
            size = 66
            # chia dòng
            lines, cur = [], []
            for tk in toks:
                test = " ".join(cur + [tk])
                if d.textlength(test, font=F(size)) <= 920 or not cur: cur.append(tk)
                else: lines.append(cur); cur = [tk]
            lines.append(cur)
            slide = int(26 * (1 - ease_io((tv - a + 0.05) / 0.18)))
            y_last = 1500 + slide; idx = 0
            for li, line in enumerate(lines):
                y = y_last - (len(lines) - 1 - li) * 92
                widths = [d.textlength(tk, font=F(size)) for tk in line]; sp = d.textlength(" ", font=F(size))
                x = W / 2 - (sum(widths) + sp * (len(line) - 1)) / 2
                for tk, w in zip(line, widths):
                    ts = a + (b - a) * idx / n; te = a + (b - a) * (idx + 1) / n
                    cur_tok = ts <= tv < te
                    col = YELLOW if cur_tok else WHITE
                    f = F(size * (1.12 if cur_tok else 1.0))
                    d.text((x + w / 2, y), tk, font=f, fill=col, anchor="ms", stroke_width=11, stroke_fill=OUTLINE)
                    x += w + sp; idx += 1
            return


def frame(fi):
    tv = fi / FPS - LEAD
    img = compose(tv)
    captions(img, tv)
    return img.tobytes()


def main():
    n = int(TOTAL * FPS)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", "mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, b in enumerate(pool.imap(frame, range(n), chunksize=4)):
            p.stdin.write(b)
            if k % 150 == 0: print(k, "/", n, flush=True)
    p.stdin.close(); p.wait(); print("OK", OUT, round(TOTAL, 1), "s")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for s in sys.argv[1:]:
            fi = int(round((float(s) + LEAD) * FPS))
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"prev_{s}.png")
    else:
        main()
