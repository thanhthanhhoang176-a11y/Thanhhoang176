#!/usr/bin/env python3
"""Dựng video Việt hoá: mỗi cảnh gốc kéo giãn khớp một câu thoại, che chữ/logo, phụ đề, nhạc nền.

Dùng:  python3 -I build.py project.json
Cần:   ffmpeg (có libass), python3 + numpy + Pillow.
Xem project.json mẫu ở ../examples/nukied-project.json
"""
import json, os, subprocess, sys, wave
import numpy as np
from PIL import ImageFont

cfg = json.load(open(sys.argv[1]))
base = os.path.dirname(os.path.abspath(sys.argv[1]))
P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)

SRC, OUT = P(cfg["source"]), P(cfg["out"])
TEMPO = cfg.get("tempo", 1.25)          # tăng tốc giọng đọc (1.2-1.3 hợp quảng cáo)
GAP = cfg.get("gap", 0.18)              # nghỉ giữa các câu (giây)
SHOTS = cfg["shots"]                    # [[bắt_đầu, kết_thúc], ...] theo giây của video gốc
LINES = cfg["lines"]                    # đúng 1 câu / cảnh
VOICE = P(cfg["voice_dir"])             # chứa t1.wav ... tN.wav (đã cắt lặng, giọng chưa tăng tốc)
SPLIT = {int(k): v for k, v in cfg.get("split", {}).items()}   # {chỉ_số_cảnh: "đoạn đầu,"}
SUB = cfg.get("subtitle", {})
BAND = SUB.get("band", {"x": 10, "y": 893, "w": 700, "h": 94, "opacity": 0.5})
FONT = SUB.get("font", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
FONT_NAME = SUB.get("font_name", "Liberation Sans")
SIZES = SUB.get("sizes", [40, 36, 33, 30, 28])
MAXW = SUB.get("max_width", 670)
POS = SUB.get("pos", [360, 940])
W, H = cfg.get("size", [720, 1280])
assert len(SHOTS) == len(LINES), "Số cảnh phải bằng số câu thoại"
N = len(SHOTS)

def run(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())

# 1) Giọng: tăng tốc từng câu, đặt đúng đầu mỗi cảnh
sr = 44100
D, speech = [], []
tmp = P(cfg.get("work_dir", "work")); os.makedirs(tmp, exist_ok=True)
for i in range(N):
    run("ffmpeg", "-loglevel", "error", "-y", "-i", f"{VOICE}/t{i+1}.wav", "-af", f"atempo={TEMPO}", f"{tmp}/p{i+1}.wav")
    d = dur(f"{tmp}/p{i+1}.wav"); speech.append(d)
    D.append(max(d + GAP, SHOTS[i][1] - SHOTS[i][0]))      # cảnh không bao giờ nhanh hơn gốc
starts = np.concatenate([[0], np.cumsum(D)]); total = float(starts[-1])
voice = np.zeros(int(sr * total) + sr)
for i in range(N):
    w = wave.open(f"{tmp}/p{i+1}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    o = int((starts[i] + 0.04) * sr); voice[o:o + len(x)] += x
voice = voice[:int(sr * total)]
w = wave.open(f"{tmp}/voice.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

# 2) Phụ đề: ngắt tối đa 2 dòng, ưu tiên sau dấu phẩy, đo độ rộng chữ thật
def wrap(text, fs):
    f = ImageFont.truetype(FONT, fs); words = text.split()
    if f.getlength(text) <= MAXW: return [text]
    best = None
    for k in range(1, len(words)):
        l1, l2 = " ".join(words[:k]), " ".join(words[k:])
        m = max(f.getlength(l1), f.getlength(l2))
        pen = 0 if words[k - 1].endswith(",") else 1000
        if best is None or m + pen < best[0] + best[2]: best = (m, [l1, l2], pen)
    return best[1] if best[0] <= MAXW else best[1] + ["!"]
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
NL = chr(92) + "N"
def cue(a, b, t):
    for fs in SIZES:
        ls = wrap(t, fs)
        if len(ls) <= 2: break
    assert len(ls) <= 2, f"Câu quá dài, hãy rút gọn hoặc dùng 'split': {t}"
    return f"Dialogue: 0,{ts(a)},{ts(b)},Vi,,0,0,0,,{{\\an5\\pos({POS[0]},{POS[1]})\\fs{fs}}}{NL.join(ls)}\n"
ev = ""
for i, t in enumerate(LINES):
    if i in SPLIT:
        p1 = SPLIT[i]; p2 = t[len(p1):].strip()
        mid = starts[i] + 0.04 + speech[i] * len(p1.split()) / len(t.split()) + GAP / 2
        ev += cue(starts[i], mid, p1) + cue(mid, starts[i + 1], p2)
    else:
        ev += cue(starts[i], starts[i + 1], t)
ass = P(cfg.get("ass", "subs.ass"))
open(ass, "w").write(f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 2
PlayResX: {W}
PlayResY: {H}
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Vi,{FONT_NAME},38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,1,5,10,10,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
{ev}""")

# 3) Hình: che logo (delogo theo cửa sổ thời gian GỐC) + dải mờ che phụ đề cũ, rồi kéo giãn từng cảnh
f = "[0:v]"
for d in cfg.get("delogo", []):
    en = f"between(t,{d.get('from', 0)},{d.get('to', 9999)})"
    f += f"delogo=x={d['x']}:y={d['y']}:w={d['w']}:h={d['h']}:enable='{en}',"
b = BAND
f += (f"split=2[base][bl];[bl]crop={b['w']}:{b['h']}:{b['x']}:{b['y']},boxblur=20:3[blur];"
      f"[base][blur]overlay={b['x']}:{b['y']},drawbox=x={b['x']}:y={b['y']}:w={b['w']}:h={b['h']}:color=black@{b.get('opacity', 0.5)}:t=fill[clean]")
chain = f + f";[clean]split={N}" + "".join(f"[c{i}]" for i in range(N))
for i, (a, e) in enumerate(SHOTS):
    chain += f";[c{i}]trim={a}:{e},setpts=(PTS-STARTPTS)*{D[i]/(e-a):.5f},fps=30[s{i}]"
chain += ";" + "".join(f"[s{i}]" for i in range(N)) + f"concat=n={N}:v=1:a=0[cat]"
credit = cfg.get("credit_text")
chain += ";[cat]" + (f"drawtext=fontfile={FONT}:text='{credit}':fontsize=30:fontcolor=white:borderw=2:x=w-tw-26:y=26," if credit else "") + f"ass={ass}[v]"
cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", SRC, "-i", f"{tmp}/voice.wav"]
bgm = cfg.get("bgm")
if bgm:
    cmd += ["-i", P(bgm)]
    chain += f";[2:a]atrim=0:{total:.2f},volume={cfg.get('bgm_volume', 0.14)},afade=t=out:st={total-1.6:.2f}:d=1.6[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]"
else:
    chain += ";[1:a]anull[a]"
cmd += ["-filter_complex", chain, "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", OUT]
run(*cmd)
print(f"Xong: {OUT}  ({total:.1f}s)  hệ số kéo giãn từng cảnh:", [round(D[i] / (SHOTS[i][1] - SHOTS[i][0]), 2) for i in range(N)])
for i, d in enumerate(D):
    r = d / (SHOTS[i][1] - SHOTS[i][0])
    if r > 1.45: print(f"  ! Cảnh {i+1} kéo giãn {r:.2f}x (chậm quá): rút gọn câu thoại cảnh này")
