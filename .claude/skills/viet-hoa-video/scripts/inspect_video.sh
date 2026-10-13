#!/usr/bin/env bash
# Khảo sát video nguồn: thông số, mốc chuyển cảnh, ảnh tổng hợp khung hình, ảnh viền trên/dưới (tìm logo).
# Dùng: inspect_video.sh <video.mp4> <thư_mục_ra>
set -euo pipefail
V="$1"; O="$2"; mkdir -p "$O"
ffprobe -hide_banner "$V" 2>&1 | grep -E "Duration|Stream"
echo "--- Mốc chuyển cảnh (giây):"
ffmpeg -hide_banner -i "$V" -vf "select='gt(scene,0.2)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | sed 's/pts_time://'
# LƯU Ý: không dùng split+tile trong cùng một lệnh ffmpeg (bị crash); chạy riêng từng lệnh.
ffmpeg -loglevel error -y -i "$V" -vf "fps=1/2,scale=270:-1,tile=6x3" -frames:v 1 "$O/sheet.jpg"
ffmpeg -loglevel error -y -i "$V" -vf "fps=1/1.5,crop=iw:110:0:0,scale=360:-1,tile=6x3" -frames:v 1 "$O/edge_top.jpg"
ffmpeg -loglevel error -y -i "$V" -vf "fps=1/1.5,crop=iw:150:0:ih-150,scale=360:-1,tile=6x3" -frames:v 1 "$O/edge_bottom.jpg"
ffmpeg -loglevel error -y -i "$V" -vn -ac 1 -b:a 64k "$O/audio.mp3"
echo "Ảnh: $O/sheet.jpg  $O/edge_top.jpg  $O/edge_bottom.jpg ; âm thanh: $O/audio.mp3"
