#!/usr/bin/env python3
"""Render the spoken lines of the dialogues with Piper into OGG Vorbis files.

Every line is normalised to the loudness of its language (`loudness:` in voice/voices.yaml, LUFS).

Usage: render_voices.py [--out DIR] [--voices DIR] [--only NPC_ID] [--lang cs] [--jobs N] [--dry-run]

Every node of a dialogue that shows a `text_key` is spoken by the NPC owning the dialogue (the
choices of the player are not). The result is `<out>/media/voice/<language>/<text_key>.ogg`.
A text with {player} (the player's own name) is spoken with `<key>.say` or a form of address
(see spoken_text). A key that already has a file in the source tree (`media/voice/<language>/<text_key>.ogg`, a human
recording) is left alone, so a community dub replaces a synthetic voice by adding a file of the
same name. Languages come from `voice/voices.yaml` (`models:`) and the matching `i18n/<language>.yaml`;
a language without a model or translation is skipped with a warning. Anything that fails to render
makes the exit status nonzero: a package must not silently ship without its voices.

Voice models (`<model>.onnx` + `.onnx.json`) are looked up in --voices, $ISHTARIA_VOICES and a few
system directories; nothing is downloaded.
"""
import argparse
import concurrent.futures
import json
import math
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SYSTEM_VOICE_DIRS = [
    "/usr/share/piper-voices",
    "/usr/share/ishtaria/piper-voices",
    "/usr/share/claude-tts-cz/piper-voices",
    str(pathlib.Path.home() / ".cache/noveknihy/piper"),
]
# Named filter presets a voice profile can ask for; `pitch` (semitones) and `tempo` are separate numbers.
EQ = {
    "bass": "equalizer=f=120:t=q:w=1:g=4",
    "bright": "equalizer=f=3500:t=q:w=1:g=3",
    "muffled": "lowpass=f=3200",
}
ECHO = {
    "crypt": "aecho=0.8:0.7:70:0.3",
    "hall": "aecho=0.8:0.8:40:0.2",
}
DEFAULTS = {"length_scale": 1.0, "noise_scale": 0.667, "noise_w": 0.8, "pitch": 0.0, "tempo": 1.0}


def warn(message):
    print(f"render_voices: warning: {message}", file=sys.stderr)


def load_yaml(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def find_model(name, dirs):
    for directory in dirs:
        model = pathlib.Path(directory) / f"{name}.onnx"
        if model.is_file():
            config = pathlib.Path(f"{model}.json")
            return model, config if config.is_file() else None
    return None, None


def profile(voices, npc, language):
    merged = dict(DEFAULTS)
    merged.update(voices.get("default") or {})
    entry = (voices.get("npcs") or {}).get(npc) or {}
    merged.update({k: v for k, v in entry.items() if k not in voices.get("models", {})})
    merged.update(entry.get(language) or {})
    return merged


def spoken_lines(root):
    """(npc id, text_key) for every NPC line, in a stable order, first speaker wins."""
    dialogue_owner = {}
    for path in sorted((root / "npcs").glob("*.yaml")):
        for npc in load_yaml(path) or []:
            dialogue_owner.setdefault(npc["dialogue"], npc["id"])
    lines = {}
    for path in sorted((root / "dialogues").glob("*.yaml")):
        dialogue = load_yaml(path)
        owner = dialogue_owner.get(dialogue["id"])
        if owner is None:
            continue
        for node in dialogue["nodes"].values():
            key = node.get("text_key")
            if key:
                lines.setdefault(key, owner)
    return sorted((owner, key) for key, owner in lines.items())


def spoken_text(strings, key, voices, language):
    """What is said for a key. The displayed text may hold {player}, the name the player chose, which
    a recording cannot contain: `<key>.say` in the i18n file replaces the text for the voice, otherwise
    {player} becomes a form of address from `placeholders.player.<language>` in voices.yaml."""
    text = str(strings.get(f"{key}.say") or strings[key])
    address = ((voices.get("placeholders") or {}).get("player") or {}).get(language, "")
    return " ".join(text.replace("{player}", address).replace(" ,", ",").split())


def audio_filter(settings):
    filters = []
    pitch = float(settings["pitch"])
    tempo = float(settings["tempo"])
    if pitch or tempo != 1.0:
        filters.append(f"rubberband=pitch={math.pow(2, pitch / 12):.5f}:tempo={tempo:.4f}")
    if settings.get("eq"):
        filters.append(EQ[settings["eq"]])
    if settings.get("echo"):
        filters.append(ECHO[settings["echo"]])
    return ",".join(filters)


DEFAULT_LUFS = -18.0


def loudness_filter(wav, chain, lufs):
    """The filter chain followed by an exact normalisation to `lufs` (EBU R128 integrated loudness):
    the first pass measures the line, the second applies one linear gain and a limiter at -2 dBFS
    that only catches a peak. Nothing is compressed, and a short line is as exact as a long one
    (`loudnorm` itself falls back to its dynamic mode on lines of a few seconds)."""
    prefix = chain + "," if chain else ""
    probe = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-i", str(wav), "-af", prefix + f"loudnorm=I={lufs}:TP=-2:LRA=30:print_format=json", "-f", "null", "-"],
        check=True, capture_output=True, text=True,
    ).stderr
    # The measurement is the JSON object that follows the filter's log lines; anything after it is ignored.
    data, _ = json.JSONDecoder().raw_decode(probe[probe.rindex("{", 0, probe.index('"input_i"')):])
    gain = lufs - float(data["input_i"])
    return prefix + f"volume={gain:.2f}dB,alimiter=limit=0.794:attack=2:release=60:level=disabled"


def render(job):
    text, model, config, settings, speaker, target, lufs = job
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voice-") as tmp:
        wav = pathlib.Path(tmp) / "line.wav"
        command = [
            "piper", "-m", str(model),
            "--length-scale", str(settings["length_scale"]),
            "--noise-scale", str(settings["noise_scale"]),
            "--noise-w-scale", str(settings["noise_w"]),
            "-f", str(wav),
        ]
        if config:
            command += ["-c", str(config)]
        if speaker is not None:
            command += ["-s", str(speaker)]
        subprocess.run(command, input=text.encode("utf-8"), check=True, capture_output=True)
        partial = target.with_name(target.name + ".part")
        subprocess.run(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(wav),
             "-af", loudness_filter(wav, audio_filter(settings), lufs), "-ac", "1", "-ar", "24000", "-c:a", "libvorbis", "-q:a", "4", "-f", "ogg", str(partial)],
            check=True, capture_output=True,
        )
        partial.replace(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=str(ROOT / "debian" / "voice-build"), help="output tree (gets media/voice/...)")
    parser.add_argument("--voices", action="append", default=[], help="directory with Piper models (repeatable)")
    parser.add_argument("--only", help="render only the lines of this NPC id")
    parser.add_argument("--lang", action="append", help="render only this language (repeatable)")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for tool in ("piper", "ffmpeg"):
        if not args.dry_run and not shutil.which(tool):
            sys.exit(f"render_voices: {tool} not found")
    voices = load_yaml(ROOT / "voice" / "voices.yaml")
    dirs = args.voices + ([os.environ["ISHTARIA_VOICES"]] if os.environ.get("ISHTARIA_VOICES") else []) + SYSTEM_VOICE_DIRS
    out = pathlib.Path(args.out)
    lines = spoken_lines(ROOT)
    levels = voices.get("loudness") or {}

    jobs = []
    for language, model_name in sorted(voices["models"].items()):
        if args.lang and language not in args.lang:
            continue
        strings_path = ROOT / "i18n" / f"{language}.yaml"
        if not strings_path.is_file():
            warn(f"no i18n/{language}.yaml, skipping {language}")
            continue
        model, config = find_model(model_name, dirs)
        if model is None and not args.dry_run:
            warn(f"voice model {model_name} not found, skipping {language}")
            continue
        strings = load_yaml(strings_path)
        for npc, key in lines:
            if args.only and npc != args.only:
                continue
            if key not in strings:
                warn(f"{language}: no text for {key}")
                continue
            human = ROOT / "media" / "voice" / language / f"{key}.ogg"
            if human.is_file():
                continue
            settings = profile(voices, npc, language)
            speaker = settings.get("speaker")
            target = out / "media" / "voice" / language / f"{key}.ogg"
            jobs.append((spoken_text(strings, key, voices, language), model, config, settings, speaker, target,
                         float(levels.get(language, levels.get("default", DEFAULT_LUFS)))))
    print(f"render_voices: {len(jobs)} lines")
    if args.dry_run:
        for _, _, _, settings, speaker, target, lufs in jobs:
            print(f"  {target.relative_to(out)} {settings} speaker={speaker} {lufs} LUFS")
        return
    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(render, job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except subprocess.CalledProcessError as error:
                failed += 1
                print(f"render_voices: {futures[future][5].name} failed: {error.stderr.decode(errors='replace')[-300:]}", file=sys.stderr)
    if failed:
        sys.exit(f"render_voices: {failed} lines failed")


if __name__ == "__main__":
    main()
