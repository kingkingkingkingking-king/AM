"""
battery_monitor.py — Monitors battery level and fires desktop + voice alerts.
Uses plyer for cross-platform notifications (works on Windows, macOS, Linux).
"""

import threading
import time
import psutil
from plyer import notification

from tts import TextToSpeech
from config import (
    BATTERY_CHECK_INTERVAL,
    BATTERY_LOW_THRESHOLD,
    BATTERY_FULL_THRESHOLD,
)


class BatteryMonitor:
    def __init__(self):
        self.tts = TextToSpeech()
        self.running = False
        self._thread: threading.Thread | None = None

        # Track whether we've already fired each alert this cycle
        self._alerted_full = False
        self._alerted_low  = False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _notify(self, title: str, message: str) -> None:
        """Show a desktop notification (non-blocking)."""
        try:
            notification.notify(title=title, message=message, timeout=5)
        except Exception:
            pass  # Notification not critical; don't crash the monitor

    def _check(self) -> None:
        battery = psutil.sensors_battery()
        if battery is None:
            return

        percent = battery.percent
        plugged = battery.power_plugged

        # ── Fully charged ─────────────────────────────────────────────────────
        if percent >= BATTERY_FULL_THRESHOLD and plugged and not self._alerted_full:
            self._notify("Battery Full", "Battery is fully charged (100%).")
            self.tts.speak("Battery is fully charged.")
            self._alerted_full = True

        # ── Low battery ───────────────────────────────────────────────────────
        if percent <= BATTERY_LOW_THRESHOLD and not plugged and not self._alerted_low:
            self._notify("Low Battery", f"Battery is below {BATTERY_LOW_THRESHOLD}%.")
            self.tts.speak(f"Warning. Battery is below {BATTERY_LOW_THRESHOLD} percent.")
            self._alerted_low = True

        # ── Reset alert flags when conditions clear ───────────────────────────
        if percent < BATTERY_FULL_THRESHOLD:
            self._alerted_full = False
        if percent > BATTERY_LOW_THRESHOLD:
            self._alerted_low = False

    def _loop(self) -> None:
        while self.running:
            self._check()
            time.sleep(BATTERY_CHECK_INTERVAL)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.running = False


if __name__ == "__main__":
    monitor = BatteryMonitor()
    monitor.start()
    print("Battery monitor running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
