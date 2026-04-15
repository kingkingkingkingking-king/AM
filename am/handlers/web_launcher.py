"""
web_launcher.py — Opens websites based on keywords in a voice command.
"""

import webbrowser
from am.core.config import COMMON_SITES


def open_website(command: str) -> tuple[bool, str]:
    """
    Scans command for a known site keyword and opens it.

    Returns:
        (True,  "Opening <site>.") on success
        (False, "")                if no match
    """
    command = command.lower()
    for keyword, url in COMMON_SITES.items():
        if keyword in command:
            webbrowser.open(url)
            return True, f"Opening {keyword}."
    return False, ""


if __name__ == "__main__":
    success, msg = open_website("open spotify")
    print(msg if success else "No matching website found.")
