"""
Chhote helper functions — encode/decode links, humanize, progress etc.
"""
import base64
import re
import secrets
import time


def make_code(n=8):
    """URL-safe short code — batch link ke liye."""
    return secrets.token_urlsafe(n)[:n].replace("-", "x").replace("_", "y")


def encode_ids(first: int, last: int) -> str:
    raw = f"get-{first}-{last}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_ids(data: str):
    pad = "=" * (-len(data) % 4)
    try:
        raw = base64.urlsafe_b64decode(data + pad).decode()
    except Exception:
        return None
    m = re.match(r"get-(\d+)-(\d+)", raw)
    return (int(m.group(1)), int(m.group(2))) if m else None


def human_size(num):
    num = float(num or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024:
            return f"{num:.2f} {unit}" if unit != "B" else f"{int(num)} B"
        num /= 1024
    return f"{num:.2f} PB"


def human_time(seconds):
    seconds = int(seconds or 0)
    if seconds <= 0:
        return "off"
    parts = []
    for label, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        if seconds >= size:
            val, seconds = divmod(seconds, size)
            parts.append(f"{val}{label}")
    return " ".join(parts[:2])


def uptime_since(start_ts):
    return human_time(int(time.time() - start_ts))


def ago(ts):
    if not ts:
        return "—"
    return human_time(int(time.time()) - int(ts)) + " ago"


def parse_target(text, message=None):
    """
    '/ban 12345 spam'  ->  (12345, 'spam')
    reply se bhi user nikal leta hai.
    """
    parts = (text or "").split(maxsplit=2)
    uid, reason = None, "No reason given"
    if len(parts) > 1:
        m = re.search(r"-?\d+", parts[1])
        if m:
            uid = int(m.group())
    if len(parts) > 2:
        reason = parts[2]
    if uid is None and message is not None and message.reply_to_message:
        r = message.reply_to_message
        if r.from_user:
            uid = r.from_user.id
    return uid, reason


def mention(user_id, name=None):
    name = name or str(user_id)
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def progress_bar(done, total, width=12):
    if not total:
        return "▱" * width
    filled = int(width * done / total)
    return "▰" * filled + "▱" * (width - filled)
