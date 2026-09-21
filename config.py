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
UPDATES_LINK = os.environ.get("UPDATES_LINK", "https://t.me/pm_harsh")

# ── force sub channels env se (volume na ho to DB reset ho jata hai,
#    isliye har start pe ye channels dobara seed ho jate hain) ──
#    FSUB_CHANNELS="-1002644259946,-1001234567890:request,@mychannel"
FSUB_CHANNELS = [c.strip() for c in
                 os.environ.get("FSUB_CHANNELS", "").split(",") if c.strip()]

# ── logging (LOG_CHANNEL me kya kya jaye) ──
LOG_STARTUP = _bool("LOG_STARTUP", False)     # "bot started" message
LOG_NEW_USER = _bool("LOG_NEW_USER", True)    # naya user aaya
LOG_FILES = _bool("LOG_FILES", False)         # har delivery / batch


def validate():
    missing = [k for k, v in {
        "API_ID": API_ID, "API_HASH": API_HASH, "BOT_TOKEN": BOT_TOKEN,
        "OWNER_ID": OWNER_ID, "DB_CHANNEL": DB_CHANNEL,
    }.items() if not v]
    return missing


def token_problem():
    """BOT_TOKEN ka format check — galat ho to reason string return karta hai."""
    tok = BOT_TOKEN
    if not tok:
        return "BOT_TOKEN set hi nahi hai"
    if tok != tok.strip():
        return "token ke aage/peeche space hai"
    if tok[0] in "\"'" or tok[-1] in "\"'":
        return "token ke aas-paas quotes hain — hata do"
    if ":" not in tok:
        return "token me ':' nahi hai (format: 123456:AAE...)"
    head, _, tail = tok.partition(":")
    if not head.isdigit():
        return f"token ka pehla hissa number nahi hai: {head[:20]}"
    if len(tail) < 30:
        return "token adhura lag raha hai (bahut chhota)"
    return None


def bot_id():
    """Token se bot ki user id nikaalo."""
    try:
        return int(BOT_TOKEN.split(":")[0])
    except (ValueError, IndexError, AttributeError):
        return 0
