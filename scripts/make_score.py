"""Synthesize the score and UI sound for the Hinge film.

Everything is generated from code (seeded noise, sine voices) so the audio is
reproducible and license-free. Timings match the compositions:

  0–5s    prompt   soft quarter-note arp, key clicks, heart pop, send whoosh
  5–11s   beats    kick on every word, offbeat hats, eighth-note arp
  11–16.5 delete   drums drop out, haptic buzz, taps, the pop, iris riser
  16.5–20 endcard  resolve chord + bell, ring out

Usage: python3 scripts/make_score.py  (needs numpy and ffmpeg on PATH)
"""

import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
LENGTH = 20.0
BPM = 120
BEAT = 60 / BPM
N = int(SR * LENGTH)
rng = np.random.default_rng(214)

left = np.zeros(N)
right = np.zeros(N)


def hz(note):
    """MIDI note number to frequency."""
    return 440.0 * 2 ** ((note - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0):
    """Mix a mono signal into the stereo bus at time t (seconds)."""
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    left[i : i + len(sig)] += sig * np.sqrt((1 - pan) / 2)
    right[i : i + len(sig)] += sig * np.sqrt((1 + pan) / 2)


def env_ad(n, attack, tau):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / tau)


def pluck(note, dur=1.6, tau=0.55):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(note)
    sig = np.sin(2 * np.pi * f * t) + 0.28 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    return sig * env_ad(n, 0.004, tau)


def bell(note, dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(note)
    sig = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
    return sig * env_ad(n, 0.002, 0.9)


def pad(notes, dur, attack=0.35, release=0.7):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for note in notes:
        f = hz(note)
        for detune in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (detune / 12)
            sig += np.sin(2 * np.pi * ff * t) + 0.18 * np.sin(4 * np.pi * ff * t)
    sig /= 3 * len(notes)
    a = np.clip(t / attack, 0, 1)
    r = np.clip((dur + release - t) / release, 0, 1)
    return sig * a * r


def kick(gain=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t / 0.12) * gain


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def highpass(x, amount=0.97):
    """Cheap one-pole high-pass: x minus a smoothed copy of itself."""
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = amount * acc + (1 - amount) * v
        y[i] = v - acc
    return y


def hat():
    n = noise(0.05)
    return highpass(n) * env_ad(len(n), 0.001, 0.012)


def click(gain=1.0):
    n = noise(0.02)
    return highpass(n, 0.9) * env_ad(len(n), 0.0005, 0.004) * gain


def blip(f0, f1, dur=0.14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.003, dur / 3)


def whoosh(dur, rise=True):
    x = noise(dur)
    # Band-limit by smoothing, then shape with a swell.
    k = 18
    x = np.convolve(x, np.ones(k) / k, mode="same")
    t = np.linspace(0, 1, len(x))
    shape = np.sin(np.pi * t) ** 2 if not rise else t**2.2
    return x * shape


# ---- harmony ---------------------------------------------------------------
F, A, C, D, E, G, Bb = 53, 57, 60, 62, 64, 55, 58  # around octave 3
CHORDS = [
    (0.0, 2.0, [F, A, C, E, G + 12]),  # Fmaj9
    (2.0, 2.0, [A - 12, C, E, G + 12]),  # Am7
    (4.0, 2.0, [D, F + 12, A, C, E]),  # Dm9
    (6.0, 2.0, [Bb - 12, D, F + 12, A]),  # Bbmaj7
    (8.0, 2.0, [F, A, C, E, G + 12]),  # Fmaj9
    (10.0, 1.0, [A - 12, C, E, G + 12]),  # Am7 ("Us.")
    (11.0, 2.0, [D, F + 12, A, C]),  # Dm7   delete scene: tension
    (13.0, 2.0, [Bb - 12, D, F + 12, A]),  # Bbmaj7
    (15.0, 1.5, [C, F + 12, G + 12, Bb]),  # C7sus4 into the iris
    (16.5, 3.5, [F - 12, A, C, E, G + 12]),  # Fmaj9 resolve
]

for start, dur, notes in CHORDS:
    place(pad(notes, dur), start, gain=0.22)
    root = min(notes) - 12
    if 5.0 <= start < 11.0 or start >= 16.5:
        place(pluck(root, dur + 0.5, tau=0.5), start, gain=0.35)


def chord_at(t):
    for start, dur, notes in CHORDS:
        if start <= t < start + dur:
            return notes
    return CHORDS[-1][2]


# Arpeggio: quarters in the prompt, eighths in the beats, halves while deleting.
arp_steps = [(0.0, 5.0, BEAT), (5.0, 11.0, BEAT / 2), (11.0, 16.5, BEAT * 2)]
for a, b, step in arp_steps:
    t, k = a, 0
    while t < b - 1e-6:
        notes = sorted(chord_at(t))
        note = notes[k % len(notes)] + 12
        place(pluck(note), t, gain=0.1 if step < BEAT else 0.12, pan=0.35 * np.sin(k * 1.3))
        t += step
        k += 1

# Resolve arp slows to a stop on the end card.
for i, (dt, note) in enumerate([(0.0, 77), (0.5, 81), (1.0, 84), (1.75, 88), (2.75, 91)]):
    place(bell(note), 16.5 + dt, gain=0.1, pan=(-0.3 + 0.15 * i))

# ---- rhythm (beats scene) ----------------------------------------------------
for i in range(12):
    t = 5.0 + i * BEAT
    place(kick(1.0 if i % 2 == 0 else 0.7), t, gain=0.55)
    if t >= 6.0:
        place(hat(), t + BEAT / 2, gain=0.12, pan=0.25)

# "Us." sparkle
for i, note in enumerate([89, 93, 96]):
    place(bell(note, 1.5), 10.0 + i * 0.06, gain=0.07, pan=0.2 * (i - 1))

# ---- UI sound ----------------------------------------------------------------
answer, comment = "you ask a second question.", "Ask me one."
for k in range(len(answer)):
    place(click(0.8 + 0.2 * ((k * 7) % 3) / 2), 0.9 + k * 1.5 / len(answer), gain=0.1, pan=0.1)
for k in range(len(comment)):
    place(click(0.9), 3.3 + k * 0.5 / len(comment), gain=0.1, pan=0.1)

place(blip(520, 1180, 0.16), 2.7, gain=0.22)  # heart
place(bell(84, 1.2), 2.72, gain=0.05)
place(click(1.5), 3.98, gain=0.14)  # send
place(whoosh(0.7, rise=False), 4.1, gain=0.1)

# Delete scene (global time = 11 + local).
buzz_t = np.arange(int(0.14 * SR)) / SR
place(np.sin(2 * np.pi * 70 * buzz_t) * np.sin(np.pi * buzz_t / 0.14), 12.8, gain=0.35)  # haptic
place(click(1.4), 13.3, gain=0.14)  # tap badge
place(blip(700, 900, 0.1), 13.45, gain=0.1)  # alert
place(click(1.4), 14.28, gain=0.14)  # tap delete
place(blip(900, 260, 0.2), 14.68, gain=0.26)  # the pop
place(whoosh(0.3, rise=False), 14.9, gain=0.05)  # puff
place(whoosh(0.5, rise=False), 15.0, gain=0.04)  # icons reflow
place(blip(820, 1040, 0.08), 12.25, gain=0.07)  # "Press & hold" callout
place(blip(820, 1040, 0.08), 13.8, gain=0.07)  # "Tap Delete" callout
place(bell(81, 0.8), 14.98, gain=0.05)  # toast
place(bell(88, 0.8), 15.06, gain=0.04)
place(whoosh(0.95, rise=True), 15.55, gain=0.16)  # iris riser
place(kick(1.2), 16.5, gain=0.6)  # landing

# ---- reverb (a few feedback combs, processed in delay-sized blocks) ----------


def comb(x, delay_s, g):
    d = int(delay_s * SR)
    y = x.copy()
    for s in range(d, len(y), d):
        e = min(s + d, len(y))
        y[s:e] += g * y[s - d : e - d]
    return y


def reverb(x):
    wet = sum(comb(x, d, g) for d, g in [(0.0297, 0.72), (0.0371, 0.7), (0.0411, 0.68), (0.0437, 0.66)])
    return wet / 4


left += 0.22 * reverb(left)
right += 0.22 * reverb(right)

# ---- master ------------------------------------------------------------------
fade = np.ones(N)
tail = int(0.9 * SR)
fade[-tail:] = np.linspace(1, 0, tail) ** 1.5
mix = np.stack([left, right], axis=1) * fade[:, None]
mix = np.tanh(mix * 1.2)
mix *= 0.89 / np.max(np.abs(mix))

out = Path(__file__).resolve().parent.parent / "assets" / "audio"
out.mkdir(parents=True, exist_ok=True)
wav = out / "score.wav"
with wave.open(str(wav), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())

subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(out / "score.mp3")],
    check=True,
)
wav.unlink()
print(f"wrote {out / 'score.mp3'}")
