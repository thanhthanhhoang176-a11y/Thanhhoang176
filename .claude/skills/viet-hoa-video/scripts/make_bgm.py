#!/usr/bin/env python3
"""Tạo nhạc nền hộp nhạc vui nhẹ (tự sáng tác, không dính bản quyền). Dùng: make_bgm.py <giây> <ra.wav>"""
import sys, wave, numpy as np
dur = float(sys.argv[1]); out = sys.argv[2]
sr = 44100; beat = 60 / 108
notes = {'C': 523.25, 'D': 587.33, 'E': 659.25, 'G': 783.99, 'A': 880.0, 'c': 1046.5}
mel = "E G A G E D C D E G E D C D E G A c A G E G A G E D C - - -".split()
y = np.zeros(int(sr * dur))
def tone(f, st, ln, amp):
    n = int(sr * ln); t = np.arange(n) / sr
    env = np.exp(-t * 5.5) * (1 - np.exp(-t * 400))
    seg = amp * (np.sin(2*np.pi*f*t) + .35*np.sin(4*np.pi*f*t) + .12*np.sin(6*np.pi*f*t)) * env
    i = int(st * sr); seg = seg[:max(0, len(y) - i)]; y[i:i + len(seg)] += seg
t = 0.0; i = 0
while t < dur - 1:
    m = mel[i % len(mel)]
    if m in notes: tone(notes[m], t, 0.9, 0.22)
    t += beat / 2; i += 1
t = 0.0; k = 0
while t < dur - 1:
    f = [130.81, 110.0, 87.31, 98.0][k % 4]; tone(f, t, 1.8, 0.18); tone(f * 1.5, t + beat * 2, 1.2, 0.08); t += beat * 4; k += 1
y /= np.max(np.abs(y)); y *= 0.8; fade = int(sr * 1.5); y[-fade:] *= np.linspace(1, 0, fade)
w = wave.open(out, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
