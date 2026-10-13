#!/usr/bin/env python3
"""Quét TỰ ĐỘNG từng khung hình để tìm chữ trang trí tiếng Trung còn sót (tấm chữ vàng/cam, dấu ✅ xanh, chữ đỏ).
Dùng:  python3 -I scan_leftovers.py <video_nguồn.mp4> <video_dựng.mp4> [vùng_trên_cùng_%=55]
In ra các đoạn thời gian bị phát hiện ở NGUỒN (để biết tấm chữ nào có) và ở BẢN DỰNG (phải rỗng).
Lưu ý: tia lửa vàng trang trí (không có chữ) cũng có thể bị dò ra; mở khung đó xem để chắc.
"""
import glob, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

def scan(video, fps=20, top_pct=55):
    d = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-vf", f"fps={fps},scale=360:-1", f"{d}/f_%05d.png"], check=True)
    ts = []
    for i, p in enumerate(sorted(glob.glob(d + "/f_*.png"))):
        a = np.asarray(Image.open(p).convert("RGB")).astype(int)
        a = a[: int(a.shape[0] * top_pct / 100)]
        R, G, B = a[..., 0], a[..., 1], a[..., 2]
        green = ((G > 150) & (R < 90) & (B < 140) & (G - R > 90)).sum()      # dấu ✅
        yellow = ((R > 230) & (G > 190) & (B < 70)).sum()                     # chữ vàng đậm
        orange = ((R > 240) & (G > 110) & (G < 170) & (B < 60)).sum()         # chữ cam
        red = ((R > 200) & (G < 70) & (B < 70)).sum()                         # chữ đỏ
        if green > 25 or yellow > 60 or orange > 150 or red > 150:
            ts.append(round(i / fps, 2))
    segs = []
    for t in ts:
        if segs and t - segs[-1][1] <= 0.11: segs[-1][1] = t
        else: segs.append([t, t])
    for f in glob.glob(d + "/*.png"): os.remove(f)
    return segs

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    top = float(sys.argv[3]) if len(sys.argv) > 3 else 55
    print("Nguồn (các tấm chữ có mặt, giây gốc):", scan(src, top_pct=top))
    res = scan(out, top_pct=top)
    print("Bản dựng (phải rỗng):", res)
    sys.exit(1 if res else 0)
