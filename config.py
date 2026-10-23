import os

APP_NAME = "LazyDesk AI"
DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT", "180"))
