"""
Harsh File Store Bot  ·  Configuration
Sab kuch Railway ke Variables tab se aayega.
"""
import os


def _int(key, default=0):
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return int(default)


def _bool(key, default=False):
    return str(os.environ.get(key, default)).strip().lower() in ("1", "true", "yes", "on")


def _list_int(key):
    raw = os.environ.get(key, "").replace(",", " ").split()
    out = []
    for x in raw:
        try:
            out.append(int(x))
        except ValueError:
            pass
    return out


# ───────────────────────────── TELEGRAM CORE ─────────────────────────────
API_ID = _int("API_ID")                       # my.telegram.org
API_HASH = os.environ.get("API_HASH", "")     # my.telegram.org
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")   # @BotFather

OWNER_ID = _int("OWNER_ID")                   # tumhari user id (permanent super-admin)
ADMINS = list({*_list_int("ADMINS"), OWNER_ID} - {0})

DB_CHANNEL = _int("DB_CHANNEL")               # private channel -100xxxx (bot = admin)
LOG_CHANNEL = _int("LOG_CHANNEL") or DB_CHANNEL

BOT_NAME = os.environ.get("BOT_NAME", "Harsh File Store Bot")
BOT_VERSION = os.environ.get("BOT_VERSION", "v1.0")

# ───────────────────────────── STORAGE (RAILWAY VOLUME) ──────────────────
# Railway me volume ka Mount Path = /data  rakhna hai.
DATA_DIR = os.environ.get("DATA_DIR", "/data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    _probe = os.path.join(DATA_DIR, ".write_test")
    with open(_probe, "w") as f:
        f.write("ok")
    os.remove(_probe)
except Exception:  # volume mount nahi hai -> local folder (data loss on redeploy)
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "filestore.db")
SESSION_DIR = DATA_DIR

# ───────────────────────────── DEFAULT BEHAVIOUR ─────────────────────────
AUTO_DELETE = _int("AUTO_DELETE", 1800)       # seconds (1800 = 30 minute)
PROTECT_CONTENT = _bool("PROTECT_CONTENT", False)
FORCE_SUB = _bool("FORCE_SUB", False)
COLOR_BUTTONS = _bool("COLOR_BUTTONS", True)
MAINTENANCE = False

WORKERS = _int("WORKERS", 8)
PORT = _int("PORT", 8080)                     # Railway health check

START_PHOTO = os.environ.get("START_PHOTO", "")
SUPPORT_LINK = os.environ.get("SUPPORT_LINK", "")
UPDATES_LINK = os.environ.get("UPDATES_LINK", "")


def validate():
    missing = [k for k, v in {
        "API_ID": API_ID, "API_HASH": API_HASH, "BOT_TOKEN": BOT_TOKEN,
        "OWNER_ID": OWNER_ID, "DB_CHANNEL": DB_CHANNEL,
    }.items() if not v]
    return missing
