"""
llm_brain.py — Local LLM interface via llama-cpp-python.
"""

import os
from typing import Generator

from am.core.config import (
    LLM_MODEL_PATH,
    LLM_N_CTX,
    LLM_N_THREADS,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_SYSTEM_PROMPT,
    CHAT_HISTORY_FILE,
    CHAT_HISTORY_MAX_LINES,
)


class LLMBrain:
    def __init__(self):
        if not os.path.exists(LLM_MODEL_PATH):
            raise FileNotFoundError(
                f"LLM model not found at: {LLM_MODEL_PATH}\n"
                "Update LLM_MODEL_PATH in config.py."
            )

        from llama_cpp import Llama  # imported here so the app can start without it

        self.model = Llama(
            model_path=LLM_MODEL_PATH,
            n_ctx=LLM_N_CTX,
            n_threads=LLM_N_THREADS,
            verbose=False,
        )

        self.history_file = CHAT_HISTORY_FILE
        self.max_history_lines = CHAT_HISTORY_MAX_LINES

        if not os.path.exists(self.history_file):
            open(self.history_file, "w").close()

    # ── History helpers ───────────────────────────────────────────────────────

    def _load_history(self) -> str:
        with open(self.history_file, "r") as f:
            lines = f.readlines()
        return "".join(lines[-self.max_history_lines:])

    def save_to_history(self, user_input: str, response: str) -> None:
        with open(self.history_file, "a") as f:
            f.write(f"User: {user_input}\n")
            f.write(f"Jarvis: {response}\n")

    def _build_messages(self, user_input: str) -> list[dict]:
        history = self._load_history()
        return [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user",   "content": f"{history}\nUser: {user_input}"},
        ]

    # ── Generation ────────────────────────────────────────────────────────────

    def generate(self, user_input: str, memory_context: str = "") -> str:
        """Blocking generation — returns complete response string."""
        result = self.model.create_chat_completion(
            messages=self._build_messages(user_input, memory_context),
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            stream=False,
        )
        content: str = result["choices"][0]["message"]["content"]
        self.save_to_history(user_input, content)
        return content

    def stream_generate(self, user_input: str, memory_context: str = "") -> Generator[str, None, None]:
        """
        Streaming generation — yields tokens one by one.
        Caller is responsible for saving history via save_to_history().
        """
        stream = self.model.create_chat_completion(
            messages=self._build_messages(user_input, memory_context),
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            stream=True,
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
