"""
Dataset Preparation Tools (Offline)
- Audio slicing (WAV, 16kHz, mono)
- Silence trimming
- Text-audio pairing
- Metadata generation (CSV/JSON)
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List, Tuple

from pydub import AudioSegment, silence


def load_audio(path: Path) -> AudioSegment:
    return AudioSegment.from_file(path)


def ensure_16k_mono(audio: AudioSegment) -> AudioSegment:
    return audio.set_frame_rate(16000).set_channels(1)


def trim_silence(audio: AudioSegment, silence_thresh: int = -40, min_silence_len: int = 300) -> AudioSegment:
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=80
    )
    if not chunks:
        return audio
    combined = chunks[0]
    for chunk in chunks[1:]:
        combined += chunk
    return combined


def slice_audio(audio: AudioSegment, segment_ms: int) -> List[AudioSegment]:
    segments = []
    for start in range(0, len(audio), segment_ms):
        segments.append(audio[start:start + segment_ms])
    return segments


def pair_audio_text(audio_dir: Path, text_dir: Path) -> List[Tuple[Path, str]]:
    pairs: List[Tuple[Path, str]] = []
    for wav_path in sorted(audio_dir.glob("*.wav")):
        text_path = text_dir / f"{wav_path.stem}.txt"
        if text_path.exists():
            text = text_path.read_text(encoding="utf-8").strip()
            if text:
                pairs.append((wav_path, text))
    return pairs


def write_metadata_csv(pairs: List[Tuple[Path, str]], out_csv: Path) -> None:
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="|")
        for wav_path, text in pairs:
            writer.writerow([wav_path.name, text])


def write_metadata_json(pairs: List[Tuple[Path, str]], out_json: Path) -> None:
    data = [{"file": p.name, "text": t} for p, t in pairs]
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def process_directory(
    input_dir: Path,
    output_dir: Path,
    text_dir: Path | None,
    trim: bool,
    slice_ms: int | None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for wav_path in sorted(input_dir.glob("*.wav")):
        audio = load_audio(wav_path)
        audio = ensure_16k_mono(audio)
        if trim:
            audio = trim_silence(audio)

        if slice_ms:
            segments = slice_audio(audio, slice_ms)
            for idx, segment in enumerate(segments, start=1):
                out_path = output_dir / f"{wav_path.stem}_{idx:04d}.wav"
                segment.export(out_path, format="wav")
        else:
            out_path = output_dir / wav_path.name
            audio.export(out_path, format="wav")

    if text_dir and text_dir.exists():
        pairs = pair_audio_text(output_dir, text_dir)
        if pairs:
            write_metadata_csv(pairs, output_dir / "metadata.csv")
            write_metadata_json(pairs, output_dir / "metadata.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline dataset preparation tools")
    parser.add_argument("--input", required=True, type=Path, help="Input WAV directory")
    parser.add_argument("--output", required=True, type=Path, help="Output WAV directory")
    parser.add_argument("--text", type=Path, help="Directory with matching .txt transcripts")
    parser.add_argument("--trim", action="store_true", help="Trim leading/trailing silence")
    parser.add_argument("--slice-ms", type=int, help="Slice audio into fixed-length segments")
    args = parser.parse_args()

    process_directory(args.input, args.output, args.text, args.trim, args.slice_ms)


if __name__ == "__main__":
    main()
