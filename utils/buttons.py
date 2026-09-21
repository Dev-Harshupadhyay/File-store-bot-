"""
Coloured buttons — ButtonStyle (Bot API 9.4 / MTProto layer 227+).

    blue()   -> PRIMARY  (dark blue)   — normal actions
    green()  -> SUCCESS  (green)       — positive / confirm
    red()    -> DANGER   (red)         — destructive / warning
    grey()   -> DEFAULT  (transparent) — neutral

Library me ButtonStyle na ho to style chup-chaap drop ho jata hai —
button phir bhi banta hai, bas rang nahi dikhta. Crash kabhi nahi hoga.
"""
from pyrogram.types import InlineKeyboardButton

# ── style support detect ──────────────────────────────────────────────
try:
    from pyrogram.enums import ButtonStyle

    STYLES_OK = True
except ImportError:  # purana pyrogram
    ButtonStyle = None
    STYLES_OK = False

# panel toggle (database import circular na ho isliye module-level flag)
COLORS_ENABLED = True


def _mk(text, style, **kw):
    """InlineKeyboardButton banao — style tabhi jab library support kare."""
    kw = {k: v for k, v in kw.items() if v is not None}
    if style is not None and STYLES_OK and COLORS_ENABLED:
        try:
            return InlineKeyboardButton(text, style=style, **kw)
        except TypeError:
            pass
    return InlineKeyboardButton(text, **kw)


# ── public helpers ────────────────────────────────────────────────────
def blue(text, **kw):
    """Dark blue — normal / main actions."""
    return _mk(text, ButtonStyle.PRIMARY if STYLES_OK else None, **kw)


def green(text, **kw):
    """Green — positive actions (done, approve, backup, open link)."""
    return _mk(text, ButtonStyle.SUCCESS if STYLES_OK else None, **kw)


def red(text, **kw):
    """Red — destructive / warning (ban, revoke, delete, close)."""
    return _mk(text, ButtonStyle.DANGER if STYLES_OK else None, **kw)


def grey(text, **kw):
    """Neutral — back, info."""
    return _mk(text, ButtonStyle.DEFAULT if STYLES_OK else None, **kw)


def plain(text, **kw):
    """Bilkul plain button — koi style nahi."""
    kw = {k: v for k, v in kw.items() if v is not None}
    return InlineKeyboardButton(text, **kw)


def set_colors(enabled: bool):
    """Panel toggle se colours on/off."""
    global COLORS_ENABLED
    COLORS_ENABLED = bool(enabled)


def status():
    return {
        "library_supports": STYLES_OK,
        "enabled": COLORS_ENABLED,
        "active": STYLES_OK and COLORS_ENABLED,
    }
