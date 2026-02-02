#!/usr/bin/env python3
"""Select a deterministic daily alarm song from a playlist."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class DailySongPicker:
    songs: List[str]

    def pick_for_date(self, target_date: date) -> str:
        if not self.songs:
            raise ValueError("Song list must not be empty.")

        seed = target_date.isoformat()
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        index = int(digest, 16) % len(self.songs)
        return self.songs[index]


def load_songs_from_file(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Song list file not found: {path}")

    songs = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    songs = [song for song in songs if song]
    if not songs:
        raise ValueError("Song list file is empty.")
    return songs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pick a deterministic daily alarm song from a playlist.",
    )
    parser.add_argument(
        "songs",
        nargs="*",
        help="Song names or file paths. If omitted, --file is required.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to a text file with one song per line.",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Target date in YYYY-MM-DD format. Defaults to today.",
    )
    return parser


def parse_date(date_str: str | None) -> date:
    if not date_str:
        return date.today()
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format.") from exc


def resolve_songs(cli_songs: Iterable[str], file_path: Path | None) -> List[str]:
    songs = list(cli_songs)
    if songs:
        return songs
    if file_path:
        return load_songs_from_file(file_path)
    raise ValueError("Provide songs via arguments or --file.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    songs = resolve_songs(args.songs, args.file)
    target_date = parse_date(args.date)

    picker = DailySongPicker(songs)
    selection = picker.pick_for_date(target_date)
    print(selection)


if __name__ == "__main__":
    main()
