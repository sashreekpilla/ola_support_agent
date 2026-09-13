from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EVAL = ROOT / "eval"
CHROMA_PATH = os.getenv("CHROMA_PATH", str(ROOT / ".chroma"))
SQLITE_PATH = os.getenv("SQLITE_PATH", str(DATA / "support_tickets.db"))
LOG_PATH = os.getenv("LOG_PATH", str(ROOT / "app.log"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MOCK_LLM = os.getenv("MOCK_LLM", "true").lower() == "true"
ESCALATION_THRESHOLD = 0.80
TOKEN_BUDGET = 1200
MAX_INPUT_CHARS = 4000
FIXED_CHUNK_SIZE = 350
FIXED_CHUNK_OVERLAP = 70
TOP_K = 3
