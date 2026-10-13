#!/usr/bin/env bash
# Cắt khoảng lặng đầu/cuối từng câu giọng đọc: s1.mp3 .. sN.mp3  ->  t1.wav .. tN.wav (mono 44.1kHz)
# Dùng: prep_voice.sh <thư_mục_chứa_s*.mp3>
set -euo pipefail
cd "$1"
for f in s*.mp3; do
  i="${f#s}"; i="${i%.mp3}"
  ffmpeg -loglevel error -y -i "$f" \
    -af "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.05,areverse" \
    -ar 44100 -ac 1 "t$i.wav"
  printf "t%s %.2fs\n" "$i" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "t$i.wav")"
done
