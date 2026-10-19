#!/usr/bin/env python3
"""Synthesize Early Dynastic–inspired soundtrack for the Gilgamesh disk.

Inspired by public descriptions of Sumerian performance practice (gish-gudi lute
and zurna reed with circular-breathing drone — e.g. reconstructions that retell
"Gilgamesh, Enkidu and the Nether World"), not by sampling any copyrighted
recording. Motifs are newly synthesized. Optional CC0 loops in tools/music-samples/
are mixed underneath.

    python3 tools/compose_music.py
"""
from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "music"
SAMPLES = Path(__file__).resolve().parent / "music-samples"
RATE = 44100

# Just-intonation heptatonic sketch around a modal centre (lyre / lute of Ur notes).
SCALE = np.array([1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2.0], dtype=np.float64)


def env(n: int, attack: float = 0.01, release: float = 0.12) -> np.ndarray:
    a = max(1, int(RATE * attack))
    r = max(1, int(RATE * release))
    e = np.ones(n, dtype=np.float64)
    if a < n:
        e[:a] = np.linspace(0.0, 1.0, a, endpoint=False)
    if r < n:
        e[-r:] = np.linspace(1.0, 0.0, r)
    return e


def soft_clip(x: np.ndarray, drive: float = 1.4) -> np.ndarray:
    return np.tanh(x * drive) / math.tanh(drive)


def frequency(root: float, degree: int) -> float:
    return float(root * SCALE[degree % 8] * (2 ** (degree // 8)))


def karplus_strong(freq: float, seconds: float, amp: float = 0.25, brightness: float = 0.55) -> np.ndarray:
    """Plucked-string model — gish-gudi / lyre attack with a woody decay."""
    n = max(1, int(RATE * seconds))
    period = max(2, int(RATE / max(freq, 20.0)))
    rng = np.random.default_rng(int(freq * 10) % 10_000 + 7)
    buf = rng.uniform(-1.0, 1.0, period)
    out = np.zeros(n, dtype=np.float64)
    idx = 0
    for i in range(n):
        out[i] = buf[idx]
        avg = brightness * 0.5 * (buf[idx] + buf[(idx + 1) % period])
        buf[idx] = avg * 0.996
        idx = (idx + 1) % period
    # Soft body resonance
    t = np.arange(n) / RATE
    body = 0.15 * np.sin(2 * math.pi * freq * 0.5 * t) * np.exp(-t * 3.5)
    return soft_clip((out + body) * amp) * env(n, 0.002, min(0.35, seconds * 0.4))


def zurna(freq: float, seconds: float, amp: float = 0.12, vibrato_hz: float = 5.2) -> np.ndarray:
    """Nasal reed / folk-oboe with circular-breathing drone character."""
    n = max(1, int(RATE * seconds))
    t = np.arange(n) / RATE
    vib = 1.0 + 0.012 * np.sin(2 * math.pi * vibrato_hz * t)
    phase = np.cumsum(2 * math.pi * freq * vib / RATE)
    # Square-ish reed with odd harmonics, then soft low-pass by rolling average
    reed = np.sign(np.sin(phase)) * 0.55
    reed += 0.28 * np.sin(2 * phase)
    reed += 0.12 * np.sin(3 * phase)
    reed += 0.06 * np.sin(5 * phase)
    # Slight pulse-width wobble
    reed += 0.08 * np.sin(phase + 0.4 * np.sin(2 * math.pi * 0.7 * t))
    kernel = np.ones(9) / 9.0
    reed = np.convolve(reed, kernel, mode="same")
    return soft_clip(reed * amp) * env(n, 0.08, 0.15)


def drone(root: float, seconds: float, amp: float = 0.07) -> np.ndarray:
    """Open-fifth drone under a zurna-style continuous breath."""
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    breath = 1.0 + 0.04 * np.sin(2 * math.pi * 0.11 * t)
    sig = (
        np.sin(2 * math.pi * root * t)
        + 0.55 * np.sin(2 * math.pi * root * 1.5 * t)
        + 0.2 * np.sin(2 * math.pi * root * 2.0 * t)
    )
    return soft_clip(sig * amp * breath) * env(n, 0.8, 0.8)


def frame_hit(seconds: float = 0.18, amp: float = 0.3, pitch: float = 78.0, seed: int = 1) -> np.ndarray:
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, n)
    membrane = np.sin(2 * math.pi * pitch * t * (1.0 + 0.15 * np.exp(-t * 40))) * np.exp(-t * 18)
    slap = noise * np.exp(-t * 55)
    return soft_clip((0.75 * membrane + 0.25 * slap) * amp) * env(n, 0.001, 0.06)


def place(track: np.ndarray, clip: np.ndarray, at_s: float) -> None:
    start = int(at_s * RATE)
    end = min(len(track), start + len(clip))
    if start >= len(track) or end <= start:
        return
    track[start:end] += clip[: end - start]


def lute_phrase(root: float, degrees: list[int], note_len: float, amp: float = 0.2) -> np.ndarray:
    parts = [karplus_strong(frequency(root, d), note_len, amp=amp) for d in degrees]
    return np.concatenate(parts) if parts else np.zeros(0)


def zurna_phrase(root: float, degrees: list[int], note_len: float, amp: float = 0.1) -> np.ndarray:
    parts = []
    for d in degrees:
        # Slight legato: longer notes with short overlap-friendly release
        parts.append(zurna(frequency(root, d), note_len, amp=amp))
    return np.concatenate(parts) if parts else np.zeros(0)


def drum_pattern(seconds: float, step_s: float, accents: list[float], base_amp: float = 0.12) -> np.ndarray:
    out = np.zeros(int(RATE * seconds))
    step = max(1, int(RATE * step_s))
    for i, start in enumerate(range(0, len(out) - RATE // 8, step)):
        amp = accents[i % len(accents)] * base_amp
        hit = frame_hit(0.14 if amp > 0.15 else 0.1, amp=amp, pitch=70 + (i % 3) * 6, seed=20 + i)
        place(out, hit, start / RATE)
    return out


def mix(*layers: np.ndarray, peak: float = 0.88) -> np.ndarray:
    length = max((len(x) for x in layers), default=0)
    out = np.zeros(length)
    for layer in layers:
        out[: len(layer)] += layer
    # Gentle high-shelf roll-off (average with delayed self) for less digital glare
    out = 0.85 * out + 0.15 * np.concatenate([[0.0], out[:-1]])
    m = np.max(np.abs(out)) or 1.0
    return soft_clip(out / m * peak, 1.15)


def load_cc0(name: str, seconds: float, amp: float = 0.12) -> np.ndarray | None:
    path = SAMPLES / name
    if not path.exists():
        return None
    tmp = Path("/tmp") / f"ishtaria_{path.stem}_mix.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", str(RATE), str(tmp)],
        check=True,
        capture_output=True,
    )
    with wave.open(str(tmp), "rb") as wf:
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    tmp.unlink(missing_ok=True)
    if len(data) == 0:
        return None
    need = int(RATE * seconds)
    looped = np.tile(data, int(math.ceil(need / len(data))))[:need]
    # Fade edges of each original period lightly via overall envelope
    return looped * amp * env(need, 0.4, 0.4)


def write_ogg(path: Path, audio: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wav = path.with_suffix(".wav")
    pcm = np.clip(audio, -1.0, 1.0)
    with wave.open(str(wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes((pcm * 32767).astype(np.int16).tobytes())
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "5", str(path)],
        check=True,
        capture_output=True,
    )
    wav.unlink(missing_ok=True)
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def section_bed(root: float, seconds: float, lute_deg: list[int], zurna_deg: list[int],
                lute_len: float, zurna_len: float, drum_step: float, accents: list[float],
                lute_amp: float = 0.18, zurna_amp: float = 0.09, drone_amp: float = 0.06) -> np.ndarray:
    n = int(RATE * seconds)
    bed = drone(root, seconds, drone_amp)
    lute = lute_phrase(root * 2, lute_deg, lute_len, lute_amp)
    reed = zurna_phrase(root * 2, zurna_deg, zurna_len, zurna_amp)
    lute_loop = np.tile(lute, int(math.ceil(n / max(len(lute), 1))))[:n]
    reed_loop = np.tile(reed, int(math.ceil(n / max(len(reed), 1))))[:n]
    # Offset the reed so lute and zurna answer each other
    reed_shift = np.zeros(n)
    place(reed_shift, reed_loop, zurna_len * 0.5)
    drums = drum_pattern(seconds, drum_step, accents)
    return mix(bed, lute_loop * 0.9, reed_shift, drums)


def track_logo() -> np.ndarray:
    # Short gish-gudi call answered by a zurna fifth — jingle, not a loop.
    root = 146.83
    lute = lute_phrase(root, [0, 2, 4, 7, 4, 7, 9, 7], 0.28, 0.26)
    reed = zurna_phrase(root * 2, [4, 5, 7, 4], 0.35, 0.12)
    d = drone(root / 2, 7.0, 0.05)
    hit = np.concatenate([frame_hit(0.16, 0.35, 85, 1), np.zeros(int(RATE * 0.45)), frame_hit(0.2, 0.3, 70, 2)])
    out = np.zeros(int(RATE * 7.0))
    place(out, d, 0.0)
    place(out, lute, 0.35)
    place(out, reed, 2.4)
    place(out, hit, 0.2)
    return mix(out)


def track_plains() -> np.ndarray:
    root = 110.0
    a = section_bed(
        root, 24.0,
        lute_deg=[0, 1, 0, 2, 4, 2, 0, 7],
        zurna_deg=[0, 2, 4, 2],
        lute_len=0.5, zurna_len=0.9,
        drum_step=1.05, accents=[1.0, 0.35, 0.55, 0.35],
        lute_amp=0.16, zurna_amp=0.07, drone_amp=0.055,
    )
    b = section_bed(
        root * 9 / 8, 24.0,
        lute_deg=[0, 2, 3, 2, 4, 3, 0, 4],
        zurna_deg=[4, 2, 0, 2, 4],
        lute_len=0.45, zurna_len=0.75,
        drum_step=1.05, accents=[0.8, 0.3, 0.45, 0.3, 1.0, 0.3],
        lute_amp=0.17, zurna_amp=0.08, drone_amp=0.05,
    )
    pad = load_cc0("lyre_pad.ogg", 48.0, 0.08)
    layers = [np.concatenate([a, b])]
    if pad is not None:
        layers.append(pad)
    return mix(*layers)


def track_city() -> np.ndarray:
    root = 130.81
    a = section_bed(
        root, 21.0,
        lute_deg=[0, 2, 3, 2, 4, 3, 2, 0, 4, 5, 4, 2],
        zurna_deg=[0, 3, 4, 3, 0],
        lute_len=0.26, zurna_len=0.42,
        drum_step=0.52, accents=[1.0, 0.25, 0.45, 0.25],
        lute_amp=0.18, zurna_amp=0.08, drone_amp=0.05,
    )
    b = section_bed(
        root, 21.0,
        lute_deg=[4, 5, 4, 2, 0, 2, 4, 7, 5, 4],
        zurna_deg=[2, 4, 5, 4, 2, 0],
        lute_len=0.24, zurna_len=0.38,
        drum_step=0.52, accents=[1.0, 0.3, 0.55, 0.3, 0.7, 0.3],
        lute_amp=0.19, zurna_amp=0.09, drone_amp=0.045,
    )
    drum_pad = load_cc0("frame_drum.ogg", 42.0, 0.07)
    layers = [np.concatenate([a, b])]
    if drum_pad is not None:
        layers.append(drum_pad)
    return mix(*layers)


def track_temple() -> np.ndarray:
    root = 98.0
    # Slow lute + sustained zurna fifths — sparse, no busy street drums
    bed = drone(root, 52.0, 0.08)
    lute = lute_phrase(root * 2, [0, 4, 5, 4, 7, 4, 0, 4], 0.75, 0.14)
    reed = zurna_phrase(root * 2, [0, 4, 7, 4, 0], 1.1, 0.07)
    n = int(RATE * 52.0)
    lute_l = np.tile(lute, int(math.ceil(n / len(lute))))[:n]
    reed_l = np.zeros(n)
    place(reed_l, np.tile(reed, int(math.ceil(n / len(reed))))[:n], 1.2)
    # Occasional soft hit
    hits = np.zeros(n)
    for t in (4.0, 16.0, 28.0, 40.0):
        place(hits, frame_hit(0.22, 0.12, 60, int(t)), t)
    pad = load_cc0("lyre_pad.ogg", 52.0, 0.06)
    layers = [bed, lute_l, reed_l, hits]
    if pad is not None:
        layers.append(pad)
    return mix(*layers)


def track_cedar() -> np.ndarray:
    root = 87.31
    a = section_bed(
        root, 26.0,
        lute_deg=[0, 1, 3, 4, 3, 1, 0, 4],
        zurna_deg=[0, 3, 4, 3, 1],
        lute_len=0.6, zurna_len=0.95,
        drum_step=1.2, accents=[0.7, 0.25, 0.4, 0.25],
        lute_amp=0.15, zurna_amp=0.07, drone_amp=0.07,
    )
    b = section_bed(
        root * 4 / 3, 26.0,
        lute_deg=[0, 2, 4, 5, 4, 2, 0],
        zurna_deg=[4, 5, 7, 5, 4],
        lute_len=0.55, zurna_len=0.85,
        drum_step=1.2, accents=[0.6, 0.2, 0.35, 0.2],
        lute_amp=0.14, zurna_amp=0.08, drone_amp=0.06,
    )
    air = zurna(root * 6, 52.0, amp=0.025, vibrato_hz=4.0)
    return mix(np.concatenate([a, b]), air)


def track_waters() -> np.ndarray:
    # Enki of the waters: deeper drone, sparse lute, long zurna breaths
    root = 73.42
    bed = drone(root, 48.0, 0.1)
    lute = lute_phrase(root * 2, [0, 2, 0, 3, 2, 0, 4, 2], 0.7, 0.12)
    reed = zurna_phrase(root * 2, [0, 2, 4, 2, 0], 1.3, 0.08)
    n = int(RATE * 48.0)
    lute_l = np.tile(lute, int(math.ceil(n / len(lute))))[:n]
    reed_l = np.zeros(n)
    place(reed_l, np.tile(reed, int(math.ceil(n / len(reed))))[:n], 0.8)
    t = np.arange(n) / RATE
    ripple = 0.035 * np.sin(2 * math.pi * 0.13 * t) * np.sin(2 * math.pi * root * 3 * t)
    return mix(bed, lute_l, reed_l, ripple)


TRACKS = {
    "logo.ogg": track_logo,
    "plains.ogg": track_plains,
    "city.ogg": track_city,
    "temple.ogg": track_temple,
    "cedar_forest.ogg": track_cedar,
    "waters.ogg": track_waters,
}


def main() -> None:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    readme = SAMPLES / "README.md"
    readme.write_text(
        "# Soundtrack sample sources (CC0)\n\n"
        "Mixed under newly synthesized gish-gudi / zurna beds (`tools/compose_music.py`).\n"
        "Inspired by public descriptions of Sumerian instruments (lute ancestor and reed "
        "oboe with circular-breathing drone), not by sampling any commercial recording.\n\n"
        "| File | Source | Licence |\n"
        "| --- | --- | --- |\n"
        "| `lyre_pad.ogg` | [Lyre](https://freesound.org/people/Hedmarking/sounds/191883/) "
        "by Hedmarking (Freesound preview, mono) | CC0 |\n"
        "| `lyre_pluck.ogg` | [Lyre harp single note](https://freesound.org/people/Biggertigger2006/sounds/722897/) "
        "by Biggertigger2006 | CC0 |\n"
        "| `frame_drum.ogg` | [detuned frame drum bass](https://freesound.org/people/HarpDave/sounds/518943/) "
        "by HarpDave | CC0 |\n"
    )
    for name, builder in TRACKS.items():
        write_ogg(OUT / name, builder())


if __name__ == "__main__":
    main()
