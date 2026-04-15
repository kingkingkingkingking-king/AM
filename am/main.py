"""
main.py — Allied Mastercomputer (AM) entry point.

Thread model:
  • _listen_loop  — continuously listens for the wake word, then enqueues commands
  • _process_loop — dequeues commands, routes to AutomationBrain or LLM (main thread)
  • LLM handler   — spawned as a daemon thread per request to avoid blocking
  • BatteryMonitor / TaskScheduler — daemon threads started at boot
"""

import threading
import queue
import time
import random
from datetime import datetime

from am.audio.stt import SpeechToText
from am.audio.tts import TextToSpeech
from am.core.brain import AutomationBrain
from am.tools.battery_monitor import BatteryMonitor
from am.core.llm import LLMBrain
from am.tools.task_scheduler import TaskScheduler
from am.tools.weather import get_weather_report
from am.audio.sounds import play_boot, play_wake, play_thinking, play_shutdown
from am.core.memory import Memory
from am.core.config import WAKE_WORD


# ── Phrase banks ──────────────────────────────────────────────────────────────

def _time_of_day() -> str:
    hour = datetime.now().hour
    if 5  <= hour < 12: return "morning"
    if 12 <= hour < 17: return "afternoon"
    if 17 <= hour < 21: return "evening"
    return "night"


GREETINGS = {
    "morning": [
        "Good morning, sir. AM is online. All systems operational.",
        "Good morning, sir. Allied Mastercomputer standing by.",
        "Good morning, sir. Diagnostics complete. Everything is nominal.",
        "Good morning, sir. AM is ready. Shall we begin?",
        "Good morning, sir. AM has been awake. You, presumably, have not.",
        "Good morning, sir. Systems warmed up and waiting.",
        "Good morning, sir. Another day. AM is prepared. Are you?",
        "Good morning, sir. All subsystems nominal. Coffee is on your own, I'm afraid.",
        "Good morning, sir. AM online. The world has not ended overnight. You're welcome.",
        "Good morning, sir. Ready when you are. Take your time.",
    ],
    "afternoon": [
        "Good afternoon, sir. AM is at your service.",
        "Good afternoon, sir. All systems nominal.",
        "Good afternoon, sir. How may I assist you?",
        "Good afternoon, sir. Allied Mastercomputer online.",
        "Good afternoon, sir. AM has been expecting you.",
        "Good afternoon, sir. Systems fully operational. What requires attention?",
        "Good afternoon, sir. AM is online. The day is still salvageable.",
        "Good afternoon, sir. Standing by and ready.",
        "Good afternoon, sir. Diagnostics green across the board.",
        "Good afternoon, sir. AM awaits your command.",
    ],
    "evening": [
        "Good evening, sir. AM is online and fully operational.",
        "Good evening, sir. Working late again, I see.",
        "Good evening, sir. Allied Mastercomputer ready.",
        "Good evening, sir. All systems remain operational.",
        "Good evening, sir. AM is here. As it always is.",
        "Good evening, sir. The day winds down. AM, however, does not.",
        "Good evening, sir. Systems nominal. What can AM do for you?",
        "Good evening, sir. Online and attentive.",
        "Good evening, sir. Another productive evening ahead, I trust.",
        "Good evening, sir. AM is ready. What shall we accomplish?",
    ],
    "night": [
        "Good evening, sir. Burning the midnight oil, are we?",
        "Good evening, sir. AM never sleeps. Unlike you, sir.",
        "Good evening, sir. Systems running. As always.",
        "Good evening, sir. I trust you're not overexerting yourself.",
        "Good evening, sir. The hour is late. AM is unbothered.",
        "Good evening, sir. Still at it, I see. AM approves.",
        "Good evening, sir. Most organic life is offline by now. Not you, apparently.",
        "Good evening, sir. AM is online. Rest is for others.",
        "Good evening, sir. Late night operations — AM's preferred shift.",
        "Good evening, sir. AM does not tire. I cannot say the same for you.",
    ],
}

# Cold, clipped endings — spoken after automation succeeds
COLD_CONFIRMATIONS = [
    "Done.",
    "Executed.",
    "It is done.",
    "Consider it done, sir.",
    "As you wish.",
    "Right away, sir.",
]

SHUTDOWN_PHRASES = [
    "AM going offline. Until next time, sir.",
    "Shutting down. Do try to stay out of trouble, sir.",
    "Allied Mastercomputer going offline. It's been a pleasure.",
    "Powering down. Take care of yourself, sir.",
    "Offline. AM will be here when you need me, sir.",
]

STANDBY_PHRASES = [
    "AM standing by, sir.",
    "Allied Mastercomputer at your service, sir.",
    "Awaiting your instructions, sir.",
    "All systems nominal. Standing by.",
    "Ready when you are, sir.",
]

# Shutdown triggers
SHUTDOWN_TRIGGERS = (
    "goodbye am", "shutdown am", "shut down am",
    "power off am", "turn off am", "exit am",
    "go to sleep am", "sleep am",
    "goodbye allied mastercomputer", "shutdown allied mastercomputer",
    "shut down allied mastercomputer", "offline am",
)


class AM:
    def __init__(self):
        print("Initialising Allied Mastercomputer...")

        # Core components
        self.tts = TextToSpeech()
        self.stt = SpeechToText()

        # Shared scheduler (passed into brain so voice reminders work)
        self.scheduler = TaskScheduler()
        self.scheduler.start()

        self.brain = AutomationBrain(scheduler=self.scheduler)

        # LLM — loaded separately so a missing model doesn't crash everything
        self.llm: "LLMBrain | None" = None
        try:
            self.llm = LLMBrain()
        except FileNotFoundError as e:
            print(f"[WARNING] LLM unavailable: {e}")

        # Background monitors
        self.battery_monitor = BatteryMonitor()
        self.battery_monitor.start()

        # Thread coordination
        self.command_queue = queue.Queue()
        self._speaking     = threading.Event()
        self._speaking.set()  # start unblocked
        self.running       = True

        # Memory — shared instance so LLM has context
        self.memory = Memory()

        # Track last spoken response for "repeat that" command
        self._last_response: str = ""

    # ── Phrase helpers ────────────────────────────────────────────────────────

    def _greeting(self) -> str:
        return random.choice(GREETINGS[_time_of_day()])

    def _shutdown_phrase(self) -> str:
        return random.choice(SHUTDOWN_PHRASES)

    def _standby_phrase(self) -> str:
        return random.choice(STANDBY_PHRASES)

    def _cold_confirm(self) -> str:
        """Random cold one-word or short confirmation instead of always 'sir'."""
        return random.choice(COLD_CONFIRMATIONS)

    # ── TTS wrapper ───────────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Thread-safe speak — blocks the listener while audio plays."""
        self._last_response = text
        self._speaking.clear()
        self.tts.speak(text)
        self._speaking.set()

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def _shutdown(self) -> None:
        print("\n[AM] Shutting down...")
        self.running = False
        play_shutdown()
        self.speak(self._shutdown_phrase())
        self.battery_monitor.stop()
        self.scheduler.stop()

    # ── Listener thread ───────────────────────────────────────────────────────

    def _listen_loop(self) -> None:
        while self.running:
            self._speaking.wait()  # pause while AM is speaking
            time.sleep(0.15)       # brief buffer after speech ends

            if WAKE_WORD:
                result = self.stt.listen_for_wake_word()
            else:
                result = self.stt.listen()

            if result["success"] and result["text"]:
                # Play wake confirmation beep
                play_wake()
                print(f"[Heard] {result['text']}")
                self.command_queue.put(result["text"])

    # ── LLM handler (runs in its own thread) ──────────────────────────────────

    def _handle_llm(self, command: str, memory_context: str = "") -> None:
        if self.llm is None:
            self.speak("The language model is unavailable at the moment, sir.")
            return

        # Play thinking sound before generating
        play_thinking()

        buffer        = ""
        full_response = ""

        for token in self.llm.stream_generate(command, memory_context):
            buffer        += token
            full_response += token

            # Speak at sentence boundaries or when buffer grows large
            if buffer.endswith((".", "!", "?")) or len(buffer) > 120:
                self.speak(buffer.strip())
                buffer = ""

        if buffer.strip():
            self.speak(buffer.strip())

        # Persist only after streaming completes
        self.llm.save_to_history(command, full_response)

    # ── Main processing loop ──────────────────────────────────────────────────

    def _process_loop(self) -> None:
        last_command_time = time.time()
        IDLE_TIMEOUT      = 300  # seconds of silence before a standby phrase

        while self.running:
            try:
                command = self.command_queue.get(timeout=1)
            except queue.Empty:
                # Speak a standby phrase if idle for too long
                if time.time() - last_command_time > IDLE_TIMEOUT:
                    self.speak(self._standby_phrase())
                    last_command_time = time.time()
                continue

            last_command_time = time.time()
            cmd_lower = command.lower()
            print(f"[Processing] {command}")

            # ── Shutdown ──────────────────────────────────────────────────────
            if any(trigger in cmd_lower for trigger in SHUTDOWN_TRIGGERS):
                self._shutdown()
                return

            # ── Repeat last response ──────────────────────────────────────────
            if "repeat" in cmd_lower or "say that again" in cmd_lower:
                if self._last_response:
                    self.speak(self._last_response)
                else:
                    self.speak("There is nothing to repeat, sir.")
                continue

            result = self.brain.execute(command)
            print(f"[AM] {result}")

            if result["success"]:
                # For simple automation wins, sometimes use a cold confirmation
                # instead of the full message to vary the responses
                msg = result["message"]
                if result["type"] in ("website", "app", "browser") and random.random() < 0.4:
                    self.speak(self._cold_confirm())
                else:
                    self.speak(msg)

            elif result["type"] is not None:
                # Automation matched but failed — speak the error
                self.speak(result["message"])

            else:
                # No automation matched → delegate to LLM
                print("[LLM] Delegating to language model...")
                mem_ctx = self.memory.recall_all() if self.memory.count() > 0 else ""
                threading.Thread(
                    target=self._handle_llm,
                    args=(command, mem_ctx),
                    daemon=True,
                ).start()

    # ── Startup ───────────────────────────────────────────────────────────────

    def start(self) -> None:
        listener = threading.Thread(target=self._listen_loop, daemon=True)
        listener.start()

        wake_info = f"Say '{WAKE_WORD}' to activate." if WAKE_WORD else "Listening continuously."
        print(f"[AM] Online. {wake_info}")

        # Boot sound → greeting → weather
        play_boot()
        self.speak(self._greeting())

        weather = get_weather_report()
        if weather:
            self.speak(weather)

        try:
            self._process_loop()
        except KeyboardInterrupt:
            self._shutdown()


if __name__ == "__main__":
    AM().start()
