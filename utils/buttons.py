"""
Coloured buttons — Kurigram ka ButtonStyle (Bot API 9.4 / MTProto layer 227+).

    blue()   -> PRIMARY  (dark blue)  — normal actions
    green()  -> SUCCESS  (green)      — positive / confirm
    red()    -> DANGER   (red)        — destructive / warning
    grey()   -> DEFAULT  (transparent)— neutral

Agar library purani hai (plain pyrogram) to style silently drop ho jata hai —
buttons phir bhi kaam karenge, bas rang nahi dikhega. Kuch crash nahi hoga.
"""
from pyrogram.types import InlineKeyboardButton as IKB

# ── style support detect ──────────────────────────────────────────────
try:
    from pyrogram import enums

    _PRIMARY = enums.ButtonStyle.PRIMARY
    _DANGER = enums.ButtonStyle.DANGER
    _SUCCESS = enums.ButtonStyle.SUCCESS
    _DEFAULT = enums.ButtonStyle.DEFAULT
    STYLES_OK = True
except (ImportError, AttributeError):  # plain pyrogram / purana fork
    _PRIMARY = _DANGER = _SUCCESS = _DEFAULT = None
    STYLES_OK = False

# panel se colours off karne ke liye (database import circular na ho isliye flag)
COLORS_ENABLED = True


def _mk(text, style=None, **kw):
    """IKB banao — style tabhi lagao jab library support kare aur colours on ho."""
    if style is not None and STYLES_OK and COLORS_ENABLED:
        try:
            return IKB(text, style=style, **kw)
        except TypeError:
            pass
    return IKB(text, **kw)


# ── public helpers ────────────────────────────────────────────────────
def blue(text, *, callback_data=None, url=None, **kw):
    """Dark blue — normal / main actions."""
    return _mk(text, _PRIMARY, callback_data=callback_data, url=url, **kw) \
        if url else _mk(text, _PRIMARY, callback_data=callback_data, **kw)


def green(text, *, callback_data=None, url=None, **kw):
    """Green — positive actions (done, approve, get files)."""
    return _mk(text, _SUCCESS, callback_data=callback_data, url=url, **kw) \
        if url else _mk(text, _SUCCESS, callback_data=callback_data, **kw)


def red(text, *, callback_data=None, url=None, **kw):
    """Red — destructive / warning (ban, revoke, delete, close)."""
    return _mk(text, _DANGER, callback_data=callback_data, url=url, **kw) \
        if url else _mk(text, _DANGER, callback_data=callback_data, **kw)


def grey(text, *, callback_data=None, url=None, **kw):
    """Neutral — back, info, disabled-looking."""
    return _mk(text, _DEFAULT, callback_data=callback_data, url=url, **kw) \
        if url else _mk(text, _DEFAULT, callback_data=callback_data, **kw)


def plain(text, **kw):
    """Bilkul plain button — koi style nahi."""
    return IKB(text, **kw)


def set_colors(enabled: bool):
    """Panel ke toggle se colours on/off."""
    global COLORS_ENABLED
    COLORS_ENABLED = bool(enabled)


def status():
    return {
        "library_supports": STYLES_OK,
        "enabled": COLORS_ENABLED,
        "active": STYLES_OK and COLORS_ENABLED,
    }
