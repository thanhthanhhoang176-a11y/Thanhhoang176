---
name: viet-hoa-video
description: Việt hoá video ngắn dọc (TikTok/Reels/Shorts) từ tiếng Trung (hoặc ngôn ngữ khác) sang tiếng Việt, gần gũi với bé và phụ huynh Việt Nam: lấy lời thoại, biên tập lại tự nhiên, lồng tiếng ElevenLabs, che chữ/logo cũ, phụ đề Việt, nhạc nền, soạn bài đăng. Dùng khi người dùng gửi một video nước ngoài và muốn "việt hoá", "lồng tiếng Việt", "dịch và đăng lại", "làm video quảng cáo tiếng Việt từ video Trung Quốc".
---

# Việt hoá video (quy trình 8 bước)

Quy trình này đã chạy thành công với video quảng cáo đồ chơi cắt lát rau củ (28 giây, Xiaohongshu → 30 giây tiếng Việt).
Kết quả: mỗi câu lồng tiếng khớp đúng một cảnh quay, phụ đề gọn, không còn chữ Trung/logo nền tảng, giọng đọc khớp từng chữ với phụ đề.

Người dùng thường dùng iPad nên **mọi lệnh chạy trên máy ảo đám mây**. Gửi video cho người dùng bằng `SendUserFile` (display: render), nhắc họ lưu về Files vì máy ảo sẽ bị xoá.

## Điều kiện cần
- `ffmpeg` (có libass), `python3` + `numpy` + `Pillow`.
- Connector **ElevenLabs** (công cụ `mcp__ElevenLabs__creative_*`; nạp bằng ToolSearch `select:` trước khi gọi). Bản này **không tạo nhạc/ảnh/video**.
- Thư mục dự án riêng, ví dụ `studio-video/<tên-video>/`. Đặt file nguồn là `source.mp4`.

## Bước 0. Quyền sử dụng (hỏi trước, 1 câu)
Video của thương hiệu/người khác: hỏi người dùng đã được phép dùng chưa (đại lý, affiliate, tự quay, hay đã xin phép). Nếu đã được phép thì làm tiếp, không hỏi lại. Nếu chưa rõ thì nói rõ rủi ro bị gỡ bài/báo bản quyền, rồi làm theo quyết định của họ. **Không đưa video gốc hay video thành phẩm của bên thứ ba lên repo công khai**: thêm vào `.gitignore` (`cn/source*`, `cn/*.mp4`), repo nên để Private.

## Bước 1. Khảo sát video nguồn
```
scripts/inspect_video.sh source.mp4 insp/
```
Xem `insp/sheet.jpg`, `edge_top.jpg`, `edge_bottom.jpg` bằng Read. Ghi lại:
- **Mốc chuyển cảnh** (giây) → chính là danh sách `shots`. Mỗi cảnh = một câu thoại.
- **Chữ in sẵn (hardsub)**: vùng y nào, có liên tục không → `subtitle.band`.
- **Logo/watermark** và **thời điểm chúng đổi vị trí**. Logo nền tảng hay nằm dưới đáy rồi nhảy lên đỉnh giữa video. Phải lấy mẫu mỗi 0,2–0,5 giây quanh chỗ chuyển (đã sót logo một lần vì tắt che quá sớm).
- Kích thước khung (thường 720x1280).

- **Tấm chữ trang trí lớn** (sticker/emoji tiếng Trung ở phía trên hình, kèm tia sáng vàng). Lấy mẫu dày (mỗi 0,2s) để biết lúc nó xuất hiện/biến mất và vùng chính xác (cả tia sáng phía trên chữ). Che bằng `stickers` thay chữ Việt cùng nghĩa; tia sáng còn sót lại dưới `delogo` thường trông như vệt sọc vàng.

## Bước 2. Lấy lời thoại gốc (ElevenLabs Scribe)
Thứ tự gọi (một flow chung):
1. `creative_create_flow`
2. `creative_create_asset_upload` (name, mime `audio/mpeg`, file_size đúng byte của `insp/audio.mp3`)
3. `curl -X PUT -H "Content-Type: audio/mpeg" --data-binary @insp/audio.mp3 "<upload_url>"` (mong đợi HTTP 200)
4. `creative_finalize_asset_upload` (asset_id + flow_id) → `node_id`
5. `creative_transcribe_audio` (`model_id: eleven_scribe_v1`, `connect_from: [node_id]`, flow_id)
6. Đợi vài giây (dùng `Monitor`/until-loop, không `sleep` đứng riêng), rồi `creative_get_flow_run_status` đến `all_completed`.

Kết quả có mốc thời gian từng chữ: dùng để biết lời gốc nói gì ở cảnh nào. Chi phí ~150 credit/phút.

## Bước 3. Biên tập lời Việt (đây là bước quyết định chất lượng)
Viết **lại**, không dịch sát chữ. Mỗi cảnh một câu. Quy tắc rút ra từ thực tế:
- **Tên thao tác phải đúng với hình.** Xem kỹ cảnh trước khi viết ("ấn xuống rồi trượt qua trượt lại", "đẩy tới, kéo lui"). Từ "gọt" sai khi sản phẩm tạo lát: dùng **"cắt lát"/"thái lát"**.
- Mở đầu hấp dẫn, tự nhiên ("…bé nào mà không mê!"). Tránh câu hỏi tu từ dịch máy.
- Cụm Hán-Việt máy móc phải Việt hoá ("手眼脑协调" → "nhanh tay, nhanh mắt, nhanh trí"; "精细动作" → "khéo tay").
- Xưng hô gần gũi: "bé", "bé nhà mình", câu ngắn, từ đệm vui ("luôn", "lắm", "nữa đó").
- **Độ dài câu ≈ thời lượng cảnh.** Ước tính ~5 âm tiết/giây ở tốc độ gốc, giọng sẽ được tăng tốc 1,25x. Câu dài hơn ~1,4 lần cảnh thì rút gọn (script cảnh báo `!` khi kéo giãn >1,45x).
- **Tránh từ dễ nghe nhầm** với giọng miền Bắc: "Trò" bị đọc/nghe thành "Cho" (tr/ch). Đổi từ khác.
- Câu rất dài (>~60 ký tự): đặt dấu phẩy chia 2 vế để dùng `split` (chữ phụ đề to, dễ đọc hơn).
- Ghi bảng song ngữ vào `loi-thoai.md` (giây | tiếng gốc | tiếng Việt).

## Bước 4. Tạo giọng (ElevenLabs)
- Chọn giọng bằng `creative_list_voices` (languages `["vi"]`). Đã dùng tốt: **Chi** `5yEPTrA0uAhZsBEhHjfi` (trẻ, tươi, hợp quảng cáo ngắn); **Cô Giang** `BNdqbMgt3iZONYMkKMzH` (cô giáo, dịu dàng, hợp video dạy bé). Nói với người dùng giọng đã chọn.
- Mô hình `eleven_v4`. **Tạo từng câu riêng** (`creative_generate_speech`, `generations_count: 1`, cùng `flow_id`), gọi song song cả loạt trong một lượt. Cách này cho thời lượng từng câu chính xác, dễ sửa 1 câu mà không tạo lại cả bài. ~40–80 credit/câu.
- Poll `creative_get_flow_run_status` với tất cả session_ids; tải `content_url` bằng curl thành `voices/s1.mp3 … sN.mp3`.
- Cắt lặng đầu/cuối: `scripts/prep_voice.sh voices/` → `t1.wav … tN.wav`.
- Không bao giờ gọi lại một lệnh tạo giọng để "thử lại": mỗi lần tính tiền.

## Bước 5. Cấu hình và dựng
Sao `examples/nukied-project.json` thành `project.json` và sửa: `shots`, `lines`, `split`, `blur_patches` (che logo: xoá bằng delogo rồi làm mờ; vùng + cửa sổ thời gian **theo giây của video gốc**), `stickers` (thay tấm chữ trang trí tiếng Trung bằng chữ Việt: vùng mờ `blur`, khung chữ `pill`, `text`, cửa sổ `from/to`), `subtitle.band` (vùng che hardsub; cao ~94px cho 2 dòng), `voice_dir`, `bgm`. (`delogo` đơn thuần vẫn dùng được nhưng dễ để lại vệt sọc trên nền nhiều chi tiết.)
Nhạc nền: `scripts/make_bgm.py <giây> bgm.wav` (tự sáng tác, không bản quyền) hoặc dùng file của người dùng.
```
python3 -I scripts/build.py project.json
```
Script làm: tăng tốc giọng 1,25x → đặt mỗi câu đúng đầu cảnh → kéo giãn từng cảnh gốc cho vừa câu (không bao giờ nhanh hơn gốc) → xoá logo (delogo) → dải mờ tối che hardsub → phụ đề ASS cân dòng, ngắt sau dấu phẩy → trộn nhạc nền nhỏ.

Mẹo kỹ thuật đã vấp:
- `boxblur` trên dải cao 94px: bán kính tối đa 23 (dùng `20:3`).
- Không gộp `split` với `tile` trong một lệnh ffmpeg (crash); chạy riêng.
- Phông `Liberation Sans Bold` gọn hơn DejaVu; phụ đề 2 dòng ≤ 670px, cỡ chữ tự giảm 40→28.
- Ngắt dòng ASS dùng `\N` (đừng viết `chr(92)+'N'.join(...)` vì sai thứ tự phép toán).

## Bước 6. Kiểm tra chất lượng (bắt buộc, không bỏ)
0. **Quét tự động chữ Trung còn sót** (bắt buộc, trước khi gửi người dùng):
   `python3 -I scripts/scan_leftovers.py source.mp4 <video_dựng>.mp4`. Phần "Bản dựng" phải rỗng. Bước này tồn tại vì lấy mẫu mắt thường (0,5s) làm lỡ khung chữ bay vào/ra: đã có lần gửi video còn lộ chữ ✅成就感 ở 17,0s và ✅专注力 ở 33,0s.
   Để đặt cửa sổ `stickers`/`blur_patches` đúng: lấy khung nguồn mỗi **0,1s** quanh mỗi tấm (từ trước lúc nó hiện ~0,5s đến sau lúc mất ~0,5s), ghi giây hiện đầu tiên và giây mất cuối cùng, rồi nới thêm ~0,05s trước và ~0,1s sau. Chữ thường bay vào/phóng to ở 1–2 khung đầu (có thể to hơn vùng chữ bình thường: thêm `blur_patches` phủ cả dải ở khoảnh khắc đó với `"delogo": false`), và khung đầu tiên sau điểm chuyển cảnh có thể vẫn còn chữ cũ.
1. **Khung hình**: trích ~8–10 khung ở các giây khác nhau (đầu, giữa, cuối, và sát điểm logo đổi chỗ), ghép thành ảnh rồi Read. Kiểm tra: còn chữ Trung/logo không, chữ phụ đề có bị cắt mép không, dải có che sản phẩm quá không, có lúc dải trống không.
2. **Nhận dạng ngược giọng đọc**: xuất `work/voice.wav` → mp3 → làm lại quy trình Bước 2 (ngôn ngữ Việt). So từng câu với phụ đề; kiểm tra không lẫn tiếng Trung (`language_code` phải là `vie`). Sửa câu nào bị nghe sai (tạo lại **riêng câu đó**, dựng lại).
3. Hệ số kéo giãn từng cảnh nằm trong khoảng ~1,0–1,35.
4. Gửi video cho người dùng xem và hỏi: giọng, tốc độ, chữ, lời thoại có cần đổi không.

## Bước 7. Soạn bài đăng
Tạo `dang-bai.md`: tiêu đề hook, mô tả (có lợi ích cho bé, đối tượng), hashtag (#mevabe #dochoigiaoduc…), bản Facebook ngắn, giờ đăng gợi ý (11:30–13:00, 19:30–22:00), ghi "Video gốc: <thương hiệu>" nếu được phép, và nhắc ghi rõ quảng cáo/affiliate nếu có. Dùng đúng từ khoá đã chọn trong video ("cắt lát").
Hỏi người dùng có muốn thêm lời kêu gọi cuối (tên shop, giá, link mua) không.

## Bước 8. Lưu và bàn giao
- Commit mã, lời thoại, phụ đề, giọng (không commit video nguồn/thành phẩm của bên thứ ba). Theo cấu hình repo: push lên nhánh hiện tại.
- Gửi bản cuối bằng `SendUserFile`; nhắc lưu về Files; nhắc đổi repo sang Private.

## Bài học thêm từ video thứ hai (gạch từ tính, 19,6s)
- Cả 3 tấm chữ trang trí tiếng Trung + logo đổi chỗ (đáy → đỉnh ở giây ~4,95): dùng `stickers` và `blur_patches` (delogo + làm mờ).
- Cảnh ngắn (≤1,7s) mà câu thoại 8 âm tiết trở lên sẽ bị kéo chậm >1,4x: rút gọn câu trước khi tạo giọng. Lần đầu phải tạo lại 3 câu (~110 credit) vì không ước lượng trước.
- Khi mốc kích thước file nhập vào `creative_create_asset_upload` sai dù chỉ vài byte, URL tải sẽ không dùng được: lấy đúng bằng `stat -c %s`, nhập lại, tạo upload mới.
- Phiên khác có thể đã đẩy commit lên cùng nhánh: nếu `git push` bị từ chối, `git pull --no-rebase` rồi push lại.

## Bài học thêm từ video thứ ba (xe lửa domino, 42s, 12 cảnh)
- Từ dễ nghe nhầm ở giọng đọc: "như **ng**ăn kéo" nghe thành "nhưng **ăn** kéo" (âm "ng" bị nuốt). Tránh các từ bắt đầu bằng "ng"/"tr" nằm sau từ kết thúc bằng "ư/u"; luôn nhận dạng ngược để bắt lỗi.
- Câu rất dài: `split` nhận cả danh sách ["đoạn 1,", "đoạn 2,"] để tách nhiều cue; cue 2 dòng vẫn phải đủ lớn (cỡ chữ ≥ 36).
- Hai tấm chữ chồng cùng một vùng (ví dụ "✅直线" và "✅弯线"): tấm thứ hai chỉ cho `blur` đúng vùng khung chữ của nó, nếu không sẽ làm mờ luôn khung chữ của tấm thứ nhất.
- Logo nền tảng chuyển chỗ muộn hơn mốc chuyển cảnh gần nhất (ở đây ~4,95s trong khi cảnh đổi ở 4,2s): lấy mẫu 0,1s quanh điểm chuyển.
- Kết quả `creative_get_flow_run_status` nhiều câu rất dài: nó tự lưu ra file; đọc `content_url` bằng python/jq rồi tải về, đừng in ra.
- Kiểm tra nhanh một câu đã sửa: chỉ tải riêng câu đó (~35 credit) thay vì cả bài (~240 credit).

## Chi phí tham khảo (credit ElevenLabs)
Scribe ~150–165/lần; giọng ~40–80/câu; một video 9 cảnh ~500 + 1–2 lần kiểm tra ngược ~330. Tạo lại câu lỗi ~50–70.

## Bắt đầu nhanh (người dùng chỉ cần nhắn)
> Việt hoá video này theo skill viet-hoa-video: giọng nữ tươi vui, xưng "bé", phụ đề Việt, nhạc nền nhẹ. (kèm video)
