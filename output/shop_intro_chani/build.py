#!/usr/bin/env python3
"""Video giới thiệu CHANI's House (720x1280, ~31s): ảnh + logo thật của shop, giọng ElevenLabs.
Chạy: python3 build.py          -> chani_house_intro.mp4
      python3 build.py <giây>   -> prev_<giây>.png (xem thử 1 khung)"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 24
LEAD, TAIL, VOICE_LEN = 0.5, 5.0, 25.34
VOICE, OUT = "voice.mp3", "chani_house_intro.mp4"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F = lambda s, b=True: ImageFont.truetype(B if b else R, s)

CREAM, GREEN, ORANGE, CORAL = (253, 246, 236), (95, 150, 50), (214, 110, 25), (255, 107, 87)
BROWN, WHITE, SHOPEE, FB = (74, 44, 10), (255, 255, 255), (238, 77, 45), (24, 119, 242)

IMG = {k: Image.open(f"assets/{k}.jpg").convert("RGB") for k in ("abc", "kaleido", "scissors", "cover")}
LOGO = Image.open("assets/logo.png").convert("RGB")

END = VOICE_LEN + TAIL
# (bắt đầu, kết thúc, chữ) theo mốc từng từ của file giọng
CAPS = [
    (0.00, 2.70, "Mẹ ơi, đang tìm đồ chơi chính hãng cho bé phải không?"),
    (2.88, 4.20, "Ghé ngay CHANI's House nè!"),
    (4.42, 6.70, "Ở đây có đồ chơi giáo dục của nhiều thương hiệu cao cấp"),
    (6.80, 10.30, "như Mideer, Joan Miró, TopBright, Boby,"),
    (10.41, 12.95, "hợp với nhiều lứa tuổi, từ bé sơ sinh trở đi."),
    (13.29, 14.80, "CHANI còn miễn phí gói quà,"),
    (14.86, 16.65, "1 đổi 1 nếu lỗi từ nhà sản xuất,"),
    (16.74, 18.45, "và giao hỏa tốc nội thành nữa nha."),
    (18.71, 20.55, "Mẹ tìm CHANI's House trên Shopee,"),
    (20.60, 23.05, "hoặc Facebook, để chọn quà cho bé liền nè."),
    (23.16, END, "CHANI, in dấu tuổi thơ con!"),
]
SCENES = [(-1, 2.85), (2.85, 6.6), (6.6, 10.4), (10.4, 13.2), (13.2, 18.6), (18.6, 99)]


def ease(t):
    t = max(0.0, min(1.0, t)); c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def pop(t, t0, dur=0.45):
    return ease((t - t0) / dur) if t >= t0 else 0.0


def ctext(d, y, text, font, fill, cx=W // 2):
    w = d.textlength(text, font=font)
    d.text((cx - w / 2, y), text, font=font, fill=fill)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]


def photo(img, key, t, t0, y0=0, size=700):
    """Ảnh vuông với hiệu ứng zoom nhẹ (Ken Burns), cắt bo góc dưới."""
    src = IMG[key]; z = 1.0 + 0.10 * min(1.0, (t - t0) / 4.0)
    c = int(src.width / z); x = (src.width - c) // 2; y = (src.height - c) // 2
    im = src.crop((x, y, x + c, y + c)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, -80, size, size], 60, fill=255)
    img.paste(im, ((W - size) // 2, y0), m)


def bg():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 36, W, H], fill=CORAL)
    return img


def logo(img, cx, cy, width, k=1.0):
    w = int(width * k)
    if w < 10: return
    h = int(LOGO.height * w / LOGO.width)
    lg = LOGO.resize((w, h), Image.LANCZOS)
    pad = 24
    card = Image.new("RGB", (w + 2 * pad, h + 2 * pad), WHITE)
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width, card.height], 36, fill=255)
    card.paste(lg, (pad, pad))
    img.paste(card, (int(cx - card.width / 2), int(cy - card.height / 2)), m)


def pill(d, cx, cy, text, font, fill, fg=WHITE, k=1.0):
    if k <= 0.05: return
    w = (d.textlength(text, font=font) + 70) * k
    d.rounded_rectangle([cx - w / 2, cy - 42 * k, cx + w / 2, cy + 42 * k], int(42 * k), fill=fill)
    if k > 0.7: ctext(d, cy - font.size * 0.62, text, font, fg, cx)


def scene1(img, d, t):
    photo(img, "abc", t, -1, 0, 700)
    ctext(d, 740, "Đồ chơi chính hãng", F(56), BROWN)
    ctext(d, 815, "cho bé yêu", F(72), ORANGE)


def scene2(img, d, t, t0):
    k = pop(t, t0, 0.55)
    logo(img, W // 2, 380, 520, k)
    if t - t0 > 0.7:
        ctext(d, 700, "Đồ chơi giáo dục cho bé", F(40), BROWN)
    if t - t0 > 1.4:
        pill(d, W // 2, 830, "In dấu tuổi thơ con", F(42), GREEN, WHITE, pop(t, t0 + 1.4))


def scene3(img, d, t, t0):
    photo(img, "kaleido", t, t0, 0, 700)
    cols = [(GREEN, 6.9), (ORANGE, 7.8), (CORAL, 8.8), ((156, 90, 220), 9.6)]
    names = ["Mideer", "Joan Miró", "TopBright", "Boby"]
    for i, ((c, ts), n) in enumerate(zip(cols, names)):
        x = 190 if i % 2 == 0 else 530
        y = 790 + (i // 2) * 110
        pill(d, x, y, n, F(38), c, WHITE, pop(t, ts - 0.15, 0.4))


def scene4(img, d, t, t0):
    photo(img, "scissors", t, t0, 0, 700)
    ctext(d, 745, "Hợp mọi lứa tuổi", F(56), BROWN)
    pill(d, W // 2, 860, "Từ bé sơ sinh trở đi", F(40), ORANGE, WHITE, pop(t, t0 + 0.6))


def scene5(img, d, t, t0):
    keys = ["abc", "kaleido", "scissors"]
    for i, k in enumerate(keys):
        a = pop(t, t0 + i * 0.12, 0.5)
        s = int(210 * a)
        if s > 8:
            im = IMG[k].resize((s, s), Image.LANCZOS)
            img.paste(im, (40 + i * 225 + (210 - s) // 2, 120 + (210 - s) // 2))
    items = [("Miễn phí gói quà", 13.3, GREEN), ("1 đổi 1 nếu lỗi từ nhà sản xuất", 14.8, ORANGE), ("Giao hỏa tốc nội thành", 16.7, CORAL)]
    for i, (txt, ts, c) in enumerate(items):
        k = pop(t, ts - 0.15, 0.45)
        if k <= 0: continue
        cy = 520 + i * 140
        w, h = 620 * k, 110 * k
        d.rounded_rectangle([W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2], 40, fill=c)
        if k > 0.8:
            f = F(32 if len(txt) > 24 else 44)
            ctext(d, cy - f.size * 0.62, txt, f, WHITE)


def scene6(img, d, t):
    logo(img, W // 2, 290, 440, pop(t, 18.6, 0.5))
    k1 = pop(t, 18.9, 0.5)
    if k1 > 0:
        w, h = 620 * k1, 200 * k1
        d.rounded_rectangle([W / 2 - w / 2, 640 - h / 2, W / 2 + w / 2, 640 + h / 2], 40, fill=SHOPEE)
        if k1 > 0.8:
            ctext(d, 570, "Tìm trên Shopee", F(34), WHITE)
            ctext(d, 616, "CHANI's House", F(60), WHITE)
            ctext(d, 696, "shopee.vn/mexoai1706", F(28, False), WHITE)
    k2 = pop(t, 20.6, 0.5)
    if k2 > 0:
        w, h = 620 * k2, 170 * k2
        d.rounded_rectangle([W / 2 - w / 2, 860 - h / 2, W / 2 + w / 2, 860 + h / 2], 40, fill=FB)
        if k2 > 0.8:
            ctext(d, 802, "Theo dõi Facebook", F(34), WHITE)
            ctext(d, 848, "CHANI's House", F(52), WHITE)
            ctext(d, 916, "facebook.com/chanishouseforkids", F(24, False), WHITE)


def caption(img, t):
    d = ImageDraw.Draw(img)
    for a, b, txt in CAPS:
        if a - 0.05 <= t <= b:
            font = F(44)
            lines = wrap(d, txt, font, 600)
            h = len(lines) * 60 + 28
            y0 = 1070 if len(lines) < 3 else 1050
            d.rounded_rectangle([50, y0, W - 50, y0 + h], 30, fill=WHITE, outline=GREEN, width=4)
            for i, ln in enumerate(lines):
                ctext(d, y0 + 12 + i * 60, ln, font, BROWN)
            return


def frame(t):
    img = bg(); d = ImageDraw.Draw(img)
    for i, (a, b) in enumerate(SCENES):
        if a <= t < b:
            if i == 0: scene1(img, d, t)
            elif i == 1: scene2(img, d, t, a)
            elif i == 2: scene3(img, d, t, a)
            elif i == 3: scene4(img, d, t, a)
            elif i == 4: scene5(img, d, t, a)
            else: scene6(img, d, t)
    d = ImageDraw.Draw(img)
    if t >= 18.6:
        ctext(d, 1000, "Hotline: 08.28.10.3579", F(30, False), BROWN)
    caption(img, t)
    return img


def main():
    total = LEAD + END
    n = int(total * FPS)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", VOICE, "-filter_complex", f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad=whole_dur={total:.2f}[a]",
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
           "-t", f"{total:.2f}", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS - LEAD).tobytes())
    p.stdin.close(); p.wait()
    print("OK", OUT, round(total, 1), "s")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        frame(float(sys.argv[1])).save(f"prev_{sys.argv[1]}.png")
    else:
        main()
