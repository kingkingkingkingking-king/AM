"""
stt.py — Speech-to-Text using Google Speech Recognition.
"""

import speech_recognition as sr

from config import (
    STT_ENERGY_THRESHOLD,
    STT_PAUSE_THRESHOLD,
    STT_LISTEN_TIMEOUT,
    STT_PHRASE_TIME_LIMIT,
    WAKE_WORD,
)


class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = STT_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = STT_PAUSE_THRESHOLD
        self._calibrate()

    def _calibrate(self) -> None:
        print("Calibrating microphone...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone ready.")

    def listen(self) -> dict:
        """
        Listens for a single utterance and returns a result dict:
            {"success": bool, "text": str | None, "error": str | None}
        """
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=STT_LISTEN_TIMEOUT,
                    phrase_time_limit=STT_PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                return {"success": False, "text": None, "error": "Listening timed out."}

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio).lower()
            return {"success": True, "text": text, "error": None}

        except sr.UnknownValueError:
            return {"success": False, "text": None, "error": "Could not understand audio."}

        except sr.RequestError as e:
            return {"success": False, "text": None, "error": f"API request failed: {e}"}

    def listen_for_wake_word(self) -> dict:
        """
        Keeps listening until the wake word is detected, then returns
        the full utterance (so the command can follow in the same phrase).
        If WAKE_WORD is None in config, behaves identically to listen().
        """
        if WAKE_WORD is None:
            return self.listen()

        while True:
            result = self.listen()
            if result["success"] and WAKE_WORD in result["text"]:
                # Strip the wake word itself before returning
                command = result["text"].replace(WAKE_WORD, "").strip()
                return {"success": True, "text": command, "error": None}


if __name__ == "__main__":
    stt = SpeechToText()
    result = stt.listen()
    if result["success"]:
        print("You said:", result["text"])
    else:
        print("Error:", result["error"])
