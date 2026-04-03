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
