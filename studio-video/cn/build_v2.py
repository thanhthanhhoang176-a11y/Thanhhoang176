"""Dựng video Nukied bản Việt hoá v2: mỗi cảnh gốc kéo giãn khớp một câu thoại."""
import subprocess, wave, numpy as np
from PIL import ImageFont

TEMPO = 1.25        # tăng tốc giọng đọc
GAP = 0.18          # nghỉ giữa các câu
SHOTS = [(0, 2.267), (2.267, 5.2), (5.2, 8.4), (8.4, 11.433), (11.433, 14.267),
         (14.267, 18.067), (18.067, 20.833), (20.833, 23.467), (23.467, 25.8)]
LINES = [
    "Cắt lát rau củ vui thế này, bé nào mà không mê!",
    "Bé nhà mình cắt cà rốt, cắt dưa leo mà vui lắm luôn!",
    "Đồ chơi này đơn giản lắm, bé chỉ cần ấn xuống rồi trượt qua trượt lại,",
    "là từng lát rơi ra liền, bé thấy mới lạ và thích mê!",
    "Vừa chơi vừa rèn cho bé nhanh tay, nhanh mắt, nhanh trí nữa đó!",
    "Cắt xong, bé tự xếp các lát vào hộp, giúp bé khéo tay và biết tập trung hơn.",
    "Bộ có cà rốt, dưa leo và cà tím, hình dáng đáng yêu lắm.",
    "Chỉ cần đẩy tới, kéo lui là cắt xong ngay!",
    "Chơi đã tay mà dọn cũng dễ, cất vào hộp là gọn!",
]
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MAXW = 670

def sh(*a): subprocess.run(a, check=True)
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).strip())

# 1) giọng: tăng tốc từng câu, đặt vào đúng đầu mỗi cảnh
sr = 44100; D = []; speech = []
for i in range(9):
    sh("ffmpeg","-loglevel","error","-y","-i",f"v2/t{i+1}.wav","-af",f"atempo={TEMPO}",f"v2/p{i+1}.wav")
    d = dur(f"v2/p{i+1}.wav"); speech.append(d)
    shot = SHOTS[i][1]-SHOTS[i][0]
    D.append(max(d+GAP, shot*1.0))        # cảnh không bao giờ nhanh hơn gốc
starts = np.concatenate([[0], np.cumsum(D)])
total = starts[-1]
voice = np.zeros(int(sr*total)+sr)
for i in range(9):
    w = wave.open(f"v2/p{i+1}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768; w.close()
    o = int((starts[i]+0.04)*sr); voice[o:o+len(x)] += x
voice = voice[:int(sr*total)]
w = wave.open("v2/voice.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((np.clip(voice,-1,1)*32767).astype(np.int16).tobytes()); w.close()

# 2) phụ đề: ngắt dòng theo độ rộng thật của chữ, mỗi cảnh một cue liền mạch
def wrap(text, fs):
    """Ngắt tối đa 2 dòng cân đối (không để dòng mồ côi); trả về >2 dòng nếu không vừa."""
    f = ImageFont.truetype(FONT, fs); words = text.split()
    if f.getlength(text) <= MAXW: return [text]
    best = None
    for k in range(1, len(words)):
        l1, l2 = " ".join(words[:k]), " ".join(words[k:])
        m = max(f.getlength(l1), f.getlength(l2))
        pen = 0 if words[k-1].endswith(",") else 1000   # ưu tiên ngắt sau dấu phẩy
        if best is None or m + pen < best[0] + best[2]: best = (m, [l1, l2], pen)
    return best[1] if best[0] <= MAXW else best[1] + ["!"]
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
NL = chr(92) + 'N'
SPLIT = {2: "Đồ chơi này đơn giản lắm,"}   # câu dài: tách 2 cue theo nhịp đọc để chữ to, dễ đọc
def cue(a, b, t):
    for fs in (40, 36, 33, 30, 28):
        ls = wrap(t, fs)
        if len(ls) <= 2: break
    assert len(ls) <= 2, (t, ls)
    return f"Dialogue: 0,{ts(a)},{ts(b)},Vi,,0,0,0,,{{\\an5\\pos(360,940)\\fs{fs}}}{NL.join(ls)}\n"
ev = ""
for i, t in enumerate(LINES):
    if i in SPLIT:
        p1 = SPLIT[i]; p2 = t[len(p1):].strip()
        r = len(p1.split()) / len(t.split())
        mid = starts[i] + 0.04 + speech[i] * r + GAP / 2
        ev += cue(starts[i], mid, p1) + cue(mid, starts[i+1], p2)
    else:
        ev += cue(starts[i], starts[i+1], t)
open("vi2.ass","w").write(f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 2
PlayResX: 720
PlayResY: 1280
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Vi,Liberation Sans,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,1,5,10,10,0,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
{ev}""")

# 3) hình: che logo/chữ Trung ở thời gian gốc, rồi kéo giãn từng cảnh
src = ("[0:v]delogo=x=10:y=1205:w=700:h=62:enable='lt(t,4.2)',"
       "delogo=x=12:y=10:w=110:h=70:enable='gte(t,3.0)',"
       "delogo=x=470:y=10:w=245:h=70:enable='gte(t,3.0)',"
       "split=2[base][bl];[bl]crop=700:94:10:893,boxblur=20:3[blur];"
       "[base][blur]overlay=10:893,drawbox=x=10:y=893:w=700:h=94:color=black@0.5:t=fill[clean]")
parts=[]; names=[]
n=len(SHOTS)
split_out="".join(f"[c{i}]" for i in range(n))
chain = src + f";[clean]split={n}{split_out}"
for i,(a,b) in enumerate(SHOTS):
    f = D[i]/(b-a)
    chain += f";[c{i}]trim={a}:{b},setpts=(PTS-STARTPTS)*{f:.5f},fps=30[s{i}]"
    names.append(f"[s{i}]")
chain += f";{''.join(names)}concat=n={n}:v=1:a=0[cat]"
chain += (";[cat]drawtext=fontfile=%s:text='Nukied':fontsize=30:fontcolor=white:borderw=2:bordercolor=black@0.6:x=w-tw-26:y=26,"
          "ass=vi2.ass[v]" % FONT)
sh("ffmpeg","-loglevel","error","-y","-i","source.mp4","-i","v2/voice.wav","-i","bgm.wav",
   "-filter_complex", chain + f";[2:a]atrim=0:{total:.2f},volume=0.14,afade=t=out:st={total-1.6:.2f}:d=1.6[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]",
   "-map","[v]","-map","[a]","-t",f"{total:.2f}","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","vi-nukied-v2.mp4")
print("tổng", round(total,2), "giây; hệ số kéo giãn:", [round(D[i]/(SHOTS[i][1]-SHOTS[i][0]),2) for i in range(n)])
