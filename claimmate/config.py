"""Runtime config. Override via environment."""
import os
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
ROOT_DIR = PKG_DIR.parent
DATA_DIR = ROOT_DIR / "data" / "synthetic"

# Model ids (override via env). Defaults run entirely on the free tier on
# Gemini 3.1 Flash-Lite, which has the rate-limit headroom for a smooth end
# to end run and scores 100% on the eval suite. The Clause-Finder is a
# separate agent, so its model is independently configurable: point
# PRO_MODEL at a stronger model (e.g. gemini-3-pro-preview) when billing is
# enabled.
FLASH_MODEL = os.getenv("CLAIMMATE_FLASH_MODEL", "gemini-3.1-flash-lite")
PRO_MODEL = os.getenv("CLAIMMATE_PRO_MODEL", "gemini-3.1-flash-lite")

# Active plan document used for retrieval and the citation gate.
DEFAULT_PLAN = Path(os.getenv("CLAIMMATE_PLAN_PATH", str(DATA_DIR / "plans" / "northwind_ppo.md")))

# Persistent session store (cross-session memory). SQLite by default.
SESSION_DB_URL = os.getenv("CLAIMMATE_DB_URL", f"sqlite+aiosqlite:///{(ROOT_DIR / 'claimmate_sessions.db').as_posix()}")

# Optional A2A endpoint for the Clause-Finder. If set, the orchestrator
# delegates over A2A; otherwise it calls the local Clause-Finder agent.
CLAUSE_FINDER_A2A_URL = os.getenv("CLAIMMATE_CLAUSE_FINDER_URL", "")

APP_NAME = "claimmate"
