"""
tts.py — Text-to-Speech with British accent (thread-safe).

Two modes:
  1. Coqui TTS  — neural British voice (best quality, requires espeak-ng)
  2. pyttsx3    — Windows SAPI British voice (fallback, no extra installs)

To use Coqui:
    pip install TTS sounddevice soundfile
    Install espeak-ng from https://github.com/espeak-ng/espeak-ng/releases

To stay on pyttsx3, set USE_COQUI = False below.
"""

import os
import tempfile
import threading
import time

# ── Toggle this to switch between engines ─────────────────────────────────────
USE_COQUI = True


class TextToSpeech:
    def __init__(self):
        self._lock = threading.Lock()

        if USE_COQUI:
            self._init_coqui()
        else:
            self._init_pyttsx3()

    # ── Coqui TTS (neural British voice) ─────────────────────────────────────

    def _init_coqui(self):
        try:
            import sounddevice as sd
            import soundfile as sf
            from TTS.api import TTS

            self._sd = sd
            self._sf = sf

            print("Loading TTS model (first run downloads ~150MB)...")
            self._coqui = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False)
            self._speaker = "p273"  # calm British male — swap if preferred
            self._engine = "coqui"
            print("TTS model ready.")

        except Exception as e:
            print(f"[TTS] Coqui failed ({e}), falling back to pyttsx3.")
            self._init_pyttsx3()

    def _speak_coqui(self, text: str):
        # tts_to_file requires a real file path — BytesIO is not supported
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()

        try:
            self._coqui.tts_to_file(
                text=text,
                speaker=self._speaker,
                file_path=tmp_path,
            )
            data, sr = self._sf.read(tmp_path, dtype="float32")
            self._sd.play(data, sr)
            self._sd.wait()
        finally:
            os.remove(tmp_path)

    # ── pyttsx3 (Windows SAPI British voice) ─────────────────────────────────

    def _init_pyttsx3(self):
        import pyttsx3
        self._pyttsx3_engine = pyttsx3.init()

        voices = self._pyttsx3_engine.getProperty("voices")
        british = None
        for v in voices:
            if "hazel" in v.name.lower() or "gb" in v.id.lower() or "en-gb" in v.id.lower():
                british = v.id
                break

        if british:
            self._pyttsx3_engine.setProperty("voice", british)
            print(f"[TTS] British voice selected: {british}")
        else:
            print("[TTS] No British voice found. Install 'Microsoft Hazel' from")
            print("      Windows Settings → Time & Language → Speech → Add voices")
            print("      Then search for English (United Kingdom).")

        self._pyttsx3_engine.setProperty("rate", 170)
        self._pyttsx3_engine.setProperty("volume", 1.0)
        self._engine = "pyttsx3"

    def _speak_pyttsx3(self, text: str):
        self._pyttsx3_engine.say(text)
        self._pyttsx3_engine.runAndWait()
        time.sleep(0.3)

    # ── Public API ────────────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Blocking speak — returns only after audio finishes."""
        with self._lock:
            if self._engine == "coqui":
                self._speak_coqui(text)
            else:
                self._speak_pyttsx3(text)


if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak("Good evening, sir. Jarvis is online and fully operational.")
