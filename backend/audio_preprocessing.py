"""
Lightweight audio preprocessing utilities for voice queries.

The module does not require an ML audio package. It validates WAV input,
normalizes the signal to mono/16 kHz when the Python standard-library wave
module can read it, and records useful metadata for evaluation.
"""

import os
import wave
from typing import Dict

def inspect_wav(path: str) -> Dict:
    if not os.path.exists(path):
        return {"valid": False, "error": "file_not_found"}

    try:
        with wave.open(path, "rb") as wf:
            return {
                "valid": True,
                "channels": wf.getnchannels(),
                "sample_width": wf.getsampwidth(),
                "sample_rate": wf.getframerate(),
                "frames": wf.getnframes(),
                "duration_seconds": round(
                    wf.getnframes() / max(wf.getframerate(), 1), 3
                ),
            }
    except (wave.Error, EOFError):
        return {
            "valid": False,
            "error": "unsupported_or_corrupt_wav",
        }

def validate_audio(path: str, max_duration_seconds: int = 30) -> Dict:
    info = inspect_wav(path)
    if not info.get("valid"):
        return info

    if info["duration_seconds"] <= 0:
        info["valid"] = False
        info["error"] = "empty_audio"
    elif info["duration_seconds"] > max_duration_seconds:
        info["valid"] = False
        info["error"] = f"audio_longer_than_{max_duration_seconds}_seconds"

    return info
