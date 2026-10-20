#!/usr/bin/env python3
"""Synthesize Early Dynastic–inspired soundtrack for the Gilgamesh disk.

Inspired by public descriptions of Sumerian performance practice (gish-gudi lute
and zurna reed with circular-breathing drone — e.g. reconstructions that retell
"Gilgamesh, Enkidu and the Nether World"), not by sampling any copyrighted
recording. Motifs are newly synthesized. Optional CC0 loops in tools/music-samples/
are mixed underneath.

Dramaturgy (not a single tiled phrase):
  - Shared Gilgamesh leitmotif on the cover jingle, city, and temple tracks
  - Section timeline (verse / break / verse') with silence and dynamics
  - Heterophony: zurna shadows the lute with local ornaments
  - Ambient loops crossfade at the ends for seamless replay

    python3 tools/compose_music.py
"""
from __future__ import annotations

import math
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "music"
SAMPLES = Path(__file__).resolve().parent / "music-samples"
RATE = 44100

# Just-intonation heptatonic sketch around a modal centre (lyre / lute of Ur notes).
SCALE = np.array([1.0, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2.0], dtype=np.float64)

# Shared call of Gilgamesh — degrees relative to the track root (octave-doubled voice).
# Hapax of intervals: rise to the fifth, settle on the fourth, open octave.
LEITMOTIF = [0, 2, 4, 3, 4, 7]
LEITMOTIF_ANSWER = [4, 5, 7, 5, 4, 2]


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


def karplus_strong(
    freq: float,
    seconds: float,
    amp: float = 0.25,
    brightness: float = 0.55,
    seed: int = 7,
) -> np.ndarray:
    """Plucked-string model — gish-gudi / lyre attack with a woody decay."""
    n = max(1, int(RATE * seconds))
    period = max(2, int(RATE / max(freq, 20.0)))
    rng = np.random.default_rng(seed)
    buf = rng.uniform(-1.0, 1.0, period)
    out = np.zeros(n, dtype=np.float64)
    idx = 0
    decay = 0.996
    for i in range(n):
        out[i] = buf[idx]
        avg = brightness * 0.5 * (buf[idx] + buf[(idx + 1) % period])
        buf[idx] = avg * decay
        idx = (idx + 1) % period
    t = np.arange(n) / RATE
    body = 0.15 * np.sin(2 * math.pi * freq * 0.5 * t) * np.exp(-t * 3.5)
    return soft_clip((out + body) * amp) * env(n, 0.002, min(0.35, seconds * 0.4))


def zurna(
    freq: float,
    seconds: float,
    amp: float = 0.12,
    vibrato_hz: float = 5.2,
    ornament: bool = False,
) -> np.ndarray:
    """Nasal reed / folk-oboe with circular-breathing drone character."""
    n = max(1, int(RATE * seconds))
    t = np.arange(n) / RATE
    # Vibrato grows toward the note end (lament ornament), not a constant wobble.
    vib_depth = 0.008 + (0.018 if ornament else 0.006) * (t / max(seconds, 1e-6))
    vib = 1.0 + vib_depth * np.sin(2 * math.pi * vibrato_hz * t)
    if ornament and seconds > 0.2:
        # Short upward scoop into the pitch (mordent-ish attack).
        scoop = np.linspace(0.94, 1.0, min(n, int(RATE * 0.06)))
        vib[: len(scoop)] *= scoop
    phase = np.cumsum(2 * math.pi * freq * vib / RATE)
    reed = np.sign(np.sin(phase)) * 0.55
    reed += 0.28 * np.sin(2 * phase)
    reed += 0.12 * np.sin(3 * phase)
    reed += 0.06 * np.sin(5 * phase)
    reed += 0.08 * np.sin(phase + 0.4 * np.sin(2 * math.pi * 0.7 * t))
    kernel = np.ones(9) / 9.0
    reed = np.convolve(reed, kernel, mode="same")
    return soft_clip(reed * amp) * env(n, 0.08, 0.15)


def drone(root: float, seconds: float, amp: float = 0.07, breathe: bool = True) -> np.ndarray:
    """Open-fifth drone under a zurna-style continuous breath."""
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    breath = 1.0 + (0.05 * np.sin(2 * math.pi * 0.09 * t) if breathe else 0.0)
    # Slow amplitude swell so the bed is not a flat hum.
    swell = 0.72 + 0.28 * (0.5 - 0.5 * np.cos(2 * math.pi * t / max(seconds, 1e-6)))
    sig = (
        np.sin(2 * math.pi * root * t)
        + 0.55 * np.sin(2 * math.pi * root * 1.5 * t)
        + 0.2 * np.sin(2 * math.pi * root * 2.0 * t)
    )
    return soft_clip(sig * amp * breath * swell) * env(n, 0.8, 0.8)


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


def plate_dynamics(n: int, shape: str = "arch") -> np.ndarray:
    """Whole-track gain curve so loops are not flat."""
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    if shape == "sparse":
        # Soft peaks with quieter valleys — for plains / waters.
        return 0.55 + 0.45 * (0.5 + 0.5 * np.sin(2 * math.pi * 2.0 * t))
    if shape == "procession":
        return 0.7 + 0.3 * (0.5 - 0.5 * np.cos(2 * math.pi * 3.0 * t))
    if shape == "litany":
        return 0.6 + 0.4 * np.clip(np.sin(math.pi * t) ** 1.4, 0.0, 1.0)
    # Default arch
    return 0.65 + 0.35 * np.sin(math.pi * t)


def mix(*layers: np.ndarray, peak: float = 0.88, dynamics: str | None = "arch") -> np.ndarray:
    length = max((len(x) for x in layers), default=0)
    out = np.zeros(length)
    for layer in layers:
        out[: len(layer)] += layer
    out = 0.85 * out + 0.15 * np.concatenate([[0.0], out[:-1]])
    if dynamics:
        out *= plate_dynamics(length, dynamics)
    m = np.max(np.abs(out)) or 1.0
    return soft_clip(out / m * peak, 1.15)


def crossfade_loop(audio: np.ndarray, fade_s: float = 1.5) -> np.ndarray:
    """Make an ambient loop join cleanly when the client restarts the stream."""
    n_fade = min(len(audio) // 4, int(RATE * fade_s))
    if n_fade < 64:
        return audio
    out = audio.copy()
    fade_in = np.linspace(0.0, 1.0, n_fade)
    fade_out = 1.0 - fade_in
    head = out[:n_fade].copy()
    out[-n_fade:] = out[-n_fade:] * fade_out + head * fade_in
    return out


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
    return looped * amp * env(need, 0.4, 0.4)


def load_pluck_oneshot(amp: float = 0.35) -> np.ndarray | None:
    """Single CC0 lyre attack mixed onto synthesized plucks for wooden bite."""
    path = SAMPLES / "lyre_pluck.ogg"
    if not path.exists():
        return None
    tmp = Path("/tmp") / "ishtaria_lyre_pluck.wav"
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
    data = data * amp
    # Trim trailing silence-ish tail for placement on note attacks.
    peak = np.max(np.abs(data)) or 1.0
    thresh = peak * 0.02
    end = len(data)
    while end > RATE // 20 and abs(data[end - 1]) < thresh:
        end -= 1
    return data[:end]


_PLUCK: np.ndarray | None = None


def get_pluck() -> np.ndarray | None:
    global _PLUCK
    if _PLUCK is None:
        _PLUCK = load_pluck_oneshot()
    return _PLUCK


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


def mutate_degrees(degrees: list[int], seed: int, amount: int = 1) -> list[int]:
    """Local heterophonic / verse' variation — keep contour, nudge a few steps."""
    rng = np.random.default_rng(seed)
    out = list(degrees)
    if len(out) < 2:
        return out
    for i in rng.choice(len(out), size=min(amount, len(out)), replace=False):
        out[i] = int(np.clip(out[i] + int(rng.choice([-1, 1])), 0, 9))
    return out


def heterophony(degrees: list[int], seed: int = 3) -> list[int]:
    """Zurna shadows the lute: same contour, occasional neighbour-tone ornament."""
    rng = np.random.default_rng(seed)
    out: list[int] = []
    for i, d in enumerate(degrees):
        out.append(d)
        if i > 0 and i < len(degrees) - 1 and rng.random() < 0.35:
            neighbour = d + int(rng.choice([-1, 1]))
            out.append(int(np.clip(neighbour, 0, 9)))
    return out


def lute_phrase(
    root: float,
    degrees: list[int],
    note_lens: list[float] | float,
    amp: float = 0.2,
    seed: int = 11,
    with_pluck: bool = True,
) -> np.ndarray:
    if isinstance(note_lens, float):
        lens = [note_lens] * len(degrees)
    else:
        lens = list(note_lens)
        while len(lens) < len(degrees):
            lens.append(lens[-1] if lens else 0.4)
    parts: list[np.ndarray] = []
    pluck = get_pluck() if with_pluck else None
    for i, d in enumerate(degrees):
        note = karplus_strong(
            frequency(root, d),
            lens[i],
            amp=amp,
            brightness=0.5 + 0.08 * (i % 3),
            seed=seed + i * 17,
        )
        if pluck is not None and lens[i] > 0.12:
            attack = pluck.copy()
            # Match rough pitch colour by mild resampling via index skip/hold.
            ratio = frequency(root, d) / 220.0
            step = max(0.5, min(2.0, ratio))
            idx = (np.arange(len(attack)) * step).astype(int)
            idx = idx[idx < len(attack)]
            attack = attack[idx] * (0.22 * amp / 0.2)
            blended = note.copy()
            place(blended, attack, 0.0)
            note = blended
        parts.append(note)
    return np.concatenate(parts) if parts else np.zeros(0)


def zurna_phrase(
    root: float,
    degrees: list[int],
    note_lens: list[float] | float,
    amp: float = 0.1,
    ornament_every: int = 2,
) -> np.ndarray:
    if isinstance(note_lens, float):
        lens = [note_lens] * len(degrees)
    else:
        lens = list(note_lens)
        while len(lens) < len(degrees):
            lens.append(lens[-1] if lens else 0.5)
    parts = []
    for i, d in enumerate(degrees):
        parts.append(
            zurna(
                frequency(root, d),
                lens[i],
                amp=amp,
                ornament=(i % ornament_every == ornament_every - 1),
            )
        )
    return np.concatenate(parts) if parts else np.zeros(0)


def drum_pattern(
    seconds: float,
    step_s: float,
    accents: list[float],
    base_amp: float = 0.12,
    cycle: int | None = None,
) -> np.ndarray:
    """Frame-drum hits. Optional odd cycle (e.g. 5 or 7) for non-4/4 procession feel."""
    out = np.zeros(int(RATE * seconds))
    step = max(1, int(RATE * step_s))
    period = cycle or len(accents)
    for i, start in enumerate(range(0, len(out) - RATE // 8, step)):
        if cycle and (i % period) >= len(accents):
            continue  # rest inside odd metre
        amp = accents[i % len(accents)] * base_amp
        if amp <= 0.01:
            continue
        hit = frame_hit(0.14 if amp > 0.15 else 0.1, amp=amp, pitch=70 + (i % 3) * 6, seed=20 + i)
        place(out, hit, start / RATE)
    return out


@dataclass
class Section:
    """One breath of the piece: instruments and optional silence after."""
    kind: str  # "full" | "lute" | "reed" | "drums" | "drone" | "rest"
    seconds: float
    lute_deg: list[int] | None = None
    zurna_deg: list[int] | None = None
    lute_len: float = 0.4
    zurna_len: float = 0.7
    drum_step: float = 1.0
    accents: list[float] | None = None
    lute_amp: float = 0.17
    zurna_amp: float = 0.08
    drone_amp: float = 0.055
    drum_amp: float = 0.12
    drum_cycle: int | None = None
    seed: int = 1


def render_section(root: float, sec: Section) -> np.ndarray:
    n = int(RATE * sec.seconds)
    if sec.kind == "rest":
        return np.zeros(n)

    layers: list[np.ndarray] = []
    if sec.kind in ("full", "drone", "lute", "reed"):
        layers.append(drone(root, sec.seconds, sec.drone_amp))

    if sec.kind in ("full", "lute") and sec.lute_deg:
        lute = lute_phrase(root * 2, sec.lute_deg, sec.lute_len, sec.lute_amp, seed=sec.seed)
        lute_l = np.tile(lute, int(math.ceil(n / max(len(lute), 1))))[:n]
        # Soften repeats inside the section so tiling is less obvious.
        reps = max(1, n // max(len(lute), 1))
        gain = np.ones(n)
        for r in range(reps):
            start = r * len(lute)
            end = min(n, start + len(lute))
            # Alternate slightly quieter second statements.
            gain[start:end] *= 0.92 if r % 2 else 1.0
        layers.append(lute_l * gain)

    if sec.kind in ("full", "reed") and sec.zurna_deg:
        reed_deg = sec.zurna_deg
        reed = zurna_phrase(root * 2, reed_deg, sec.zurna_len, sec.zurna_amp)
        reed_l = np.zeros(n)
        tiled = np.tile(reed, int(math.ceil(n / max(len(reed), 1))))[:n]
        # Answer the lute: enter a little late.
        place(reed_l, tiled, min(sec.seconds * 0.12, sec.zurna_len * 0.45))
        layers.append(reed_l)

    if sec.kind in ("full", "drums") and sec.accents:
        layers.append(
            drum_pattern(
                sec.seconds,
                sec.drum_step,
                sec.accents,
                base_amp=sec.drum_amp,
                cycle=sec.drum_cycle,
            )
        )

    if not layers:
        return np.zeros(n)
    length = max(len(x) for x in layers)
    out = np.zeros(length)
    for layer in layers:
        out[: len(layer)] += layer
    return out[:n]


def compose_sections(root: float, sections: list[Section], root_shifts: list[float] | None = None) -> np.ndarray:
    parts: list[np.ndarray] = []
    for i, sec in enumerate(sections):
        shift = 1.0 if not root_shifts else root_shifts[min(i, len(root_shifts) - 1)]
        parts.append(render_section(root * shift, sec))
    return np.concatenate(parts) if parts else np.zeros(0)


def track_logo() -> np.ndarray:
    """Cover jingle: drum → leitmotif lute → zurna answer → shared open fifth."""
    root = 146.83  # D3-ish
    duration = 14.0
    out = np.zeros(int(RATE * duration))
    place(out, drone(root / 2, duration, 0.045), 0.0)
    place(out, frame_hit(0.18, 0.38, 88, 1), 0.25)
    place(out, frame_hit(0.14, 0.22, 72, 2), 0.55)

    lute = lute_phrase(
        root,
        LEITMOTIF,
        [0.32, 0.28, 0.36, 0.3, 0.34, 0.55],
        amp=0.28,
        seed=101,
    )
    place(out, lute, 1.0)

    answer = zurna_phrase(
        root * 2,
        LEITMOTIF_ANSWER,
        [0.38, 0.34, 0.42, 0.36, 0.4, 0.55],
        amp=0.13,
        ornament_every=1,
    )
    place(out, answer, 4.2)

    # Shared cadence: lute + zurna on open fifth / octave.
    cadence_lute = lute_phrase(root, [4, 7, 7], [0.4, 0.45, 0.9], amp=0.22, seed=202)
    cadence_reed = zurna_phrase(root * 2, [4, 7], [0.55, 1.1], amp=0.1, ornament_every=1)
    place(out, cadence_lute, 8.4)
    place(out, cadence_reed, 8.7)
    place(out, frame_hit(0.22, 0.28, 65, 3), 11.2)
    # Soft final breath of drone only — leave silence for the cover UI.
    return mix(out, peak=0.9, dynamics=None)


def track_plains() -> np.ndarray:
    root = 110.0
    motif_a = [0, 1, 0, 2, 4, 2, 0, 7]
    motif_b = mutate_degrees(motif_a, seed=41, amount=2)
    sections = [
        Section("drone", 6.0, drone_amp=0.06, seed=1),
        Section(
            "lute",
            14.0,
            lute_deg=motif_a,
            lute_len=0.55,
            lute_amp=0.15,
            drone_amp=0.05,
            seed=2,
        ),
        Section("rest", 3.0),
        Section(
            "reed",
            12.0,
            zurna_deg=heterophony([0, 2, 4, 2, 0], seed=5),
            zurna_len=0.95,
            zurna_amp=0.075,
            drone_amp=0.055,
            seed=3,
        ),
        Section("rest", 2.5),
        Section(
            "full",
            16.0,
            lute_deg=motif_b,
            zurna_deg=heterophony(motif_b, seed=6),
            lute_len=0.5,
            zurna_len=0.85,
            drum_step=1.1,
            accents=[0.7, 0.0, 0.35, 0.0],
            lute_amp=0.16,
            zurna_amp=0.07,
            drone_amp=0.05,
            drum_amp=0.08,
            seed=4,
        ),
        Section("drone", 5.0, drone_amp=0.045, seed=5),
        Section(
            "lute",
            10.0,
            lute_deg=mutate_degrees(motif_a, seed=55, amount=1),
            lute_len=0.6,
            lute_amp=0.14,
            drone_amp=0.048,
            seed=6,
        ),
    ]
    bed = compose_sections(root, sections)
    pad = load_cc0("lyre_pad.ogg", len(bed) / RATE, 0.07)
    layers = [bed]
    if pad is not None:
        layers.append(pad)
    return crossfade_loop(mix(*layers, dynamics="sparse"), 1.8)


def track_city() -> np.ndarray:
    root = 130.81
    street = [0, 2, 3, 2, 4, 3, 2, 0, 4, 5, 4, 2]
    street_b = mutate_degrees(street, seed=77, amount=3)
    # Processional 7-cycle feel: accents of length 4 inside cycle 7 → rests.
    sections = [
        Section(
            "drums",
            4.0,
            accents=[1.0, 0.25, 0.45, 0.25],
            drum_step=0.48,
            drum_amp=0.14,
            drum_cycle=7,
            drone_amp=0.04,
            seed=1,
        ),
        Section(
            "full",
            18.0,
            lute_deg=LEITMOTIF + street[:6],
            zurna_deg=heterophony(LEITMOTIF + street[:6], seed=8),
            lute_len=0.26,
            zurna_len=0.4,
            drum_step=0.48,
            accents=[1.0, 0.25, 0.5, 0.25],
            lute_amp=0.19,
            zurna_amp=0.085,
            drone_amp=0.045,
            drum_amp=0.13,
            drum_cycle=7,
            seed=2,
        ),
        Section(
            "drums",
            5.0,
            accents=[0.85, 0.0, 0.4, 0.0, 0.55],
            drum_step=0.48,
            drum_amp=0.12,
            drone_amp=0.035,
            seed=3,
        ),
        Section(
            "full",
            18.0,
            lute_deg=street_b,
            zurna_deg=heterophony(street_b, seed=9),
            lute_len=0.24,
            zurna_len=0.38,
            drum_step=0.46,
            accents=[1.0, 0.3, 0.55, 0.3],
            lute_amp=0.2,
            zurna_amp=0.09,
            drone_amp=0.042,
            drum_amp=0.14,
            drum_cycle=7,
            seed=4,
        ),
        Section(
            "lute",
            8.0,
            lute_deg=LEITMOTIF,
            lute_len=0.35,
            lute_amp=0.17,
            drone_amp=0.04,
            seed=5,
        ),
    ]
    bed = compose_sections(root, sections)
    drum_pad = load_cc0("frame_drum.ogg", len(bed) / RATE, 0.06)
    layers = [bed]
    if drum_pad is not None:
        layers.append(drum_pad)
    return crossfade_loop(mix(*layers, dynamics="procession"), 1.4)


def track_temple() -> np.ndarray:
    root = 98.0
    litany = [0, 4, 5, 4, 7, 4, 0, 4]
    sections = [
        Section("drone", 8.0, drone_amp=0.085, seed=1),
        Section(
            "lute",
            14.0,
            lute_deg=LEITMOTIF,
            lute_len=0.85,
            lute_amp=0.13,
            drone_amp=0.075,
            seed=2,
        ),
        Section("rest", 4.0),
        Section(
            "reed",
            16.0,
            zurna_deg=heterophony([0, 4, 7, 4, 0], seed=2),
            zurna_len=1.35,
            zurna_amp=0.07,
            drone_amp=0.08,
            seed=3,
        ),
        Section("rest", 3.5),
        Section(
            "lute",
            14.0,
            lute_deg=litany,
            lute_len=0.8,
            lute_amp=0.135,
            drone_amp=0.07,
            seed=4,
        ),
        Section(
            "full",
            12.0,
            lute_deg=mutate_degrees(litany, seed=12, amount=1),
            zurna_deg=LEITMOTIF_ANSWER,
            lute_len=0.75,
            zurna_len=1.2,
            accents=[0.35, 0.0, 0.0, 0.0],
            drum_step=4.0,
            lute_amp=0.12,
            zurna_amp=0.065,
            drone_amp=0.075,
            drum_amp=0.1,
            seed=5,
        ),
        Section("drone", 6.0, drone_amp=0.06, seed=6),
    ]
    bed = compose_sections(root, sections)
    # Sparse ceremonial hits as verse punctuation (not a groove).
    hits = np.zeros(len(bed))
    for t, seed in ((10.0, 1), (28.0, 2), (46.0, 3), (62.0, 4)):
        if t * RATE < len(hits):
            place(hits, frame_hit(0.24, 0.11, 58, seed), t)
    pad = load_cc0("lyre_pad.ogg", len(bed) / RATE, 0.055)
    layers = [bed, hits]
    if pad is not None:
        layers.append(pad)
    return crossfade_loop(mix(*layers, dynamics="litany"), 2.0)


def track_cedar() -> np.ndarray:
    root = 87.31
    dark = [0, 1, 3, 4, 3, 1, 0, 4]
    # Occasional out-of-scale neighbour as forest dissonance (degree 6 is already in scale;
    # push one step to a sharpened colour via degree bump in mutate).
    dark_b = mutate_degrees(dark, seed=99, amount=2)
    sections = [
        Section("drone", 5.0, drone_amp=0.07, seed=1),
        Section(
            "full",
            18.0,
            lute_deg=dark,
            zurna_deg=heterophony(dark, seed=11),
            lute_len=0.62,
            zurna_len=1.0,
            drum_step=1.25,
            accents=[0.55, 0.0, 0.3, 0.0],
            lute_amp=0.145,
            zurna_amp=0.07,
            drone_amp=0.065,
            drum_amp=0.09,
            seed=2,
        ),
        Section("rest", 2.0),
        Section(
            "reed",
            12.0,
            zurna_deg=[0, 3, 4, 5, 4, 3],
            zurna_len=1.05,
            zurna_amp=0.08,
            drone_amp=0.07,
            seed=3,
        ),
        Section(
            "full",
            18.0,
            lute_deg=dark_b,
            zurna_deg=heterophony(dark_b, seed=12),
            lute_len=0.55,
            zurna_len=0.9,
            drum_step=1.2,
            accents=[0.5, 0.15, 0.35, 0.15],
            lute_amp=0.14,
            zurna_amp=0.075,
            drone_amp=0.06,
            drum_amp=0.085,
            seed=4,
        ),
        Section("lute", 8.0, lute_deg=[0, 4, 3, 0], lute_len=0.7, lute_amp=0.12, drone_amp=0.055, seed=5),
    ]
    # Root shift into the second half of the forest (fourth up).
    shifts = [1.0, 1.0, 1.0, 1.0, 4 / 3, 4 / 3]
    bed = compose_sections(root, sections, root_shifts=shifts)
    # Distant air / echo: delayed quiet zurna ghost.
    air = zurna(root * 6, len(bed) / RATE, amp=0.022, vibrato_hz=4.0, ornament=False)
    echo = np.zeros_like(bed)
    place(echo, bed * 0.18, 0.45)
    return crossfade_loop(mix(bed, air, echo, dynamics="sparse"), 1.8)


def track_waters() -> np.ndarray:
    root = 73.42
    ripple_deg = [0, 2, 0, 3, 2, 0, 4, 2]
    sections = [
        Section("drone", 10.0, drone_amp=0.1, seed=1),
        Section(
            "lute",
            12.0,
            lute_deg=ripple_deg,
            lute_len=0.75,
            lute_amp=0.11,
            drone_amp=0.09,
            seed=2,
        ),
        Section("rest", 4.0),
        Section(
            "reed",
            14.0,
            zurna_deg=[0, 2, 4, 2, 0],
            zurna_len=1.45,
            zurna_amp=0.075,
            drone_amp=0.095,
            seed=3,
        ),
        Section("rest", 3.0),
        Section(
            "lute",
            12.0,
            lute_deg=mutate_degrees(ripple_deg, seed=33, amount=1),
            lute_len=0.8,
            lute_amp=0.105,
            drone_amp=0.085,
            seed=4,
        ),
        Section("drone", 8.0, drone_amp=0.08, seed=5),
    ]
    bed = compose_sections(root, sections)
    n = len(bed)
    t = np.arange(n) / RATE
    ripple = 0.03 * np.sin(2 * math.pi * 0.11 * t) * np.sin(2 * math.pi * root * 3 * t)
    ripple += 0.015 * np.sin(2 * math.pi * 0.07 * t + 1.2) * np.sin(2 * math.pi * root * 4.5 * t)
    return crossfade_loop(mix(bed, ripple, dynamics="sparse"), 2.0)


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
        "Tracks use a shared Gilgamesh leitmotif, sectioned timelines (verse / rest / answer),\n"
        "heterophonic lute–zurna lines, and crossfaded ambient loops.\n\n"
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
