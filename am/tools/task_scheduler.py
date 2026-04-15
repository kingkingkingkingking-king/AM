"""
task_scheduler.py — Time-based reminder system with voice alerts.
Reminders are stored in a plain-text file (HH:MM|message per line).
"""

import re
import threading
import time
from datetime import datetime

from am.audio.tts import TextToSpeech
from am.core.config import SCHEDULE_FILE, SCHEDULE_CHECK_INTERVAL


class TaskScheduler:
    def __init__(self):
        self.tts = TextToSpeech()
        self.running = False
        self._triggered_today: set[str] = set()
        self._last_date: str = datetime.now().strftime("%Y-%m-%d")

    # ── Reminder file I/O ─────────────────────────────────────────────────────

    def add_reminder(self, time_str: str, message: str) -> str:
        """
        Adds a reminder.  time_str must be HH:MM (24-hour).
        Returns a confirmation string.
        """
        if not re.match(r"^\d{2}:\d{2}$", time_str):
            return f"Invalid time format: '{time_str}'. Use HH:MM."

        with open(SCHEDULE_FILE, "a") as f:
            f.write(f"{time_str}|{message}\n")
        return f"Reminder set for {time_str}."

    def _load_reminders(self) -> list[tuple[str, str]]:
        reminders = []
        try:
            with open(SCHEDULE_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if "|" in line:
                        time_part, message = line.split("|", 1)
                        reminders.append((time_part, message))
        except FileNotFoundError:
            pass
        return reminders

    # ── Monitor loop ──────────────────────────────────────────────────────────

    def _loop(self) -> None:
        while self.running:
            now_time = datetime.now().strftime("%H:%M")
            today    = datetime.now().strftime("%Y-%m-%d")

            # Reset triggered set at midnight
            if today != self._last_date:
                self._triggered_today.clear()
                self._last_date = today

            for time_part, message in self._load_reminders():
                key = f"{time_part}|{message}"
                if now_time == time_part and key not in self._triggered_today:
                    print(f"[Reminder] {message}")
                    self.tts.speak(f"Reminder: {message}")
                    self._triggered_today.add(key)

            time.sleep(SCHEDULE_CHECK_INTERVAL)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        self.running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def stop(self) -> None:
        self.running = False
