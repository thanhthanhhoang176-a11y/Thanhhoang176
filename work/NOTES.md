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

Việc cần làm: thay giọng Piper bằng giọng nữ ElevenLabs (tiếng Việt, mềm, miền Nam nếu có).
Khóa ElevenLabs nằm ở "network secret" của môi trường (header `xi-api-key`, host `api.elevenlabs.io`): gọi API không cần tự thêm khóa.
Cách đọc "Nukied": "Nu kít" (chờ người dùng xác nhận). Phụ đề vẫn ghi "Nukied".
Yêu cầu giữ nguyên hiệu ứng âm thanh gốc (nền `inst.wav` x2.2, ducking nhẹ).

## Cập nhật: đã lồng tiếng ElevenLabs
- Giọng: "Nhi" (nữ miền Nam, id `Xq6JCnPKC1WM8ONUXMCJ`), model `eleven_multilingual_v2`, đọc "Nu kít" cho Nukied. Từng câu lưu `e0.mp3`…`e12.mp3`.
- `build.py` giờ đọc `e*.mp3` (không còn Piper) rồi tạo `mix.wav`, `vi.ass`, `vi.srt`; `final.mp4` dựng bằng lệnh ffmpeg ở trên (35,54 s).
- Chưa nghe thử bằng tai; cần người dùng xác nhận giọng và cách đọc "Nu kít".
