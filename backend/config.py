"""
LogoForge AI - Centralized Configuration Module.

Loads environment variables from .env and provides application-wide
configuration constants for the logo generation service.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Hugging Face Configuration ---
HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
HF_MODEL_ID: str = "black-forest-labs/FLUX.1-schnell"

# --- File Storage Configuration ---
# Use a path relative to project root to avoid hardcoded path issues
GENERATED_DIR: Path = Path(__file__).resolve().parent.parent / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# --- Image Generation Constraints ---
MAX_IMAGES_PER_REQUEST: int = 4
IMAGE_SIZE: int = 512  # 512px — stable avec Pollinations

# --- Flask Configuration ---
DEBUG: bool = os.getenv("FLASK_DEBUG", "true").lower() == "true"
HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
PORT: int = int(os.getenv("FLASK_PORT", "5000"))
