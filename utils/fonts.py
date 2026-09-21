"""
Screenshot wale stylish fonts (sᴍᴀʟʟ ᴄᴀᴘs) + button icons.
"""

_SMALL = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}

_BOLD = {
    **{chr(ord("A") + i): chr(0x1D5D4 + i) for i in range(26)},
    **{chr(ord("a") + i): chr(0x1D5EE + i) for i in range(26)},
    **{chr(ord("0") + i): chr(0x1D7EC + i) for i in range(10)},
}


def sc(text: str) -> str:
    """pure small caps -> sᴛᴀᴛs"""
    return "".join(_SMALL.get(ch, ch) for ch in str(text).lower())


def tc(text: str) -> str:
    """Title small caps (screenshot style) -> Sᴛᴀᴛs / Bᴀɴ / Uɴʙᴀɴ"""
    out, new_word = [], True
    for ch in str(text):
        if ch.isalpha():
            out.append(ch.upper() if new_word else _SMALL.get(ch.lower(), ch))
            new_word = False
        else:
            out.append(ch)
            new_word = not ch.isdigit()
    return "".join(out)


def bold(text: str) -> str:
    return "".join(_BOLD.get(ch, ch) for ch in str(text))


def btn(icon: str, label: str) -> str:
    return f"{icon} {tc(label)}"


# quick aliases used across the bot
B = btn
