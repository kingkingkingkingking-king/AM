"""
browser_automation.py — Controls the active browser window via keyboard shortcuts.
"""

import time
import pyautogui


class BrowserAutomation:
    def __init__(self, typing_interval: float = 0.05):
        self.typing_interval = typing_interval

    # ── Actions ───────────────────────────────────────────────────────────────

    def new_tab(self) -> str:
        pyautogui.hotkey("ctrl", "t")
        return "New tab opened."

    def close_tab(self) -> str:
        pyautogui.hotkey("ctrl", "w")
        return "Tab closed."

    def zoom_in(self) -> str:
        pyautogui.hotkey("ctrl", "+")
        return "Zoomed in."

    def zoom_out(self) -> str:
        pyautogui.hotkey("ctrl", "-")
        return "Zoomed out."

    def go_back(self) -> str:
        pyautogui.hotkey("alt", "left")
        return "Going back."

    def go_forward(self) -> str:
        pyautogui.hotkey("alt", "right")
        return "Going forward."

    def google_search(self, query: str) -> str:
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.3)
        pyautogui.write(query, interval=self.typing_interval)
        time.sleep(0.2)
        pyautogui.press("enter")
        return f"Searching Google for {query}."

    # ── Dispatcher ────────────────────────────────────────────────────────────

    def execute(self, command: str) -> tuple[bool, str]:
        """
        Matches a browser command and executes it.

        Returns:
            (True,  response message) on match
            (False, "")               if no browser command matched
        """
        cmd = command.lower()

        if "new tab" in cmd:
            return True, self.new_tab()
        if "close tab" in cmd:
            return True, self.close_tab()
        if "zoom in" in cmd:
            return True, self.zoom_in()
        if "zoom out" in cmd:
            return True, self.zoom_out()
        if "go back" in cmd:
            return True, self.go_back()
        if "go forward" in cmd:
            return True, self.go_forward()
        if "search for" in cmd:
            query = cmd.split("search for", 1)[1].strip()
            if query:
                return True, self.google_search(query)

        return False, ""


if __name__ == "__main__":
    time.sleep(2)
    browser = BrowserAutomation()
    success, msg = browser.execute("new tab")
    print(msg)
