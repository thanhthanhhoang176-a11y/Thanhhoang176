#!/usr/bin/env python3
"""Dựng video giới thiệu shop Mẹ Xoài (720x1280, ~32s) từ voice.mp3 + mốc thời gian từ."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 24
LEAD, TAIL = 0.5, 3.8
VOICE = "voice.mp3"
OUT = "shop_intro_me_xoai.mp4"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F = lambda s, b=True: ImageFont.truetype(B if b else R, s)

CREAM, MANGO, ORANGE, BROWN = (255, 244, 220), (255, 196, 61), (255, 138, 0), (74, 44, 10)
SHOPEE, FB, LEAF, WHITE = (238, 77, 45), (24, 119, 242), (76, 175, 80), (255, 255, 255)

# (bắt đầu, kết thúc, chữ) — giây theo thời gian của file giọng
CAPS = [
    (0.00, 0.85, "Chào mẹ nha!"),
    (1.01, 2.40, "Mẹ đang tìm đồ chơi vừa vui,"),
    (2.47, 4.40, "vừa giúp bé phát triển mỗi ngày đúng không?"),
    (4.52, 6.75, "Ghé ngay shop đồ chơi Mẹ Xoài nè!"),
    (7.07, 8.85, "Ở đây có nhiều món đồ chơi cho bé,"),
    (8.99, 12.05, "từ xếp hình, lắp ráp đến những món rèn sự khéo tay,"),
    (12.19, 13.60, "mẹ tha hồ lựa chọn."),
    (13.89, 15.30, "Mỗi món đều được chọn kỹ,"),
    (15.40, 17.90, "để bé chơi thật vui, mà mẹ cũng yên tâm."),
    (18.27, 20.30, "Mẹ tìm shop Mẹ Xoài trên Shopee,"),
    (20.43, 22.40, "tên là mexoai1706,"),
    (22.50, 25.60, "hoặc theo dõi trang Facebook để xem thêm nhiều món mới nha."),
    (25.84, 27.68 + TAIL, "Mẹ Xoài chờ mẹ và bé ghé chơi nè!"),
]
SCENES = [(-1, 4.4), (4.4, 6.95), (6.95, 13.7), (13.7, 18.1), (18.1, 99)]  # A hook, B tên, C loại, D chọn kỹ, E CTA


def ease_back(t):
    t = max(0.0, min(1.0, t)); c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def pop(t, t0, dur=0.45):
    return ease_back((t - t0) / dur) if t >= t0 else 0.0


def fade(t, t0, dur=0.3):
    return max(0.0, min(1.0, (t - t0) / dur))


def center_text(d, y, text, font, fill, cx=W // 2, shadow=None):
    w = d.textlength(text, font=font)
    if shadow:
        d.text((cx - w / 2 + 3, y + 4), text, font=font, fill=shadow)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def background(t):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):  # gradient kem -> vàng xoài
        k = y / H
        d.rectangle([0, y, W, y + 4], fill=tuple(int(CREAM[i] * (1 - k * .55) + MANGO[i] * k * .55) for i in range(3)))
    for i in range(9):  # bong bóng bay
        x = (i * 97 + 40) % W
        y = (H - (t * (30 + i * 7) + i * 170)) % (H + 200) - 100
        r = 26 + (i % 4) * 14
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
    return img


def mango(d, cx, cy, s):
    d.ellipse([cx - 110 * s, cy - 90 * s, cx + 110 * s, cy + 100 * s], fill=ORANGE)
    d.ellipse([cx - 80 * s, cy - 60 * s, cx - 20 * s, cy - 10 * s], fill=(255, 176, 60))
    d.polygon([(cx, cy - 88 * s), (cx + 70 * s, cy - 140 * s), (cx + 100 * s, cy - 95 * s), (cx + 20 * s, cy - 80 * s)], fill=LEAF)
    # mặt cười
    for ex in (-35, 35):
        d.ellipse([cx + (ex - 8) * s, cy - 12 * s, cx + (ex + 8) * s, cy + 8 * s], fill=BROWN)
    d.arc([cx - 30 * s, cy + 5 * s, cx + 30 * s, cy + 50 * s], 20, 160, fill=BROWN, width=max(2, int(6 * s)))
    for ex in (-62, 62):
        d.ellipse([cx + (ex - 14) * s, cy + 18 * s, cx + (ex + 14) * s, cy + 36 * s], fill=(255, 120, 100))


def card(d, cx, cy, w, h, fill, s=1.0):
    w, h = w * s, h * s
    d.rounded_rectangle([cx - w / 2 + 6, cy - h / 2 + 8, cx + w / 2 + 6, cy + h / 2 + 8], 36, fill=(0, 0, 0, 40) if False else (210, 170, 90))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 36, fill=fill)


def scene_A(d, t):
    s = pop(t, 0.1)
    mango(d, W // 2, 330, 1.25 * s)
    if t > 1.0:
        a = pop(t, 1.0)
        center_text(d, 560, "Mẹ đang tìm", F(62), BROWN)
        center_text(d, 640, "đồ chơi cho bé?", F(62), ORANGE)
    if t > 2.6:
        center_text(d, 760, "Vui mà vẫn giúp bé", F(44), BROWN)
        center_text(d, 815, "phát triển mỗi ngày", F(44), BROWN)


def scene_B(d, t, t0):
    k = pop(t, t0, 0.5)
    mango(d, W // 2, 330, 1.0 * k)
    card(d, W // 2, 640, 600, 250, WHITE, k)
    if k > 0.6:
        center_text(d, 540, "SHOP ĐỒ CHƠI", F(44), BROWN)
        center_text(d, 600, "MẸ XOÀI", F(104), ORANGE)
    if t - t0 > 0.9:
        pill(d, W // 2, 850, "Shopee: mexoai1706", F(40), SHOPEE, WHITE)


def pill(d, cx, cy, text, font, fill, fg):
    w = d.textlength(text, font=font) + 70
    d.rounded_rectangle([cx - w / 2, cy - 42, cx + w / 2, cy + 42], 42, fill=fill)
    center_text(d, cy - 26, text, font, fg)


def scene_C(d, t, t0):
    center_text(d, 150, "Trong shop có", F(52), BROWN)
    items = [("Xếp hình", 9.0, ORANGE), ("Lắp ráp", 9.9, LEAF), ("Rèn khéo tay", 10.8, (156, 90, 220)), ("Bé chơi mê ly!", 12.2, SHOPEE)]
    for i, (txt, ts, col) in enumerate(items):
        k = pop(t + 0.0, ts - 0.25 - t0 * 0 , 0.45) if False else pop(t, ts - 0.2, 0.45)
        if k <= 0:
            continue
        cy = 330 + i * 150
        w, h = 560 * k, 110 * k
        d.rounded_rectangle([W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2], 55, fill=col)
        if k > 0.7:
            center_text(d, cy - 28, txt, F(52), WHITE)


def scene_D(d, t, t0):
    k = pop(t, t0, 0.5)
    r = 130 * k
    d.ellipse([W / 2 - r, 330 - r, W / 2 + r, 330 + r], fill=LEAF)
    if k > 0.5:  # dấu tick
        d.line([(W / 2 - 60, 335), (W / 2 - 15, 385), (W / 2 + 70, 275)], fill=WHITE, width=26, joint="curve")
    if t - t0 > 0.3:
        center_text(d, 520, "Chọn kỹ từng món", F(66), BROWN)
    if t - t0 > 1.6:
        center_text(d, 630, "Bé chơi vui", F(70), ORANGE)
        center_text(d, 720, "Mẹ yên tâm", F(70), ORANGE)


def scene_E(d, t):
    k1 = pop(t, 18.3 + LEAD * 0, 0.5)
    card(d, W // 2, 330, 600, 190, SHOPEE, k1)
    if k1 > 0.6:
        center_text(d, 262, "Tìm trên Shopee", F(40), WHITE)
        center_text(d, 316, "mexoai1706", F(72), WHITE)
    hl = pop(t, 20.7, 0.4)
    if hl:
        d.rounded_rectangle([W / 2 - 300 - 8 * hl, 330 - 95 - 8 * hl, W / 2 + 300 + 8 * hl, 330 + 95 + 8 * hl], 40, outline=MANGO, width=8)
    k2 = pop(t, 22.5, 0.5)
    card(d, W // 2, 600, 600, 190, FB, k2)
    if k2 > 0.6:
        center_text(d, 530, "Theo dõi trang", F(40), WHITE)
        center_text(d, 584, "Facebook Mẹ Xoài", F(54), WHITE)
        center_text(d, 658, "để xem món mới mỗi ngày", F(28, False), WHITE)
    if t > 25.84:
        mango(d, W // 2, 850, 0.65 * pop(t, 25.84, 0.5))


def caption(img, t):
    d = ImageDraw.Draw(img)
    for a, b, txt in CAPS:
        if a - 0.05 <= t <= b:
            font = F(46)
            lines = wrap(d, txt, font, 600)
            h = len(lines) * 62 + 30
            y0 = 1040
            d.rounded_rectangle([50, y0, W - 50, y0 + h], 30, fill=(255, 255, 255))
            for i, ln in enumerate(lines):
                center_text(d, y0 + 14 + i * 62, ln, font, BROWN)
            return


def frame(tv):
    """tv = thời gian theo file giọng (âm khi đang ở đoạn lead-in)."""
    img = background(tv + LEAD)
    d = ImageDraw.Draw(img)
    for i, (a, b) in enumerate(SCENES):
        if a <= tv < b:
            lt = tv - a
            if i == 0: scene_A(d, max(0, tv + 0.3))
            elif i == 1: scene_B(d, tv, a)
            elif i == 2: scene_C(d, tv, a)
            elif i == 3: scene_D(d, tv, a)
            else: scene_E(d, tv)
    caption(img, tv)
    return img


def main():
    total = LEAD + 27.68 + TAIL
    n = int(total * FPS)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", VOICE, "-filter_complex", f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad=whole_dur={total:.2f}[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS - LEAD).tobytes())
    p.stdin.close(); p.wait()
    print("OK", OUT, round(total, 1), "s")


if __name__ == "__main__":
    if len(sys.argv) > 1:  # xem thử một khung: build.py <giây>
        frame(float(sys.argv[1])).save(f"prev_{sys.argv[1]}.png")
    else:
        main()
