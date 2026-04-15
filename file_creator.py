"""
file_creator.py — Creates empty files from voice commands.
"""

import os
import re

from config import FILE_BASE_DIRECTORY


SUPPORTED_EXTENSIONS: dict[str, str] = {
    "python":      ".py",
    "py":          ".py",
    "html":        ".html",
    "webpage":     ".html",
    "java":        ".java",
    "javascript":  ".js",
    "js":          ".js",
    "text":        ".txt",
    "txt":         ".txt",
    "css":         ".css",
    "c plus plus": ".cpp",
    "cpp":         ".cpp",
}


class FileCreator:
    def __init__(self, base_directory: str = FILE_BASE_DIRECTORY):
        self.base_directory = base_directory

    def _parse(self, command: str) -> tuple[str | None, str | None]:
        """Extract (filename, extension) from a voice command."""
        command = command.lower()

        extension = None
        for key, ext in SUPPORTED_EXTENSIONS.items():
            if key in command:
                extension = ext
                break

        if not extension:
            return None, None

        match = re.search(r"(?:called|named)\s+([a-zA-Z0-9_]+)", command)
        filename = match.group(1) if match else "new_file"

        return filename, extension

    def execute(self, command: str) -> tuple[bool, str]:
        """
        Parse command and create the file.

        Returns:
            (True,  "filename created successfully.")
            (False, reason string)
        """
        filename, extension = self._parse(command)

        if not filename or not extension:
            return False, "Could not determine file type or name."

        full_path = os.path.join(self.base_directory, filename + extension)

        if os.path.exists(full_path):
            return False, f"{filename + extension} already exists."

        with open(full_path, "w") as f:
            f.write("")

        return True, f"{filename + extension} created successfully."


if __name__ == "__main__":
    creator = FileCreator()
    ok, msg = creator.execute("create a python file called hello")
    print(msg)
