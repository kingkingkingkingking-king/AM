"""
sounds.py — Generates and plays AM's audio cues using numpy + sounddevice.
No external audio files needed — all sounds are synthesized on the fly.
"""

import numpy as np
import sounddevice as sd


def _play(wave: np.ndarray, sample_rate: int = 22050) -> None:
    """Play a numpy audio array and block until done."""
    sd.play(wave.astype(np.float32), samplerate=sample_rate)
    sd.wait()


def _tone(freq: float, duration: float, volume: float = 0.4,
          sample_rate: int = 22050, fade: float = 0.01) -> np.ndarray:
    """Generate a pure sine tone with a short fade in/out to avoid clicks."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = volume * np.sin(2 * np.pi * freq * t)

    # Fade in and out
    fade_samples = int(sample_rate * fade)
    wave[:fade_samples]  *= np.linspace(0, 1, fade_samples)
    wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    return wave


def play_boot() -> None:
    """
    Rising multi-tone boot sequence — played once on startup before greeting.
    Sounds like a system initialising.
    """
    sr = 22050
    sequence = [
        _tone(220,  0.12, volume=0.25, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(330,  0.12, volume=0.30, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(440,  0.12, volume=0.35, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(660,  0.18, volume=0.40, sample_rate=sr),
        np.zeros(int(sr * 0.06)),
        _tone(880,  0.30, volume=0.45, sample_rate=sr),
    ]
    _play(np.concatenate(sequence), sr)


def play_wake() -> None:
    """
    Short double-beep played when the wake word is detected.
    Confirms AM heard you without being intrusive.
    """
    sr = 22050
    beep = _tone(880, 0.07, volume=0.35, sample_rate=sr)
    gap  = np.zeros(int(sr * 0.05))
    _play(np.concatenate([beep, gap, beep]), sr)


def play_thinking() -> None:
    """
    Subtle low pulse played while the LLM is generating.
    Single soft tone so the user knows AM is processing.
    """
    _play(_tone(330, 0.15, volume=0.20))


def play_shutdown() -> None:
    """
    Descending tone sequence — played just before AM goes offline.
    Mirror image of the boot sound.
    """
    sr = 22050
    sequence = [
        _tone(880,  0.12, volume=0.40, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(660,  0.12, volume=0.35, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(440,  0.12, volume=0.30, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(330,  0.12, volume=0.25, sample_rate=sr),
        np.zeros(int(sr * 0.04)),
        _tone(220,  0.30, volume=0.20, sample_rate=sr),
    ]
    _play(np.concatenate(sequence), sr)


if __name__ == "__main__":
    print("Boot sound:");    play_boot()
    print("Wake sound:");    play_wake()
    print("Thinking sound:"); play_thinking()
    print("Shutdown sound:"); play_shutdown()
