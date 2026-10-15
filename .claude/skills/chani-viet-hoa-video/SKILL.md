---
name: chani-viet-hoa-video
description: Việt hoá video đồ chơi Trung Quốc (Taobao/1688/Xiaohongshu) thành video bán hàng 30–45 giây cho Chani's House: giọng Thùy Dương miền Bắc, phụ đề Việt (Nunito), logo Chani's House, màn kết CTA, 1080x1920, file SRT, thumbnail, tiêu đề SEO và 5 caption Shopee/Facebook/Instagram. Dùng khi chị gửi lệnh kiểu "việt hoá video này cho Chani's House", dán link Taobao/1688 hoặc gửi file video đồ chơi Trung Quốc.
---

# Việt hoá video cho Chani's House

Skill này **bọc ngoài** skill `viet-hoa-video` (8 bước: khảo sát, lấy lời, biên tập, giọng, dựng, kiểm tra). Đọc `../viet-hoa-video/SKILL.md` cho phần kỹ thuật dựng; file này chỉ thêm phần riêng của Chani's House và những bài học từ video NuKied CZ028.

Chị thường dùng iPad: mọi lệnh chạy trên máy ảo, gửi kết quả bằng `SendUserFile`, nhắc chị lưu về Files.

## Đầu vào cần có (hỏi đủ trong một lượt)
1. **File video gốc** (bắt buộc). Máy ảo **không vào được Taobao** (link `e.tb.cn` bị ngắt kết nối, cần đăng nhập, chặn bot). Đừng hứa phân tích được link.
2. **Ảnh chụp trang sản phẩm** (tên, thông số, độ tuổi, chất liệu, pin, số chi tiết, cảnh báo) hoặc chữ dán vào chat. Nếu thiếu, ghi rõ "chưa xác minh", không tự điền.
3. **Xác nhận được phép dùng video** (đại lý/nhà bán hay đã xin phép). Hỏi một câu, nếu chị đã xác nhận thì không hỏi lại.
4. Logo: đã có sẵn `assets/logo_chani.png` (logo gốc, nền trong). Chỉ dùng bản này, không vẽ lại, không đổi màu.

## Quy trình
1. **Thư mục dự án**: `studio-video/<mã-sản-phẩm>/`, đặt video là `source.mp4`. Chạy `../viet-hoa-video/scripts/inspect_video.sh source.mp4 insp/`; xem `sheet.jpg`, `edge_top.jpg`, `edge_bottom.jpg`.
2. **Mốc chuyển cảnh**: dùng `scene>0.05` in điểm số; cảnh thật có điểm > ~0.3. Ngưỡng 0.2 mặc định **bỏ sót** cảnh cắt cùng người/cùng bối cảnh (CZ028 sót 2 cảnh ở giây 2,4 và 3,9). Mỗi cảnh một câu thoại.
3. **Chép lời gốc** bằng ElevenLabs Scribe (xem skill gốc, bước 2). Lời thoại Trung và phụ đề hardsub có thể khác tên riêng (Scribe nghe sai "艺晨" thành "一橙"): bỏ tên người, đừng đưa vào lời Việt.
4. **Viết lời Việt**, mỗi cảnh một câu, ~5,5 âm tiết/giây. Quy tắc nội dung riêng của Chani's House:
   - Mở đầu (0–3 giây) bằng câu hỏi hoặc tình huống của phụ huynh.
   - Chỉ nói điều nhìn thấy trong video hoặc đã xác minh. **Bỏ** lời khẳng định an toàn ("không đau tay"), lợi ích phát triển (tập trung, phối hợp tay mắt), chứng nhận, giá, khuyến mãi, bảo hành. Thay bằng mô tả hành động ("bé say sưa lắp ráp").
   - Không giật gân, không tạo áp lực mua hàng.
   - Câu "Bé nhà mình ngồi chơi cả tiếng" chỉ dùng khi video gốc có lời kể này, và ghi vào danh sách "chưa xác minh".
5. **Giọng**: Thùy Dương, `voice_id` `MfXXiGR0HCVHHuMqcUJM`, model `eleven_v4`, `generations_count: 1`, **mỗi câu một lần gọi**, cùng `flow_id`, gọi song song. ~25–55 credit/câu. Tạo thêm **một câu CTA cuối** ("Khám phá thêm tại Chani's House nha!") thành `voices/s<N+1>.mp3`. Tải về `voices/s1..sN.mp3`, rồi `../viet-hoa-video/scripts/prep_voice.sh voices/` (kết quả `t*.wav`). Không tạo lại câu để "thử lại": mỗi lần tính tiền.
   - Kết quả `creative_get_flow_run_status` của nhiều câu rất dài: nó tự lưu ra file, đọc bằng `jq` (`.generations[] | [.content_url,.prompt]`), đừng in ra.
6. **`project.json`**: sao `examples/cz028-project.json` rồi sửa `shots`, `lines`, `split`, `delogo`/`blur_patches`, `subtitle.band`/`pos`, và mục `chani` (xem dưới). Tạo nhạc nền `../viet-hoa-video/scripts/make_bgm.py <giây+8> bgm.wav`. Chạy `python3 -I ../viet-hoa-video/scripts/build.py project.json` để kiểm tra bản nền.
   - Logo nền tảng (Xiaohongshu + tên shop gốc) thường nằm **dưới đáy** ở vài giây đầu rồi nhảy lên **hai góc trên** ở ~4,9s: lấy mẫu mỗi 0,1s quanh điểm này. Logo đáy: dùng `blur_patches` (delogo rồi làm mờ) thay `delogo` đơn thuần để khỏi sọc.
   - Phụ đề hardsub gốc thường nằm quanh y≈950–1045 (khung 720×1280): `subtitle.band` `{x:10,y:950,w:700,h:94}`, `pos` `[360,997]`. Đo lại cho từng video.
7. **Ghép bản Chani's House**:
   ```
   python3 -I .claude/skills/chani-viet-hoa-video/scripts/assemble.py studio-video/<mã>
   ```
   Script: dựng bản không phụ đề → nâng 1080×1920 → vẽ phụ đề ở độ phân giải 1080 (sắc nét) → huy hiệu logo góc trên phải → nối màn kết 4 giây (logo lớn + CTA + giọng CTA + nhạc nền) → xuất `out/chanis_house_<slug>_vi.mp4`, `.srt`, `thumbnail_chanis_house_<slug>.jpg`. Tự cài font Nunito vào `~/.fonts`.
   Mục `chani` trong `project.json`: `slug`, `thumb_title` (2 dòng, IN HOA), `thumb_sub`, `hero_cue` (đầu câu thoại có khung hình đẹp nhất để làm thumbnail), `cta_text`, `cta_voice`.
8. **Kiểm tra bắt buộc** (không bỏ):
   - Xem các khung hình: đầu, giữa, cuối, sát điểm logo đổi chỗ, màn kết, thumbnail. Phụ đề không bị cắt mép, không còn chữ Trung/logo gốc, thumbnail không lộ dải mờ ở mép.
   - **Nhận dạng ngược**: `work/voice.wav` → mp3 → Scribe → so từng câu với phụ đề; `language_code` phải là `vie`. (~170 credit.)
   - Hệ số kéo giãn từng cảnh 1,0–1,35.
   - `scan_leftovers.py` chỉ hữu ích khi video có tấm chữ trang trí màu vàng/xanh; với đồ chơi màu cam/đỏ nhớ thêm `--no-orange`, vì màu đồ chơi bị báo nhầm là chữ.
9. **Soạn `noi_dung_dang_bai.md`** theo mẫu `examples/cz028-noi-dung-dang-bai.md`: bảng thông tin **đã xác minh** (có nguồn) và **chưa xác minh**; tiêu đề Shopee (≤120 ký tự) + tiêu đề video; từ khoá chính/phụ/ý định tìm kiếm; **5 caption** (điểm nổi bật, cách chơi, giá trị vui chơi chỉ nêu điều thấy được, quà tặng, chốt sale tự nhiên), mỗi bản có tiêu đề, nội dung, CTA, hashtag; mẹo theo nền tảng; bảng kiểm tra chất lượng.
10. **Bàn giao**: `SendUserFile` video (display render) rồi thumbnail, SRT, `.md` (display attach). Commit mã, giọng, `.md`; **không** commit video gốc/thành phẩm (đã nằm trong `.gitignore`). Nếu `git push` bị từ chối: `git pull --no-rebase` rồi push lại. HEAD ở chế độ detached: checkout lại nhánh trước khi commit.

## Quy tắc thương hiệu
- Logo xuất hiện nhỏ ở góc trên phải (huy hiệu nền trắng mờ để dễ đọc), không che sản phẩm; màn kết dùng logo lớn.
- Font Nunito (đã gói trong `assets/fonts/`, ghép từ bộ subset latin + latin-ext + vietnamese của `@fontsource/nunito`). GitHub/Google Fonts bị chặn trên máy ảo; nếu cần font mới: `npm pack @fontsource/<tên>` rồi ghép bằng `fontTools.merge`.
- Màu: xanh lá logo `#6B9133`, nền kem `#FFF7EA`, cam điểm nhấn `#E47E18`.
- Câu CTA: "Khám phá thêm tại Chani's House!" (hoặc "…nha!").

## Giới hạn phải nói thẳng với chị
- Không mở được link Taobao/1688; thông tin sản phẩm lấy từ ảnh chụp trang/dán chữ, còn thiếu thì ghi "chưa xác minh".
- Không nghe được giọng bằng tai: nhắc chị nghe lại, nhất là cách đọc "Chani's House".
- Không đối chiếu được chính sách hiện hành của Shopee/Facebook/Instagram và bản quyền video gốc: chị tự kiểm tra.
- Không giả vờ đã xử lý xong nếu chưa dựng/xuất được: đưa kịch bản, timeline, lời thoại, phụ đề thay thế.

## Chi phí tham khảo (credit ElevenLabs, video 16 cảnh)
Scribe lời gốc ~158; 17 câu giọng ~560; nhận dạng ngược ~168. Tổng ~900.
