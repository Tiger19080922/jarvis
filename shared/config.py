import os
from pathlib import Path

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
ONEDRIVE_FOLDER   = os.environ.get("ONEDRIVE_MOM_FOLDER",
                    str(Path.home() / "OneDrive" / "MoMs"))

JARVIS_ROOT   = Path.home() / "jarvis"
OUTPUTS_DIR   = JARVIS_ROOT / "outputs"
LOGS_DIR      = JARVIS_ROOT / "logs"
DATA_DIR      = JARVIS_ROOT / "data"

# ── Credentials (stored outside all repos — never committed) ───────────────────
JARVIS_CREDENTIALS_DIR = Path.home() / ".jarvis" / "credentials"

# ── MoM Maker ─────────────────────────────────────────────────────────────────
MOM_RECIPIENT_EMAIL   = os.environ.get("MOM_RECIPIENT_EMAIL", "")
GMAIL_CREDENTIALS_PATH = str(JARVIS_CREDENTIALS_DIR / "gmail_credentials.json")
GMAIL_TOKEN_PATH       = str(JARVIS_CREDENTIALS_DIR / "gmail_token.json")
GDRIVE_CREDENTIALS_PATH = str(JARVIS_CREDENTIALS_DIR / "gdrive_credentials.json")
GDRIVE_TOKEN_PATH       = str(JARVIS_CREDENTIALS_DIR / "gdrive_token.json")
GMAIL_APP_PASSWORD      = os.environ.get("GMAIL_APP_PASSWORD", "")
