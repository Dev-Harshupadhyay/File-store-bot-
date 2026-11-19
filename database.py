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
    invite      TEXT,
    mode        TEXT DEFAULT 'join',
    added_at    INTEGER
);
CREATE TABLE IF NOT EXISTS join_requests (
    chat_id     INTEGER,
    user_id     INTEGER,
    ts          INTEGER,
    PRIMARY KEY (chat_id, user_id)
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
    # purane database ke liye migration
    cols = [r[1] for r in _conn.execute("PRAGMA table_info(fsub)")]
    if "mode" not in cols:
        _conn.execute("ALTER TABLE fsub ADD COLUMN mode TEXT DEFAULT 'join'")
    if "added_at" not in cols:
        _conn.execute("ALTER TABLE fsub ADD COLUMN added_at INTEGER")
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
    "colors": "1",
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
def add_fsub(chat_id, title="", invite="", mode="join"):
    _q("INSERT OR REPLACE INTO fsub(chat_id,title,invite,mode,added_at) VALUES(?,?,?,?,?)",
       (chat_id, title, invite, mode, now()))


def get_fsub(chat_id):
    return _q("SELECT * FROM fsub WHERE chat_id=?", (chat_id,), fetch="one")


def count_fsub():
    return _q("SELECT COUNT(*) c FROM fsub", fetch="one")["c"]


# ── join requests (request-mode force sub) ──
def add_join_request(chat_id, user_id):
    _q("INSERT OR IGNORE INTO join_requests(chat_id,user_id,ts) VALUES(?,?,?)",
       (chat_id, user_id, now()))


def has_join_request(chat_id, user_id):
    return _q("SELECT 1 FROM join_requests WHERE chat_id=? AND user_id=?",
              (chat_id, user_id), fetch="one") is not None


def rm_join_request(chat_id, user_id):
    _q("DELETE FROM join_requests WHERE chat_id=? AND user_id=?", (chat_id, user_id))


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


USER_FIELDS = ('user_id', 'name', 'username', 'joined', 'banned', 'ban_reason',
               'files_got', 'last_seen')


def export_users():
    return {'format': 'filestore-users-v1', 'users': [dict(row) for row in
            _q('SELECT * FROM users ORDER BY user_id', fetch='all')]}


def restore_users(payload):
    if (not isinstance(payload, dict) or payload.get('format') != 'filestore-users-v1'
            or not isinstance(payload.get('users'), list)):
        raise ValueError('Invalid user backup')
    rows = []
    for row in payload['users']:
        if not isinstance(row, dict) or not all(key in row for key in USER_FIELDS):
            raise ValueError('Invalid user row')
        for key in ('user_id', 'joined', 'banned', 'files_got', 'last_seen'):
            if type(row[key]) is not int or not 0 <= row[key] < 2**63:
                raise ValueError('Invalid numeric field')
        if not row['user_id'] or row['banned'] not in (0, 1):
            raise ValueError('Invalid user ID or ban flag')
        if any(row[k] is not None and not isinstance(row[k], str)
               for k in ('name', 'username', 'ban_reason')):
            raise ValueError('Invalid text field')
        rows.append(tuple(row[key] for key in USER_FIELDS))
    with _lock, _conn:
        cur = _conn.executemany(
            'INSERT INTO users (' + ','.join(USER_FIELDS) + ') VALUES (?,?,?,?,?,?,?,?) '
            'ON CONFLICT(user_id) DO NOTHING', rows)
        return cur.rowcount


def snapshot(path):
    with _lock:
        target = sqlite3.connect(path)
        try:
            _conn.backup(target)
        finally:
            target.close()


def auto_delete_seconds():
    return max(0, get_int('auto_delete', 1800)) if get_bool('auto_delete_on', True) else 0


def set_auto_delete(seconds):
    if not 0 <= seconds <= 86400:
        raise ValueError('Choose 0 to 86400 seconds')
    with _lock, _conn:
        _conn.executemany('INSERT INTO settings(key,value) VALUES(?,?) '
                          'ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                          [('auto_delete', str(seconds)), ('auto_delete_on', str(int(seconds > 0)))])


_q('''CREATE TABLE IF NOT EXISTS delete_jobs (
    id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, msg_ids TEXT NOT NULL,
    due INTEGER NOT NULL, link TEXT NOT NULL, count INTEGER NOT NULL
)''')
_q('CREATE INDEX IF NOT EXISTS delete_jobs_due ON delete_jobs(due)')


def queue_delete(chat_id, msg_ids, delay, link, count):
    _q('INSERT INTO delete_jobs(chat_id,msg_ids,due,link,count) VALUES(?,?,?,?,?)',
       (chat_id, json.dumps(msg_ids), now() + delay, link, count))


def due_deletes():
    return _q('SELECT * FROM delete_jobs WHERE due<=? ORDER BY due LIMIT 25',
              (now(),), fetch='all')


def finish_delete(job_id):
    _q('DELETE FROM delete_jobs WHERE id=?', (job_id,))


def retry_delete(job_id, delay):
    _q('UPDATE delete_jobs SET due=? WHERE id=?', (now() + delay, job_id))
