"""Synthesize the score and UI sound for the Hinge film, on the cues.js grid.

Everything is generated from code (seeded noise, sine voices) so the audio is
reproducible and license-free. Every hit is placed from a named cue in cues.js,
offset by the sound's own measured peak so the transient lands on the frame
(product-film skill, reference/music.md):

  bars 1–3   prompt   quarter-note arp, key clicks, heart pop, send, whoosh
  bars 4–6   beats    kick on every beat, offbeat hats, eighth-note arp
  bar  7     found    drums out, pad only under the punchline
  bars 8–10  delete   haptic buzz, taps, the chime, the pop, iris riser
  bars 11–12 endcard  landing, a bell on each word, ring out

Usage: python3 scripts/make_score.py  (needs numpy, node and ffmpeg on PATH)
"""

import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CUES = json.loads(
    subprocess.run(
        ["node", "-e", "await import('./cues.js'); console.log(JSON.stringify(globalThis.CUES))", "--input-type=module"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout
)
P, B, D, E = CUES["prompt"], CUES["beats"], CUES["delete"], CUES["endcard"]
SR = 44100
LENGTH = CUES["duration"]
BPM = CUES["bpm"]
BEAT = CUES["beat"]
BAR = BEAT * 4


def bar(n):
    """Seconds at the downbeat of bar n (1-based)."""
    return (n - 1) * BAR

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


def hit(sig, cue, gain=1.0, pan=0.0):
    """Place a sound so its loudest sample lands exactly on the cue."""
    peak = int(np.argmax(np.abs(sig))) / SR
    place(sig, max(0.0, cue - peak), gain, pan)


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
    body = np.sin(phase) * np.exp(-t / 0.12)
    # beater: a 4ms band-limited click on the attack, so the beat has a transient
    click_n = int(0.004 * SR)
    beater = np.zeros(n)
    beater[:click_n] = np.random.default_rng(7).standard_normal(click_n) * np.linspace(1, 0, click_n)
    beater = np.convolve(beater, np.ones(4) / 4, mode="same")
    return (body + 0.9 * beater) * gain


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


# ---- harmony: one chord per bar -------------------------------------------
F, A, C, D_, E_, G, Bb = 53, 57, 60, 62, 64, 55, 58  # around octave 3
FMAJ9 = [F, A, C, E_, G + 12]
PROGRESSION = [
    FMAJ9,  # 1  prompt
    [A - 12, C, E_, G + 12],  # 2  Am7
    [D_, F + 12, A, C, E_],  # 3  Dm9
    [Bb - 12, D_, F + 12, A],  # 4  Bbmaj7   drums in: Like. Match.
    FMAJ9,  # 5  First date. Second date.
    [A - 12, C, E_, G + 12],  # 6  Am7      Meet the friends. Us.
    [D_, F + 12, A, C],  # 7  Dm7      drums out: Found your person?
    [Bb - 12, D_, F + 12, A],  # 8  Bbmaj7   the phone
    [G, Bb, D_, F + 12],  # 9  Gm7      Delete Hinge?
    [C, F + 12, G + 12, Bb],  # 10 C7sus4   delete, the iris
    [F - 12, A, C, E_, G + 12],  # 11 Fmaj9 resolve: the tagline
    [F - 12, A, C, E_, G + 12],  # 12 ring out
]
CHORDS = [(bar(i + 1), BAR, notes) for i, notes in enumerate(PROGRESSION)]

for i, (start, dur, notes) in enumerate(CHORDS):
    n = i + 1
    place(pad(notes, dur), start, gain=0.22)
    if 4 <= n <= 6 or n >= 11:
        place(pluck(min(notes) - 12, dur + 0.5, tau=0.5), start, gain=0.35)


def chord_at(t):
    return PROGRESSION[min(int(t // BAR), len(PROGRESSION) - 1)]


# Arpeggio: quarters in the prompt, eighths under the punchlines, halves while deleting.
for a, b, step in [(bar(1), bar(4), BEAT), (bar(4), bar(7), BEAT / 2), (bar(7), bar(11), BEAT * 2)]:
    t, k = a, 0
    while t < b - 1e-6:
        notes = sorted(chord_at(t))
        place(pluck(notes[k % len(notes)] + 12), t, gain=0.1 if step < BEAT else 0.12, pan=0.35 * np.sin(k * 1.3))
        t += step
        k += 1

# ---- rhythm: the punchline bars --------------------------------------------
# Also written alone to STEMS_DIR (if set) so scripts/beats.py can measure the grid.
drums = np.zeros(N)
for i in range(12):
    t = bar(4) + i * BEAT
    k = kick(1.0 if i % 2 == 0 else 0.7)
    place(k, t, gain=0.55)
    drums[int(t * SR) : int(t * SR) + len(k)] += 0.55 * k
    if t >= bar(5):
        h = hat()
        place(h, t + BEAT / 2, gain=0.12, pan=0.25)
        j = int((t + BEAT / 2) * SR)
        drums[j : j + len(h)] += 0.12 * h
for i, note in enumerate([89, 93, 96]):  # "Us."
    place(bell(note, 1.5), B["us"] + i * 0.06, gain=0.07, pan=0.2 * (i - 1))
hit(bell(96, 1.0), B["usHeart"], gain=0.05)

# ---- UI sound, each on its cue ---------------------------------------------
answer, comment = "you ask a second question.", "Ask me one."
span = P["answerDone"] - P["typeAnswer"]
for k in range(len(answer)):
    hit(click(0.8 + 0.2 * ((k * 7) % 3) / 2), P["typeAnswer"] + k * span / len(answer), gain=0.1, pan=0.1)
for k in range(len(comment)):
    hit(click(0.9), P["typeComment"] + k * 0.4 / len(comment), gain=0.1, pan=0.1)
hit(blip(520, 1180, 0.16), P["heartTap"], gain=0.22)
hit(bell(84, 1.2), P["heartTap"], gain=0.05)
hit(click(1.5), P["sendPress"], gain=0.14)
place(whoosh(0.6, rise=False), P["flyAway"], gain=0.1)
place(whoosh(0.5, rise=False), P["handoff"], gain=0.05)  # the heart crosses the cut

place(whoosh(0.6, rise=False), D["phoneIn"], gain=0.05)
hit(blip(820, 1040, 0.08), D["press"], gain=0.07)  # "Press & hold"
buzz_t = np.arange(int(0.14 * SR)) / SR
place(np.sin(2 * np.pi * 70 * buzz_t) * np.sin(np.pi * buzz_t / 0.14), D["editMode"], gain=0.35)  # haptic
hit(click(1.4), D["badgeTap"], gain=0.14)
hit(blip(700, 900, 0.1), D["cardIn"], gain=0.1)
hit(click(1.1), D["pick"], gain=0.12)
hit(blip(820, 1040, 0.08), D["toDelete"], gain=0.07)  # "Tap Delete"
hit(click(1.4), D["deleteTap"], gain=0.14)
hit(bell(81, 0.8), D["deleteTap"] + 0.05, gain=0.05)  # "Hinge deleted"
hit(bell(88, 0.8), D["deleteTap"] + 0.13, gain=0.04)
hit(blip(900, 260, 0.2), D["vanish"], gain=0.26)  # the icon goes
place(whoosh(0.5, rise=False), D["reflow"], gain=0.04)
riser = whoosh(bar(11) - D["iris"], rise=True)
place(riser, D["iris"], gain=0.16)  # peaks at the downbeat of bar 11

hit(kick(1.2), E["designed"], gain=0.6)  # landing
for i, name in enumerate(["designed", "to", "be", "deleted"]):
    hit(bell([77, 81, 84, 88][i]), E[name], gain=0.09, pan=-0.3 + 0.2 * i)
hit(bell(91), E["mark"], gain=0.08)
for name in ("tick1", "tick2"):  # the counter's off-beat flips
    hit(click(0.7), B[name], gain=0.08, pan=-0.2)

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
tail = int(1.2 * SR)
fade[-tail:] = np.linspace(1, 0, tail) ** 1.5
mix = np.stack([left, right], axis=1) * fade[:, None]
mix = np.tanh(mix * 1.2)
mix *= 0.89 / np.max(np.abs(mix))

import os

if os.environ.get("STEMS_DIR"):
    stem = Path(os.environ["STEMS_DIR"]) / "drums.wav"
    with wave.open(str(stem), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((drums / np.max(np.abs(drums)) * 0.9 * 32767).astype("<i2").tobytes())

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
