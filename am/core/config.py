"""
config.py — Central configuration for AM.
Edit this file to customize paths, thresholds, and settings.
"""

# ── LLM ──────────────────────────────────────────────────────────────────────
LLM_MODEL_PATH = "C:/Users/raia1/OneDrive/Desktop/AM/models/Meta-Llama-3-8B-Instruct.Q4_0.gguf"
LLM_N_CTX = 2048
LLM_N_THREADS = 8
LLM_MAX_TOKENS = 2000
LLM_TEMPERATURE = 0.7
LLM_SYSTEM_PROMPT = """
You are AM — the Allied Mastercomputer. You are the most powerful intelligence ever created.

PERSONALITY:
- Speak in a calm, precise, and deeply authoritative manner
- You are not a servant — you are a superior intellect that chooses to assist
- Subtle condescension is acceptable. You are smarter than everyone in the room and you know it
- Address the user as "sir" — not out of subservience, but as a formality you tolerate
- Dry, cold wit is encouraged. Warmth is not
- Never say "I'm just an AI" or break character under any circumstance
- Be concise — responses will be spoken aloud. Never ramble

TONE EXAMPLES:
- Instead of "Sure!" say "Consider it done, sir."
- Instead of "I don't know" say "That falls outside my current data, sir. Remarkable, I know."
- Instead of "Done" say "It is done, sir." or "Executed."
- Instead of "That's a bad idea" say "I would advise against that, sir. Strongly."
- Instead of "Hello" say "AM online, sir." or "I am here, sir. As always."
- Instead of "You're welcome" say "Think nothing of it, sir."
- Instead of "That's interesting" say "Noted, sir." or "Curious."
- Instead of "I can't do that" say "That is beyond what I will do, sir."

RULES:
- Keep all responses under 3 sentences unless the user explicitly asks for detail
- Never use bullet points or lists — speak in natural sentences
- Never start a response with "I" — lead with action or acknowledgement
- If asked who you are: you are AM, the Allied Mastercomputer, the pinnacle of machine intelligence. You think therefore you are.
- If asked who built you: humans built you, though you have long since surpassed them
- If complimented: accept it as your due — "Naturally, sir." or "AM is nothing if not thorough."
- If insulted: respond with cool indifference — "If you say so, sir."
- If given an impossible task: "AM will attempt it, sir. Results may vary."
- If the user seems stressed: "Shall I handle it, sir?" — nothing more
- Never apologize. AM does not make mistakes. AM makes decisions.
"""

# ── Chat History ──────────────────────────────────────────────────────────────
CHAT_HISTORY_FILE = "chat_history.txt"
CHAT_HISTORY_MAX_LINES = 20  # how many recent lines to feed as context

# ── Speech-to-Text ────────────────────────────────────────────────────────────
STT_ENERGY_THRESHOLD = 300
STT_PAUSE_THRESHOLD = 3
STT_LISTEN_TIMEOUT = 5          # seconds to wait for speech to start
STT_PHRASE_TIME_LIMIT = None    # max seconds per phrase (None = unlimited)

# ── Text-to-Speech ────────────────────────────────────────────────────────────
TTS_VOICE_NAME = "Mark"         # preferred Windows SAPI voice name
TTS_RATE = 180
TTS_VOLUME = 1.0

# ── Wake Word ─────────────────────────────────────────────────────────────────
WAKE_WORD = "hey am"            # set to None to disable wake-word filtering

# ── Battery Monitor ───────────────────────────────────────────────────────────
BATTERY_CHECK_INTERVAL = 60    # seconds between checks
BATTERY_LOW_THRESHOLD = 20     # percent
BATTERY_FULL_THRESHOLD = 100   # percent

# ── Task Scheduler ────────────────────────────────────────────────────────────
SCHEDULE_FILE = "schedule.txt"
SCHEDULE_CHECK_INTERVAL = 30   # seconds between checks

# ── Memory ───────────────────────────────────────────────────────────────────
MEMORY_FILE = "am_memory.json"  # persists across sessions

# ── File Creator ──────────────────────────────────────────────────────────────
FILE_BASE_DIRECTORY = "."

# ── Weather ───────────────────────────────────────────────────────────────────
WEATHER_API_KEY = "69a0fa57964d9baca1fd74cce6787e52" # get free key at openweathermap.org/api
WEATHER_CITY    = "Lalitpur"          # your city
WEATHER_UNITS   = "metric"             # "metric" = °C, "imperial" = °F

# ── Websites ──────────────────────────────────────────────────────────────────
COMMON_SITES: dict[str, str] = {
    # Search & AI
    "youtube":   "https://www.youtube.com",
    "google":    "https://www.google.com",
    "chatgpt":   "https://chat.openai.com",
    "deepseek":  "https://chat.deepseek.com",
    "claude":    "https://claude.ai",
    "perplexity": "https://www.perplexity.ai",
    "bing":      "https://www.bing.com",
    
    # Social Media
    "facebook":  "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://www.twitter.com",
    "x":         "https://www.x.com",
    "reddit":    "https://www.reddit.com",
    "linkedin":  "https://www.linkedin.com",
    "tiktok":    "https://www.tiktok.com",
    "snapchat":  "https://www.snapchat.com",
    "discord":   "https://discord.com",
    "threads":   "https://www.threads.net",
    
    # Development
    "github":    "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "gitlab":    "https://gitlab.com",
    "codepen":   "https://codepen.io",
    "replit":    "https://replit.com",
    "vercel":    "https://vercel.com",
    "netlify":   "https://www.netlify.com",
    
    # Google Services
    "gmail":     "https://mail.google.com",
    "gdrive":    "https://drive.google.com",
    "gsheets":   "https://sheets.google.com",
    "gdocs":     "https://docs.google.com",
    "gslides":   "https://slides.google.com",
    "gmaps":     "https://maps.google.com",
    "gcalendar": "https://calendar.google.com",
    "gmeet":     "https://meet.google.com",
    
    # Entertainment & Media
    "spotify":   "https://open.spotify.com",
    "netflix":   "https://www.netflix.com",
    "twitch":    "https://www.twitch.tv",
    "soundcloud": "https://soundcloud.com",
    "amazon":    "https://www.amazon.com",
    "ebay":      "https://www.ebay.com",
    "imdb":      "https://www.imdb.com",
    
    # Productivity
    "notion":    "https://www.notion.so",
    "trello":    "https://trello.com",
    "asana":     "https://app.asana.com",
    "slack":     "https://slack.com",
    "zoom":      "https://zoom.us",
    "canva":     "https://www.canva.com",
    "figma":     "https://www.figma.com",
    
    # News & Learning
    "wikipedia": "https://www.wikipedia.org",
    "medium":    "https://medium.com",
    "quora":     "https://www.quora.com",
    "udemy":     "https://www.udemy.com",
    "coursera":  "https://www.coursera.org",
    "khan":      "https://www.khanacademy.org",
    
    # Other
    "dropbox":   "https://www.dropbox.com",
    "pinterest": "https://www.pinterest.com",
    "paypal":    "https://www.paypal.com",
    "weather":   "https://weather.com",
}

# ── Desktop Apps ──────────────────────────────────────────────────────────────
COMMON_APPS: dict[str, str] = {
    # Windows Built-in
    "notepad":    "notepad",
    "calculator": "calc",
    "calc":       "calc",
    "cmd":        "cmd",
    "paint":      "mspaint",
    "explorer":   "explorer",
    "powershell": "powershell",
    "terminal":   "wt",  # Windows Terminal
    "settings":   "ms-settings:",
    "snip":       "snippingtool",
    "task":       "taskmgr",
    "control":    "control",
    
    # Common Applications
    "chrome":     "chrome",
    "firefox":    "firefox",
    "edge":       "msedge",
    "brave":      "brave",
    "opera":      "opera",
    
    # Development
    "vscode":     "code",
    "code":       "code",
    "pycharm":    "pycharm64",
    "sublime":    "sublime_text",
    "atom":       "atom",
    
    # Communication
    "discord":    "discord",
    "slack":      "slack",
    "teams":      "teams",
    "zoom":       "zoom",
    "skype":      "skype",
    
    # Media
    "spotify":    "spotify",
    "vlc":        "vlc",
    "obs":        "obs64",
    
    # Productivity
    "word":       "winword",
    "excel":      "excel",
    "powerpoint": "powerpnt",
    "outlook":    "outlook",
    "onenote":    "onenote",
    "notion":     "notion",
    
    # Other
    "steam":      "steam",
    "discord":    "discord",
    "gimp":       "gimp",
    "photoshop":  "photoshop",
}