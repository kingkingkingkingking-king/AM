"""
automation_brain.py — Routes voice commands to the correct automation handler.

Design principle: classify_intent() only inspects the command string.
                  execute() is the only method that performs side effects.
"""

import os
import re
import subprocess
import pyautogui
from datetime import datetime

from web_launcher import open_website
from app_launcher import open_desktop_app
from browser_automation import BrowserAutomation
from file_creator import FileCreator
from hardware_monitor import HardwareMonitor
from speed_test_tool import SpeedTestTool
from task_scheduler import TaskScheduler
from memory import Memory


class AutomationBrain:
    def __init__(self, scheduler: TaskScheduler):
        self.file_creator = FileCreator()
        self.hardware     = HardwareMonitor()
        self.browser      = BrowserAutomation()
        self.scheduler    = scheduler
        self.memory       = Memory()

    # ── Intent classification (NO side effects) ───────────────────────────────

    def classify_intent(self, command: str) -> str | None:
        """
        Returns one of:
            "website" | "app" | "browser" | "hardware" | "file" |
            "speed_test" | "reminder" | "time" | "date" |
            "screenshot" | "lock" | "memory" | None
        """
        cmd = command.lower()

        # Memory — check before hardware to avoid "remember my storage" clash
        memory_triggers = (
            "remember", "don't forget", "recall",
            "what do you know", "what do you remember",
            "forget",
        )
        if any(t in cmd for t in memory_triggers):
            return "memory"

        if any(k in cmd for k in ("ram", "memory", "storage", "disk")):
            return "hardware"

        if "speed test" in cmd or "internet speed" in cmd:
            return "speed_test"

        if "create" in cmd and "file" in cmd:
            return "file"

        if "remind" in cmd or "set reminder" in cmd:
            return "reminder"

        if "screenshot" in cmd or "screen shot" in cmd or "capture screen" in cmd:
            return "screenshot"

        if "lock" in cmd and ("computer" in cmd or "screen" in cmd or "pc" in cmd):
            return "lock"

        if any(k in cmd for k in ("what time", "current time", "what's the time", "tell me the time")):
            return "time"

        if any(k in cmd for k in ("what day", "what date", "current date", "today's date", "what's the date")):
            return "date"

        # Browser commands take priority over generic "open"
        browser_keywords = (
            "new tab", "close tab", "zoom in", "zoom out",
            "go back", "go forward", "search for",
        )
        if any(k in cmd for k in browser_keywords):
            return "browser"

        # Website vs desktop app
        open_triggers = ("open", "go to", "launch", "start")
        if any(t in cmd for t in open_triggers):
            from config import COMMON_SITES, COMMON_APPS
            if any(site in cmd for site in COMMON_SITES):
                return "website"
            if any(app in cmd for app in COMMON_APPS):
                return "app"

        return None

    # ── Execution (side effects happen here only) ─────────────────────────────

    def execute(self, command: str) -> dict:
        intent = self.classify_intent(command)

        if intent == "memory":
            ok, msg = self.memory.parse_and_execute(command)
            return {"success": ok, "type": "memory", "message": msg}

        if intent == "hardware":
            return {"success": True, "type": "hardware",
                    "message": self.hardware.report()}

        if intent == "speed_test":
            speed = SpeedTestTool().run_test()
            return {"success": True, "type": "speed_test",
                    "message": f"Your current internet speed is {speed}."}

        if intent == "file":
            ok, msg = self.file_creator.execute(command)
            return {"success": ok, "type": "file", "message": msg}

        if intent == "reminder":
            ok, msg = self._handle_reminder(command)
            return {"success": ok, "type": "reminder", "message": msg}

        if intent == "screenshot":
            ok, msg = self._take_screenshot()
            return {"success": ok, "type": "screenshot", "message": msg}

        if intent == "lock":
            ok, msg = self._lock_computer()
            return {"success": ok, "type": "lock", "message": msg}

        if intent == "time":
            return {"success": True, "type": "time",
                    "message": self._get_time()}

        if intent == "date":
            return {"success": True, "type": "date",
                    "message": self._get_date()}

        if intent == "browser":
            ok, msg = self.browser.execute(command)
            return {"success": ok, "type": "browser", "message": msg}

        if intent == "website":
            ok, msg = open_website(command)
            return {"success": ok, "type": "website", "message": msg}

        if intent == "app":
            ok, msg = open_desktop_app(command)
            return {"success": ok, "type": "app", "message": msg}

        return {"success": False, "type": None, "message": ""}

    # ── Time & Date ───────────────────────────────────────────────────────────

    def _get_time(self) -> str:
        now    = datetime.now()
        hour   = now.strftime("%I").lstrip("0")
        minute = now.strftime("%M")
        period = now.strftime("%p")
        if minute == "00":
            return f"It is {hour} o'clock {period}, sir."
        return f"It is {hour} {minute} {period}, sir."

    def _get_date(self) -> str:
        now      = datetime.now()
        day_name = now.strftime("%A")
        month    = now.strftime("%B")
        day      = now.strftime("%d").lstrip("0")
        year     = now.strftime("%Y")
        suffix   = (
            "th" if 11 <= int(day) <= 13
            else {1: "st", 2: "nd", 3: "rd"}.get(int(day) % 10, "th")
        )
        return f"Today is {day_name}, {month} the {day}{suffix}, {year}, sir."

    # ── Screenshot ────────────────────────────────────────────────────────────

    def _take_screenshot(self) -> tuple[bool, str]:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_path = os.path.join(
                os.path.expanduser("~"), "Pictures", f"screenshot_{timestamp}.png"
            )
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            pyautogui.screenshot(save_path)
            return True, "Screenshot saved to Pictures folder, sir."
        except Exception as e:
            return False, f"Screenshot failed, sir. {e}"

    # ── Lock computer ─────────────────────────────────────────────────────────

    def _lock_computer(self) -> tuple[bool, str]:
        try:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return True, "Locking the computer, sir."
        except Exception as e:
            return False, f"Could not lock the computer, sir. {e}"

    # ── Reminder parsing ──────────────────────────────────────────────────────

    def _handle_reminder(self, command: str) -> tuple[bool, str]:
        time_match = re.search(r"\b(\d{1,2}:\d{2})\b", command)
        if not time_match:
            return False, "Please include a time like 14:30 in your reminder, sir."

        time_str  = time_match.group(1).zfill(5)
        msg_match = re.search(r"\b(?:to|for)\s+(.+)", command, re.IGNORECASE)
        message   = msg_match.group(1).strip() if msg_match else "Reminder"

        confirmation = self.scheduler.add_reminder(time_str, message)
        return True, confirmation


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from task_scheduler import TaskScheduler

    sched = TaskScheduler()
    brain = AutomationBrain(scheduler=sched)

    while True:
        cmd = input("Command: ").strip()
        if not cmd:
            continue
        result = brain.execute(cmd)
        print(result)
