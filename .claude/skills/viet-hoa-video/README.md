# viet-hoa-video

Skill Claude Code: Việt hoá video ngắn dọc (Trung → Việt). Đọc `SKILL.md` để biết quy trình 8 bước.

- `scripts/inspect_video.sh`: khảo sát video nguồn (mốc chuyển cảnh, khung hình, viền tìm logo, tách âm thanh)
- `scripts/prep_voice.sh`: cắt lặng đầu/cuối các câu giọng đọc
- `scripts/build.py`: dựng video từ `project.json`
- `scripts/make_bgm.py`: tạo nhạc nền hộp nhạc không bản quyền
- `examples/nukied-project.json`: cấu hình mẫu (video đồ chơi cắt lát rau củ)
