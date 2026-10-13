import json,subprocess,textwrap
import urllib.request
VOICE="cgSgspJ2msm6clMCkdW9" # Jessica (ElevenLabs), khóa do proxy môi trường tự chèn
def gen(i,text):
    body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"style":0.2,"speed":1.1}}).encode()
    rq=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",body,{"Content-Type":"application/json"})
    open(f"v{i}.mp3","wb").write(urllib.request.urlopen(rq).read())
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"v{i}.mp3","-ar","22050",f"v{i}b.wav"],check=True)
S=[ # start,end, 中文, tiếng Việt, từ khóa tô màu
(1.9,4.9,"宝宝会坐以后，就不要玩这些声光电玩具了","Bé biết ngồi rồi, mình bỏ đồ chơi đèn nhạc nha!",["đèn nhạc"]),
(4.9,7.9,"儿保建议换成切切乐这种能培养动手能力的","Bác sĩ nhi khuyên chọn bộ cắt cắt vui, bé khéo tay nè!",["cắt cắt vui"]),
(7.9,10.4,"因为精细运动好的宝宝一般也更聪明","Bé vận động tinh tốt thường thông minh hơn nè.",["vận động tinh"]),
(10.4,13.4,"宝宝每次掰开的过程，精细运动都能得到锻炼","Mỗi lần bé bẻ ra là vận động tinh được tập luyện nè.",["vận động tinh"]),
(13.4,16.9,"不同形状的水果可以提升色彩认知和形状认知","Trái cây đủ hình dạng giúp bé biết màu sắc, hình khối nữa.",["màu sắc","hình khối"]),
(16.9,19.4,"宝宝亲密接触的玩具就不要买杂牌的了","Đồ bé chạm gần, đừng mua hàng trôi nổi nha.",[]),
(19.4,21.9,"纽奇这个用的都是植物原料材质","Nukied làm từ nguyên liệu thực vật luôn nè.",["nguyên liệu thực vật"]),
(21.9,23.4,"宝宝啃咬也没关系","Bé cắn cũng không sao nè.",["không sao"]),
(23.4,25.4,"还能带宝宝认识很多蔬菜和水果","Còn giúp bé làm quen rau củ quả nữa.",["rau củ quả"]),
(25.4,27.9,"不玩的时候就和宝宝一起收纳起来","Chơi xong, mình cùng bé cất gọn nha.",[]),
(27.9,29.9,"宝宝大一点以后还可以用来过家家","Lớn hơn xíu còn chơi đồ hàng được nè.",["đồ hàng"]),
(29.9,31.9,"一直玩到3岁都没问题","Chơi tới ba tuổi vẫn ổn luôn nha!",["ba tuổi"]),
(32.0,35.4,"(câu kết thêm theo yêu cầu)","Hãy subscribe cho kênh Ghiền Mì Gõ để không bỏ lỡ những video hấp dẫn.",["subscribe"]),
]
json.dump(S,open("script.json","w"),ensure_ascii=False)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
ins=[];fl=[]
for i,(a,b,zh,vi,k) in enumerate(S):
    gen(i,vi.replace('Nukied','Nu kít'))
    r=max(1.0,dur(f"v{i}b.wav")/(b-a-0.08));print(i,round(r,2),vi)
    assert r<=1.35
    ins+=["-i",f"v{i}b.wav"];fl.append(f"[{i+2}:a]atempo={r:.3f},aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={int(a*1000)}|{int(a*1000)}[d{i}]")
mix="".join(f"[d{i}]" for i in range(len(S)))
fc=";".join(fl)+f";{mix}amix=inputs={len(S)}:normalize=0:dropout_transition=0,volume=2.2,apad=whole_dur=35.54,asplit=2[dub][sc];[1:a]volume=2.2,apad=whole_dur=35.54[bg];[bg][sc]sidechaincompress=threshold=0.06:ratio=2.5:attack=20:release=250[duck];[duck][dub]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]"
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","clean.mp4","-i","inst.wav",*ins,"-filter_complex",fc,"-map","[a]","-t","35.54","mix.wav"],check=True)
# ASS
def t(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60;return f"{h}:{m:02}:{s:05.2f}"
def wrap(s,k=()):
    if len(s)<=26: return [s]
    if s.startswith('Hãy subscribe'): return ['Hãy subscribe cho kênh','Ghiền Mì Gõ để không bỏ lỡ','những video hấp dẫn.']
    if len(s)>50:
        w=s.split(' ');n=len(w);return [' '.join(w[:n//3+1]),' '.join(w[n//3+1:2*n//3+1]),' '.join(w[2*n//3+1:])]
    best=None
    for i,c in enumerate(s):
        if c!=" ": continue
        if any(s.find(w)<i<s.find(w)+len(w) for w in k if w in s): continue
        sc=abs(i-len(s)/2)
        if best is None or sc<best[0]: best=(sc,i)
    i=best[1];return [s[:i],s[i+1:]]
ev=[]
for a,b,zh,vi,k in S:
    L=wrap(vi,k)
    txt="\\N".join(L)
    for w in k:
        txt=txt.replace(w,"{\\c&H00D7FF&}"+w+"{\\c&HFFFFFF&}")
    ev.append(f"Dialogue: 0,{t(a)},{t(b)},V,,0,0,0,,{txt}")
open("vi.ass","w").write("""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: V,DejaVu Sans,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,1.5,2,40,40,285,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""+"\n".join(ev)+"\n")
def ts(x): h=int(x//3600);m=int(x%3600//60);s=x%60;return f"{h:02}:{m:02}:{s:06.3f}".replace('.',',')
def ts(x): h=int(x//3600);m=int(x%3600//60);s=x%60;return f"{h:02}:{m:02}:{s:06.3f}".replace('.',',')
out=[]
for i,(a,b,zh,vi,k) in enumerate(S):
    out.append(str(i+1)+"\n"+ts(a)+" --> "+ts(b)+"\n"+"\n".join(wrap(vi,k))+"\n")
open("vi.srt","w").write("\n".join(out))
