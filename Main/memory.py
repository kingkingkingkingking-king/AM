"""
memory.py — AM's persistent memory system.

Stores facts the user tells AM and retrieves them on demand.
Memory is saved to a JSON file so it persists across sessions.

Voice commands:
    "hey AM, remember that my meeting is on Friday"
    "hey AM, remember my girlfriend's name is Sarah"
    "hey AM, what do you remember about my meeting"
    "hey AM, what do you know about me"
    "hey AM, forget my meeting"
    "hey AM, forget everything"
"""

import json
import os
import re
from datetime import datetime

from config import MEMORY_FILE


class Memory:
    def __init__(self):
        self.file = MEMORY_FILE
        self._data: dict = self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self) -> None:
        with open(self.file, "w") as f:
            json.dump(self._data, f, indent=2)

    # ── Core operations ───────────────────────────────────────────────────────

    def remember(self, key: str, value: str) -> str:
        """Store a fact. Key is a short label, value is what to remember."""
        key = key.strip().lower()
        self._data[key] = {
            "value":     value.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self._save()
        return f"Noted, sir. AM will remember that {value}."

    def recall(self, query: str) -> str:
        """
        Search memory for entries matching the query.
        Returns a spoken summary of matches.
        """
        query = query.strip().lower()

        # Exact key match first
        if query in self._data:
            entry = self._data[query]
            return f"AM recalls: {entry['value']}, sir."

        # Partial match across keys and values
        matches = []
        for key, entry in self._data.items():
            if query in key or query in entry["value"].lower():
                matches.append(entry["value"])

        if not matches:
            return f"AM has nothing on record regarding {query}, sir."

        if len(matches) == 1:
            return f"AM recalls: {matches[0]}, sir."

        # Multiple matches — join naturally
        joined = ". ".join(matches)
        return f"AM recalls the following, sir: {joined}."

    def recall_all(self) -> str:
        """Return everything AM remembers, spoken naturally."""
        if not self._data:
            return "AM's memory is currently empty, sir."

        entries = [entry["value"] for entry in self._data.values()]

        if len(entries) == 1:
            return f"AM remembers one thing, sir: {entries[0]}."

        joined = ". ".join(entries)
        return f"AM currently remembers the following, sir: {joined}."

    def forget(self, key: str) -> str:
        """Delete a specific memory entry by key."""
        key = key.strip().lower()

        # Try exact match
        if key in self._data:
            del self._data[key]
            self._save()
            return f"Done, sir. AM has forgotten {key}."

        # Try partial match
        matched_keys = [k for k in self._data if key in k]
        if matched_keys:
            for k in matched_keys:
                del self._data[k]
            self._save()
            return f"Forgotten, sir."

        return f"AM has no memory of {key}, sir."

    def forget_all(self) -> str:
        """Wipe all memory."""
        self._data = {}
        self._save()
        return "All memory wiped, sir. AM starts fresh."

    def count(self) -> int:
        return len(self._data)

    # ── Command parser ────────────────────────────────────────────────────────

    def parse_and_execute(self, command: str) -> tuple[bool, str]:
        """
        Parse a memory-related voice command and execute it.

        Supported patterns:
            remember that <fact>
            remember <key> is <value>
            remember my <key> is <value>
            what do you remember about <query>
            what do you know about <query>
            what do you remember            (recall all)
            forget <key>
            forget everything / forget all
        """
        cmd = command.lower().strip()

        # ── FORGET ALL ────────────────────────────────────────────────────────
        if re.search(r"forget (everything|all)", cmd):
            return True, self.forget_all()

        # ── FORGET specific ───────────────────────────────────────────────────
        forget_match = re.search(r"forget (.+)", cmd)
        if forget_match:
            key = forget_match.group(1).strip()
            return True, self.forget(key)

        # ── RECALL ALL ────────────────────────────────────────────────────────
        if re.search(r"what do you (remember|know)$", cmd) or \
           re.search(r"what (do you remember|have you remembered|do you know about me)$", cmd) or \
           "what do you remember" == cmd or "what do you know" == cmd:
            return True, self.recall_all()

        # ── RECALL specific ───────────────────────────────────────────────────
        recall_match = re.search(
            r"what (do you )?(remember|know) about (.+)", cmd
        )
        if recall_match:
            query = recall_match.group(3).strip()
            return True, self.recall(query)

        # ── REMEMBER: "remember that <fact>" ─────────────────────────────────
        that_match = re.search(r"remember that (.+)", cmd)
        if that_match:
            fact  = that_match.group(1).strip()
            # Use first 3 words as key
            key   = " ".join(fact.split()[:3])
            return True, self.remember(key, fact)

        # ── REMEMBER: "remember <key> is <value>" ────────────────────────────
        is_match = re.search(r"remember (?:my |the )?(.+?) is (.+)", cmd)
        if is_match:
            key   = is_match.group(1).strip()
            value = f"{key} is {is_match.group(2).strip()}"
            return True, self.remember(key, value)

        # ── REMEMBER: "remember <key> <value>" (fallback) ────────────────────
        rem_match = re.search(r"remember (.+)", cmd)
        if rem_match:
            fact = rem_match.group(1).strip()
            key  = " ".join(fact.split()[:3])
            return True, self.remember(key, fact)

        return False, "AM could not parse that memory command, sir."


if __name__ == "__main__":
    m = Memory()

    # Quick test
    print(m.remember("meeting", "the team meeting is on Friday at 3pm"))
    print(m.remember("girlfriend name", "girlfriend's name is Sarah"))
    print(m.recall("meeting"))
    print(m.recall_all())
    print(m.forget("meeting"))
    print(m.forget("girlfriend name"))
    print(m.recall_all())
