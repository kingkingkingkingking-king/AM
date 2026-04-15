"""
app_launcher.py — Launches desktop applications via subprocess or pyautogui.
"""

import subprocess
import time
import pyautogui

from am.core.config import COMMON_APPS


def open_desktop_app(command: str) -> tuple[bool, str]:
    """
    Detects an app keyword in command and launches it.

    Returns:
        (True,  "Opening <app>.") on success
        (False, "")               if no match or launch failed
    """
    command = command.lower()

    for keyword, app_name in COMMON_APPS.items():
        if keyword in command:
            try:
                subprocess.Popen(app_name)
                return True, f"Opening {keyword}."
            except FileNotFoundError:
                # Fallback: use Windows Start menu simulation
                try:
                    pyautogui.press("win")
                    time.sleep(0.5)
                    pyautogui.write(app_name, interval=0.05)
                    time.sleep(0.3)
                    pyautogui.press("enter")
                    return True, f"Opening {keyword}."
                except Exception:
                    return False, f"Failed to open {keyword}."
            except Exception:
                return False, f"Failed to open {keyword}."

    return False, ""


if __name__ == "__main__":
    success, msg = open_desktop_app("open notepad")
    print(msg if success else "No matching app found.")
