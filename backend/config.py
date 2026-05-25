"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# Council members - local Ollama model names
# llama3.2-vision and gemma3 support image input; mistral and qwen2.5 are text-only
COUNCIL_MODELS = [
    "llama3.2-vision",
    "mistral",
    "gemma3",
    "qwen2.5",
]

# Chairman model - synthesizes final response (vision-capable for image queries)
CHAIRMAN_MODEL = "llama3.2-vision"

# Ollama local API endpoint (OpenAI-compatible)
OPENROUTER_API_URL = "http://localhost:11434/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
