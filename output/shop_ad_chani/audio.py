#!/usr/bin/env python3
"""Tạo nhạc nền (120 BPM, vui nhộn) + SFX bằng tổng hợp số, trộn với giọng đọc (ducking) -> mix.wav.
Mọi âm thanh tự tổng hợp nên không vướng bản quyền."""
import subprocess, wave, numpy as np
from timeline import LEAD, TOTAL, SFX

SR = 44100
rng = np.random.default_rng(7)


def load_voice(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def env(n, a=0.004, d=0.3, curve=3.0):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1.0) * np.exp(-t / d * curve / 3)


def lowpass(x, k):
    c = np.cumsum(np.insert(x, 0, 0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])


def tone(f, dur, shape="sine", d=0.25, a=0.004):
    n = int(dur * SR); t = np.arange(n) / SR
    if shape == "sine":
        w = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 18) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 30)
    elif shape == "saw":
        w = 2 * ((f * t) % 1) - 1; w = lowpass(w, 24)
    else:
        w = np.sign(np.sin(2 * np.pi * f * t)); w = lowpass(w, 30)
    return w * env(n, a, d, 3.0)


def place(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i] * g


# ---------- SFX ----------
def sfx_whoosh(dur=0.38):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    # quét tần số: lọc thông thấp thay đổi theo thời gian (trộn nhiều mức lowpass)
    a, b, c = lowpass(noise, 6), lowpass(noise, 24), lowpass(noise, 90)
    p = t / dur
    w = a * np.clip(1 - np.abs(p - 0.7) * 3, 0, 1) + b * np.clip(1 - np.abs(p - 0.45) * 3, 0, 1) * 1.6 + c * np.clip(1 - np.abs(p - 0.2) * 3, 0, 1) * 3
    return w * np.sin(np.pi * p) ** 1.5 * 0.9


def sfx_pop(f=520):
    n = int(0.16 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (f + 900 * np.exp(-t * 45)) * t) * np.exp(-t * 28) * 0.9


def sfx_boing():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 260 + 140 * np.sin(2 * np.pi * 7 * t) * np.exp(-t * 6) + 120 * np.exp(-t * 12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.8


def sfx_sparkle():
    out = np.zeros(int(0.7 * SR))
    for k, f in enumerate([1568, 2093, 2637, 3136, 4186]):
        place(out, tone(f, 0.3, "sine", 0.12) * 0.35, k * 0.045)
    return out


def sfx_click():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) + rng.standard_normal(n) * np.exp(-t * 120) * 0.4) * 0.9


def sfx_riser(dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 300 + 1700 * (t / dur) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + lowpass(rng.standard_normal(n), 8) * 0.5
    return s * (t / dur) ** 1.5


def sfx_impact():
    n = int(0.6 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (60 + 120 * np.exp(-t * 14)) * t) * np.exp(-t * 7) + lowpass(rng.standard_normal(n), 14) * np.exp(-t * 12) * 0.6)


def sfx_chime(f=1046.5, g=1.0):
    out = np.zeros(int(1.6 * SR))
    for mult, a in [(1, 1.0), (2.01, 0.45), (3.02, 0.25), (4.2, 0.12)]:
        place(out, tone(f * mult, 1.5, "sine", 0.7) * a * 0.45, 0)
    return out * g


def sfx_stinger():
    out = np.zeros(int(2.4 * SR))
    for f in (523.25, 659.25, 783.99, 1046.5):
        place(out, tone(f, 2.2, "sine", 0.9) * 0.3, 0)
    place(out, sfx_sparkle(), 0.05, 0.8)
    return out


SFX_MAKERS = {"whoosh": sfx_whoosh, "pop": sfx_pop, "boing": sfx_boing, "sparkle": sfx_sparkle, "click": sfx_click,
              "riser": sfx_riser, "impact": sfx_impact, "chime": sfx_chime, "stinger": sfx_stinger}

# ---------- Nhạc ----------
BPM = 120; BEAT = 60 / BPM
CHORDS = [(261.63, [261.63, 329.63, 392.0]), (196.0, [196.0, 246.94, 392.0]), (220.0, [220.0, 261.63, 329.63]), (174.61, [174.61, 220.0, 261.63])]
PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
PATTERN = [0, 2, 4, 2, 5, 4, 2, 1, 0, 2, 4, 5, 4, 2, 1, 2]  # 16 nốt móc đơn / 2 ô nhịp


def music(total):
    n = int(total * SR); m = np.zeros(n)
    bars = int(total / (BEAT * 4)) + 1
    for bar in range(bars):
        t0 = bar * BEAT * 4; root, chord = CHORDS[bar % 4]
        for step in range(16):
            ts = t0 + step * BEAT / 4
            if step % 4 == 0:  # kick mỗi nhịp
                kn = int(0.22 * SR); kt = np.arange(kn) / SR
                place(m, np.sin(2 * np.pi * (50 + 110 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.9, ts)
            if step in (4, 12):  # clap
                cn = int(0.14 * SR); ct = np.arange(cn) / SR
                place(m, lowpass(rng.standard_normal(cn), 3) * np.exp(-ct * 28) * 0.45, ts)
            if step % 2 == 0:  # hat
                hn = int(0.05 * SR); ht = np.arange(hn) / SR
                hv = 0.22 if step % 4 == 2 else 0.12
                place(m, (rng.standard_normal(hn) - lowpass(rng.standard_normal(hn), 4)) * np.exp(-ht * 70) * hv, ts)
            if step % 2 == 0:  # bass
                f = root / 2 * (1.5 if step in (6, 14) else 1)
                place(m, tone(f, 0.28, "saw", 0.12) * 0.34, ts)
            if step % 2 == 1 or step in (0, 8):  # marimba arpeggio
                nf = PENTA[PATTERN[step]] * (1.0 if bar % 4 in (0, 2) else (0.75 if bar % 4 == 3 else 0.667))
                place(m, tone(nf, 0.35, "sine", 0.14) * 0.22, ts)
        for f in chord:  # pad nhẹ
            place(m, tone(f, BEAT * 4, "sine", 1.6, 0.25) * 0.05, t0)
    return m


def main():
    voice = load_voice("voice.mp3")
    n = int(TOTAL * SR)
    vo = np.zeros(n); place(vo, voice, LEAD)
    # đường bao giọng đọc -> ducking nhạc
    win = int(0.06 * SR); e = np.sqrt(lowpass(vo ** 2, win)); e = np.clip(e / 0.12, 0, 1)
    e = lowpass(e, int(0.18 * SR))
    mus = music(TOTAL) * (0.62 - 0.42 * e)
    fade = np.clip((TOTAL - np.arange(n) / SR) / 1.2, 0, 1)
    mus *= np.minimum(1.0, np.arange(n) / SR / 0.2 + 0.4) * fade
    fx = np.zeros(n)
    for name, at, g in SFX:
        place(fx, SFX_MAKERS[name](), at, g)
    mix = vo * 1.0 + mus * 1.0 + fx * 0.55
    mix = np.tanh(mix * 0.9) / np.tanh(0.9) * 0.89
    st = np.stack([mix, mix], 1)
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open("mix.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("mix.wav", round(TOTAL, 1), "s, peak", float(np.abs(mix).max()))


if __name__ == "__main__":
    main()
