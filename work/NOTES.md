# Ghi chú làm tiếp (Việt hóa video quảng cáo Nukied)

File trong thư mục này:
- `in.mp4`: video gốc tiếng Trung (720x1280, 50fps, 34,54 s).
- `clean.mp4`: video đã xóa phụ đề Trung (chưa có âm thanh đúng, chưa có phụ đề Việt).
- `inst.wav`: âm thanh gốc đã tách bỏ giọng Trung (còn nhạc + hiệu ứng), 44,1 kHz stereo.
- `script.json`: lời thoại [bắt đầu, kết thúc, tiếng Trung, tiếng Việt, từ khóa tô màu].
- `build.py`: tạo giọng (hiện dùng Piper), file `vi.ass`/`vi.srt`, trộn âm thanh (`mix.wav`).

Cách dựng video cuối (sau khi có `mix.wav` 35,54 s):
```
ffmpeg -i clean.mp4 -i clean.mp4 -i mix.wav -filter_complex "[0:v]trim=0:31.8,setpts=PTS-STARTPTS[a];[1:v]trim=19.95:21.9,setpts=PTS-STARTPTS,split[t1][t2];[t2]reverse[t3];[t1][t3]concat=n=2:v=1:a=0,trim=0:3.74,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,ass=vi.ass[v]" -map "[v]" -map 2:a -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -r 50 -c:a aac -b:a 192k -movflags +faststart -t 35.54 final.mp4
```
Phần cuối video (từ giây 31,8) thay trang tài khoản Trung bằng cảnh đồ chơi (19,95–21,9 s chạy tới rồi lùi). Câu kết "Hãy subscribe cho kênh Ghiền Mì Gõ..." bắt đầu giây 32,0.

Giọng hiện tại: ElevenLabs "Anh Thu - Sweet & Engaging" (nữ miền Nam, voice_id `FRYq6nepIbR0lbu7Lus4`, model `eleven_turbo_v2_5`). 13 câu đã tạo sẵn thành `v0.mp3`..`v12.mp3` (đã chép lại bằng Scribe, khớp 100% kịch bản kể cả dấu thanh). `build.py` chỉ đổi mp3 sang wav, rồi trộn + tạo phụ đề; sau đó chạy lệnh ffmpeg ở trên để ra `final.mp4`.
Cách đọc "Nukied": "Nu kít" (chờ người dùng xác nhận). Phụ đề vẫn ghi "Nukied".
Yêu cầu giữ nguyên hiệu ứng âm thanh gốc (nền `inst.wav` x2.2, ducking nhẹ).
