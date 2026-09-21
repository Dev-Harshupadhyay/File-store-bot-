"""
SQLite database — Railway volume (/data) par rehta hai, redeploy pe data safe.
"""
import json
import sqlite3
import threading
import time

import config

_lock = threading.RLock()
_conn = sqlite3.connect(config.DB_PATH, check_same_thread=False, timeout=30)
_conn.row_factory = sqlite3.Row
_conn.execute("PRAGMA journal_mode=WAL")
_conn.execute("PRAGMA synchronous=NORMAL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    name        TEXT,
    username    TEXT,
    joined      INTEGER,
    banned      INTEGER DEFAULT 0,
    ban_reason  TEXT,
    files_got   INTEGER DEFAULT 0,
    last_seen   INTEGER
);
CREATE TABLE IF NOT EXISTS batches (
    code        TEXT PRIMARY KEY,
    owner       INTEGER,
    title       TEXT,
    msg_ids     TEXT,
    count       INTEGER,
    created     INTEGER,
    opens       INTEGER DEFAULT 0,
    protect     INTEGER DEFAULT 0,
    revoked     INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS admins (
    user_id     INTEGER PRIMARY KEY,
    added_by    INTEGER,
    added_at    INTEGER
);
CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT
);
CREATE TABLE IF NOT EXISTS fsub (
    chat_id     INTEGER PRIMARY KEY,
    title       TEXT,
    invite      TEXT
);
CREATE TABLE IF NOT EXISTS logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          INTEGER,
    actor       INTEGER,
    action      TEXT,
    detail      TEXT
);
CREATE INDEX IF NOT EXISTS idx_batch_owner ON batches(owner);
CREATE INDEX IF NOT EXISTS idx_logs_ts ON logs(ts);
"""

with _lock:
    _conn.executescript(SCHEMA)
    _conn.commit()


def _q(sql, args=(), *, fetch=None):
    with _lock:
        cur = _conn.execute(sql, args)
        if fetch == "one":
            row = cur.fetchone()
            _conn.commit()
            return row
        if fetch == "all":
            rows = cur.fetchall()
            _conn.commit()
            return rows
        _conn.commit()
        return cur


def now():
    return int(time.time())


# ───────────────────────────── SETTINGS ─────────────────────────────
_DEFAULTS = {
    "auto_delete": str(config.AUTO_DELETE),
    "protect": "1" if config.PROTECT_CONTENT else "0",
    "force_sub": "1" if config.FORCE_SUB else "0",
    "maintenance": "0",
    "approval": "1",
    "start_photo": config.START_PHOTO,
    "start_text": "",
    "caption": "",
}


def get(key, default=None):
    row = _q("SELECT value FROM settings WHERE key=?", (key,), fetch="one")
    if row is None:
        return _DEFAULTS.get(key, default)
    return row["value"]


def get_int(key, default=0):
    try:
        return int(get(key, default))
    except (TypeError, ValueError):
        return default


def get_bool(key, default=False):
    return str(get(key, "1" if default else "0")) in ("1", "true", "True", "on")


def set(key, value):  # noqa: A001
    _q("INSERT INTO settings(key,value) VALUES(?,?) "
       "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))


def toggle(key, default=False):
    new = not get_bool(key, default)
    set(key, "1" if new else "0")
    return new


# ───────────────────────────── USERS ─────────────────────────────
def add_user(user_id, name="", username=""):
    _q("INSERT INTO users(user_id,name,username,joined,last_seen) VALUES(?,?,?,?,?) "
       "ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, username=excluded.username, "
       "last_seen=excluded.last_seen",
       (user_id, name, username or "", now(), now()))


def get_user(user_id):
    return _q("SELECT * FROM users WHERE user_id=?", (user_id,), fetch="one")


def all_users(only_active=True):
    sql = "SELECT user_id FROM users" + (" WHERE banned=0" if only_active else "")
    return [r["user_id"] for r in _q(sql, fetch="all")]


def count_users():
    return _q("SELECT COUNT(*) c FROM users", fetch="one")["c"]


def count_banned():
    return _q("SELECT COUNT(*) c FROM users WHERE banned=1", fetch="one")["c"]


def new_users_since(ts):
    return _q("SELECT COUNT(*) c FROM users WHERE joined>=?", (ts,), fetch="one")["c"]


def ban_user(user_id, reason="No reason"):
    add_user(user_id)
    _q("UPDATE users SET banned=1, ban_reason=? WHERE user_id=?", (reason, user_id))


def unban_user(user_id):
    _q("UPDATE users SET banned=0, ban_reason=NULL WHERE user_id=?", (user_id,))


def is_banned(user_id):
    row = get_user(user_id)
    return bool(row and row["banned"])


def banned_list():
    return _q("SELECT * FROM users WHERE banned=1 ORDER BY user_id", fetch="all")


def bump_files(user_id, n=1):
    _q("UPDATE users SET files_got=files_got+?, last_seen=? WHERE user_id=?", (n, now(), user_id))


def recent_users(limit=10):
    return _q("SELECT * FROM users ORDER BY joined DESC LIMIT ?", (limit,), fetch="all")


# ───────────────────────────── BATCHES ─────────────────────────────
def save_batch(code, owner, msg_ids, title="", protect=0):
    _q("INSERT OR REPLACE INTO batches(code,owner,title,msg_ids,count,created,opens,protect,revoked) "
       "VALUES(?,?,?,?,?,?,COALESCE((SELECT opens FROM batches WHERE code=?),0),?,0)",
       (code, owner, title, json.dumps(msg_ids), len(msg_ids), now(), code, protect))


def get_batch(code):
    row = _q("SELECT * FROM batches WHERE code=?", (code,), fetch="one")
    if not row:
        return None
    d = dict(row)
    d["msg_ids"] = json.loads(d["msg_ids"])
    return d


def bump_open(code):
    _q("UPDATE batches SET opens=opens+1 WHERE code=?", (code,))


def revoke_batch(code, flag=1):
    _q("UPDATE batches SET revoked=? WHERE code=?", (flag, code))


def delete_batch(code):
    _q("DELETE FROM batches WHERE code=?", (code,))


def count_batches():
    return _q("SELECT COUNT(*) c FROM batches", fetch="one")["c"]


def count_files():
    row = _q("SELECT COALESCE(SUM(count),0) c FROM batches", fetch="one")
    return row["c"]


def total_opens():
    return _q("SELECT COALESCE(SUM(opens),0) c FROM batches", fetch="one")["c"]


def recent_batches(limit=10):
    return _q("SELECT * FROM batches ORDER BY created DESC LIMIT ?", (limit,), fetch="all")


def top_batches(limit=10):
    return _q("SELECT * FROM batches ORDER BY opens DESC LIMIT ?", (limit,), fetch="all")


# ───────────────────────────── ADMINS ─────────────────────────────
def add_admin(user_id, by=0):
    _q("INSERT OR IGNORE INTO admins(user_id,added_by,added_at) VALUES(?,?,?)",
       (user_id, by, now()))


def rm_admin(user_id):
    _q("DELETE FROM admins WHERE user_id=?", (user_id,))


def admin_ids():
    dyn = [r["user_id"] for r in _q("SELECT user_id FROM admins", fetch="all")]
    return list(dict.fromkeys([config.OWNER_ID, *config.ADMINS, *dyn]))


def is_admin(user_id):
    return user_id in admin_ids()


def is_owner(user_id):
    return user_id == config.OWNER_ID


# ───────────────────────────── FORCE SUB ─────────────────────────────
def add_fsub(chat_id, title="", invite=""):
    _q("INSERT OR REPLACE INTO fsub(chat_id,title,invite) VALUES(?,?,?)", (chat_id, title, invite))


def rm_fsub(chat_id):
    _q("DELETE FROM fsub WHERE chat_id=?", (chat_id,))


def fsub_list():
    return _q("SELECT * FROM fsub", fetch="all")


# ───────────────────────────── AUDIT LOG ─────────────────────────────
def log(actor, action, detail=""):
    _q("INSERT INTO logs(ts,actor,action,detail) VALUES(?,?,?,?)", (now(), actor, action, detail))


def get_logs(limit=15):
    return _q("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,), fetch="all")


def clear_logs():
    _q("DELETE FROM logs")


def db_size():
    import os
    try:
        return os.path.getsize(config.DB_PATH)
    except OSError:
        return 0
