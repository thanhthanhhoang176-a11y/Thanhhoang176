"""Mốc thời gian dùng chung cho hình (build.py) và âm thanh (audio.py). Đơn vị: giây."""
LEAD, VOICE_LEN, TAIL = 0.3, 32.6, 4.0
TOTAL = LEAD + VOICE_LEN + TAIL

# Điểm bắt đầu từng cảnh theo thời gian của giọng đọc (tv); video t = tv + LEAD
SC = [-LEAD, 2.4, 5.5, 8.5, 11.9, 15.4, 17.8, 22.5, 28.0, 99.0]
# kiểu chuyển vào cảnh i (i>=1): 'flash' hoặc 'whip'
TRANS = [None, "flash", "whip", "whip", "whip", "whip", "whip", "whip", "flash"]

# (bắt đầu, kết thúc, chữ hiển thị) — lấy từ mốc từng từ của file giọng
PHRASES = [
    (0.00, 2.26, "Mẹ ơi, thế giới đồ chơi siêu thú vị đây rồi!"),
    (2.66, 3.43, "CHANI's House,"),
    (3.65, 5.34, "đồ chơi giáo dục chính hãng cho bé."),
    (5.68, 6.83, "Bảng chữ cái đầy màu sắc,"),
    (7.05, 8.30, "cho bé tập nhận mặt chữ."),
    (8.75, 9.67, "Bảng số vui nhộn,"),
    (9.89, 11.56, "đếm 1, 2, 3 thật dễ."),
    (12.10, 13.18, "Kính vạn hoa Mideer,"),
    (13.36, 15.30, "xoay một vòng, hoa văn đổi liền!"),
    (15.52, 16.27, "Kéo nhỏ xinh,"),
    (16.45, 17.66, "cho bé tập cắt giấy."),
    (17.88, 18.92, "Đủ thương hiệu cao cấp,"),
    (19.26, 22.21, "Mideer, Joan Miró, TopBright, Boby."),
    (22.66, 24.20, "CHANI còn miễn phí gói quà,"),
    (24.42, 26.48, "1 đổi 1 nếu lỗi từ nhà sản xuất,"),
    (26.70, 27.71, "giao hỏa tốc nội thành."),
    (28.11, 30.15, "Tìm CHANI's House trên Shopee hoặc Facebook,"),
    (30.49, 32.60, "khám phá đồ chơi yêu thích ngay hôm nay!"),
]


def _abs(tv): return tv + LEAD


def _sfx():
    e = []
    add = lambda n, tv, g=1.0: e.append((n, _abs(tv), g))
    # hook: 3 cú cắt nhanh
    add("pop", -0.2, 0.9); add("sparkle", 0.3, 0.6)
    add("whoosh", 0.55, 0.7); add("pop", 0.75, 0.8)
    add("whoosh", 1.35, 0.7); add("pop", 1.55, 0.8)
    add("riser", 1.4, 0.9)
    add("impact", 2.4, 1.0); add("chime", 2.45, 0.9); add("sparkle", 2.9, 0.7)
    for i in range(2, 9):
        b = SC[i]
        if TRANS[i] == "whip":
            add("whoosh", b - 0.2, 0.9)
            add("pop", b + 0.12, 0.9); add("boing", b + 0.22, 0.5); add("sparkle", b + 0.55, 0.55)
            if i <= 5: add("pop", b + 0.7, 0.7)  # chip chữ
    for tv in (19.26, 19.85, 20.68, 21.56): add("pop", tv - 0.05, 0.8)
    for tv in (22.66, 24.40, 26.70): add("boing", tv - 0.05, 0.6); add("sparkle", tv + 0.1, 0.45)
    # CTA
    add("riser", 27.0, 0.9); add("impact", 28.0, 1.0); add("sparkle", 28.2, 0.7)
    add("click", 29.0, 0.9); add("click", 29.6, 0.9); add("boing", 30.5, 0.6)
    add("stinger", 32.7, 1.0)
    return e


SFX = _sfx()
