#!/usr/bin/env python3
"""Ghép bản hoàn chỉnh Chani's House từ bản dựng nền: 1080x1920, phụ đề sắc nét, logo, màn kết CTA, SRT, thumbnail.
Chạy:  python3 -I assemble.py <thư_mục_dự_án>   (thư mục có project.json, voices/, bgm.wav; đã chạy build.py ít nhất một lần)
Cần mục "chani" trong project.json (xem ../examples/cz028-project.json).
"""
import os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.abspath(sys.argv[1])
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # thư mục skill chani-viet-hoa-video
SKILL = os.path.join(os.path.dirname(os.path.dirname(SK)), "skills/viet-hoa-video/scripts/build.py")
ASSETS = os.path.join(SK, "assets")
os.chdir(HERE)
import json, shutil
CFG = json.load(open("project.json")); CH = CFG["chani"]
SLUG = CH["slug"]
OUT = f"out/chanis_house_{SLUG}_vi.mp4"
FONT_B = f"{ASSETS}/fonts/Nunito-800.ttf"; FONT_M = f"{ASSETS}/fonts/Nunito-700.ttf"
os.makedirs(os.path.expanduser("~/.fonts"), exist_ok=True)       # libass tìm font qua fontconfig
for fn in os.listdir(f"{ASSETS}/fonts"): shutil.copy(f"{ASSETS}/fonts/{fn}", os.path.expanduser("~/.fonts/"))
subprocess.run(["fc-cache", "-f"], capture_output=True)
GREEN, CREAM = (107, 145, 51), (255, 247, 234)
S = 1.5                       # 720 -> 1080
CTA = CH.get("cta_text", "Khám phá thêm tại Chani's House nha!")
CTA_VOICE = CH.get("cta_voice", "voices/s17.mp3")
OUTRO = 4.0
os.makedirs("out", exist_ok=True)

def run(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())
def sec(t):
    h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
def ts_srt(x):
    ms = round(x * 1000); return f"{ms//3600000:02d}:{ms%3600000//60000:02d}:{ms%60000//1000:02d},{ms%1000:03d}"

# 1) Bản nền KHÔNG phụ đề (để vẽ phụ đề ở 1080 cho sắc nét)
src = open(SKILL).read()
assert "ass={ass}[v]" in src
open("work/build_nosubs.py", "w").write(src.replace("ass={ass}[v]", "null[v]"))
import json
cfg = json.load(open("project.json")); cfg["out"] = "out/nosubs.mp4"; cfg["ass"] = "work/_unused.ass"
json.dump(cfg, open("work/project_nosubs.json", "w"), ensure_ascii=False)
# giữ nguyên đường dẫn tương đối: project phải nằm cùng thư mục gốc
os.replace("work/project_nosubs.json", "project_nosubs.json")
run(sys.executable, "-I", "work/build_nosubs.py", "project_nosubs.json")
os.remove("project_nosubs.json")
base_len = dur("out/nosubs.mp4")

# 2) ASS 1080: nhân tọa độ và cỡ chữ lên 1.5
ass = open("work/subs.ass").read()
ass = ass.replace("PlayResX: 720", "PlayResX: 1080").replace("PlayResY: 1280", "PlayResY: 1920")
ass = re.sub(r"\\pos\((\d+),(\d+)\)", lambda m: f"\\pos({round(int(m[1])*S)},{round(int(m[2])*S)})", ass)
ass = re.sub(r"\\fs(\d+)", lambda m: f"\\fs{round(int(m[1])*S)}", ass)
ass = re.sub(r"(Style: Vi,[^,]+,)38,(.*?),1,3,1,5", lambda m: f"{m[1]}57,{m[2]},1,5,1,5", ass)
open("work/subs1080.ass", "w").write(ass)

# 3) Huy hiệu logo (logo gốc, không đổi màu/hình; chỉ đặt trên nền trắng mờ để dễ đọc)
logo = Image.open(f"{ASSETS}/logo_chani.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())
LW = 190
lg = logo.resize((LW, round(LW * logo.height / logo.width)), Image.LANCZOS)
pad = 14
badge = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
ImageDraw.Draw(badge).rounded_rectangle([0, 0, badge.width - 1, badge.height - 1], 24, fill=(255, 255, 255, 215))
badge.alpha_composite(lg, (pad, pad)); badge.save("work/logo_badge.png")

# 4) Màn kết: logo lớn + CTA
card = Image.new("RGB", (1080, 1920), CREAM)
big = logo.resize((780, round(780 * logo.height / logo.width)), Image.LANCZOS)
cx = Image.new("RGBA", card.size, CREAM + (255,)); cx.alpha_composite(big, ((1080 - big.width) // 2, 470))
card = cx.convert("RGB"); d = ImageDraw.Draw(card)
f = ImageFont.truetype(FONT_B, 76)
y = 470 + big.height + 120
for line in ["Khám phá thêm tại", "Chani's House!"]:
    w = d.textlength(line, font=f); d.text(((1080 - w) / 2, y), line, font=f, fill=GREEN); y += 104
card.save("work/outro.png")

# 5) Ghép: video 1080 + phụ đề + huy hiệu logo -> nối màn kết; âm thanh = lời + nhạc nền (màn kết có câu CTA)
run("ffmpeg", "-loglevel", "error", "-y", "-i", CTA_VOICE, "-af",
    "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05,areverse,atempo=1.1",
    "-ar", "44100", "-ac", "1", "work/cta.wav")
fc = (f"[0:v]scale=1080:1920:flags=lanczos,ass=work/subs1080.ass[v0];[v0][3:v]overlay=W-w-34:34[vm];"
      f"[1:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.5[vo];[vm]fps=30[vm2];[vm2][vo]concat=n=2:v=1:a=0[v];"
      f"[2:a]adelay=350|350,apad=whole_dur={OUTRO},atrim=0:{OUTRO}[ca];"
      f"[4:a]atrim=0:{OUTRO},volume=0.14,afade=t=in:d=0.4,afade=t=out:st={OUTRO-1.2}:d=1.2[cb];[ca][cb]amix=inputs=2:duration=first:normalize=0[oa];"
      f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];[oa]aformat=sample_rates=44100:channel_layouts=stereo[a1];[a0][a1]concat=n=2:v=0:a=1[a]")
run("ffmpeg", "-loglevel", "error", "-y", "-i", "out/nosubs.mp4", "-loop", "1", "-t", str(OUTRO), "-i", "work/outro.png",
    "-i", "work/cta.wav", "-i", "work/logo_badge.png", "-i", "bgm.wav",
    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT)
print("Video:", OUT, round(dur(OUT), 2), "s")

# 6) SRT (gồm câu CTA ở màn kết)
cues = []
for m in re.finditer(r"Dialogue: 0,([\d:.]+),([\d:.]+),Vi,,0,0,0,,\{[^}]*\}(.*)", open("work/subs.ass").read()):
    cues.append((sec(m[1]), sec(m[2]), m[3].replace("\\N", "\n")))
cues.append((base_len + 0.35, base_len + 0.35 + 2.4, CTA))
with open(f"out/chanis_house_{SLUG}_vi.srt", "w") as fh:
    for i, (a, b, t) in enumerate(cues, 1): fh.write(f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n{t}\n\n")

# 7) Thumbnail 1080x1920: khung hình đồ chơi (không phụ đề) + tiêu đề SEO + logo
t_hero = next(a for a, b, t in cues if t.startswith(CH["hero_cue"])) + 0.7
run("ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t_hero:.2f}", "-i", "out/nosubs.mp4", "-frames:v", "1", "-vf", "scale=1080:1920:flags=lanczos", "work/hero.png")
im = Image.open("work/hero.png").convert("RGBA")
panel = Image.new("RGBA", im.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(panel)
pd.rectangle([0, 1285, 1080, 1765], fill=(255, 247, 234, 240))
im = Image.alpha_composite(im, panel); d = ImageDraw.Draw(im)
ft, fs = ImageFont.truetype(FONT_B, 92), ImageFont.truetype(FONT_M, 46)
y = 1335
for line in CH["thumb_title"]:
    w = d.textlength(line, font=ft); d.text(((1080 - w) / 2, y), line, font=ft, fill=GREEN); y += 118
d.line([(250, y + 14), (830, y + 14)], fill=(228, 126, 24), width=6)
for line in [CH["thumb_sub"]]:
    w = d.textlength(line, font=fs); d.text(((1080 - w) / 2, y + 46), line, font=fs, fill=(94, 70, 50))
tl = logo.resize((250, round(250 * logo.height / logo.width)), Image.LANCZOS)
plate = Image.new("RGBA", (tl.width + 28, tl.height + 28), (0, 0, 0, 0))
ImageDraw.Draw(plate).rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], 28, fill=(255, 255, 255, 225)); plate.alpha_composite(tl, (14, 14))
im.alpha_composite(plate, (1080 - plate.width - 40, 40))
im.convert("RGB").save(f"out/thumbnail_chanis_house_{SLUG}.jpg", quality=93)
print("Thumbnail xong; hero t =", round(t_hero, 2))
