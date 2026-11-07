#!/usr/bin/env python3
"""Минимальный пример Fish Audio TTS.

Нужен API-ключ: https://fish.audio/app/api-keys
Задайте его в FISH_API_KEY или в файле .env рядом со скриптом.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # optional
    def load_dotenv() -> bool:
        return False

from fishaudio import FishAudio
from fishaudio.utils import save


def main() -> int:
    load_dotenv()
    if not os.getenv("FISH_API_KEY"):
        print(
            "FISH_API_KEY не задан.\n"
            "1) Создайте ключ: https://fish.audio/app/api-keys\n"
            "2) export FISH_API_KEY=...\n"
            "   или скопируйте .env.example → .env",
            file=sys.stderr,
        )
        return 1

    text = " ".join(sys.argv[1:]) or "Привет! Это голос Fish Audio."
    out = Path("output.mp3")

    client = FishAudio()  # читает FISH_API_KEY
    audio = client.tts.convert(text=text, model="s2.1-pro-free")
    save(audio, str(out))
    print(f"Сохранено: {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
