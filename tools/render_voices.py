#!/usr/bin/env python3
"""Render spoken lines for the Gilgamesh datadisk using Piper.

Usage: render_voices.py [--out OUT_DIR] [--jobs N] [--only NPC1,NPC2...]
"""
import argparse
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

import yaml

root = pathlib.Path(__file__).resolve().parent.parent


@dataclass
class VoiceConfig:
    model: str
    pitch: float = 0.0
    tempo: float = 1.0
    speaker: int | None = None


@dataclass
class NpcVoice:
    default: VoiceConfig
    languages: dict[str, VoiceConfig]  # language -> VoiceConfig


def load_voices_config() -> dict[str, NpcVoice]:
    """Load voice configuration from voice/voices.yaml."""
    path = root / "voice" / "voices.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text())
    result = {}
    for npc_id, config in data.items():
        default = VoiceConfig(
            model=config.get("model", "en_US-libritts_r-medium"),
            pitch=config.get("pitch", 0.0),
            tempo=config.get("tempo", 1.0),
            speaker=config.get("speaker"),
        )
        langs = {}
        for lang, lang_config in config.get("languages", {}).items():
            langs[lang] = VoiceConfig(
                model=lang_config.get("model", default.model),
                pitch=lang_config.get("pitch", default.pitch),
                tempo=lang_config.get("tempo", default.tempo),
                speaker=lang_config.get("speaker", default.speaker),
            )
        result[npc_id] = NpcVoice(default=default, languages=langs)
    return result


def load_dialogues() -> dict[str, list[str]]:
    """Load all dialogue text keys from dialogue files."""
    result = {}
    for path in (root / "dialogues").glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        if not data or not isinstance(data, dict):
            continue
        npc_id = data.get("id", path.stem)
        result[npc_id] = []
        # Walk through the dialogue tree
        def walk(node):
            if isinstance(node, dict):
                if "text_key" in node:
                    result[npc_id].append(node["text_key"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
        walk(data.get("nodes", data))
    return result


def load_strings(language: str) -> dict[str, str]:
    """Load all strings for a language."""
    path = root / "i18n" / f"{language}.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def render_line(text_key: str, text: str, model: str, pitch: float, tempo: float, speaker: int | None, out_dir: pathlib.Path, language: str) -> pathlib.Path:
    """Render one line with Piper and convert to OGG."""
    voice_dir = out_dir / "media" / "voice" / language
    voice_dir.mkdir(parents=True, exist_ok=True)
    out_path = voice_dir / f"{text_key}.ogg"
    
    if out_path.exists():
        return out_path
    
    # Replace {player} with placeholder for voice synthesis
    text = text.replace("{player}", "traveler")
    
    # Write text to temp file
    temp_txt = out_dir / "temp.txt"
    temp_txt.write_text(text, encoding="utf-8")
    
    # Write WAV
    temp_wav = out_dir / "temp.wav"
    
    cmd = [
        "piper",
        "--model", model,
        "--input_file", str(temp_txt),
        "--output_file", str(temp_wav),
    ]
    if pitch != 0.0:
        cmd.extend(["--pitch", str(pitch)])
    if tempo != 1.0:
        cmd.extend(["--tempo", str(tempo)])
    if speaker is not None:
        cmd.extend(["--speaker", str(speaker)])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        # Convert WAV to OGG
        subprocess.run([
            "ffmpeg", "-y", "-i", str(temp_wav),
            "-c:a", "libvorbis", "-q:a", "5",
            str(out_path),
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rendering {text_key} ({language}): {e}", file=sys.stderr)
        return None
    finally:
        temp_txt.unlink(missing_ok=True)
        temp_wav.unlink(missing_ok=True)
    
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Render spoken lines for Gilgamesh datadisk")
    parser.add_argument("--out", type=pathlib.Path, default=root / "build" / "voices", help="Output directory")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1, help="Number of parallel jobs")
    parser.add_argument("--only", type=str, help="Comma-separated list of NPC IDs to render")
    parser.add_argument("--lang", type=str, help="Only render this language")
    args = parser.parse_args()
    
    args.out.mkdir(parents=True, exist_ok=True)
    
    # Load config
    voices_config = load_voices_config()
    dialogues = load_dialogues()
    
    # Get languages from manifest
    manifest_path = root / "datadisk.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    languages = manifest.get("languages", ["en"])
    
    if args.lang:
        languages = [args.lang]
    
    only_npcs = args.only.split(",") if args.only else None
    
    # Render all lines
    futures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        for language in languages:
            strings = load_strings(language)
            for npc_id, text_keys in dialogues.items():
                if only_npcs and npc_id not in only_npcs:
                    continue
                
                # Get voice config for this NPC
                if npc_id in voices_config:
                    npc_voice = voices_config[npc_id]
                    if language in npc_voice.languages:
                        voice = npc_voice.languages[language]
                    else:
                        voice = npc_voice.default
                else:
                    voice = VoiceConfig(model="en_US-libritts_r-medium")
                
                for text_key in text_keys:
                    if text_key not in strings:
                        continue
                    text = strings[text_key]
                    
                    futures.append(executor.submit(
                        render_line,
                        text_key, text, voice.model, voice.pitch, voice.tempo, voice.speaker,
                        args.out, language
                    ))
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"Rendered: {result.relative_to(args.out)}")
    
    # Count results
    count = sum(1 for _ in (args.out / "media" / "voice").rglob("*.ogg"))
    print(f"\nTotal rendered: {count} lines")


if __name__ == "__main__":
    main()
