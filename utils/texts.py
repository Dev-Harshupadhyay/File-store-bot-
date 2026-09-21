"""
Saare messages — Hinglish + stylish fonts.
"""
from utils.fonts import sc, tc

LINE = "━━━━━━━━━━━━━━━━━━━━"

START_USER = """<b>{bot}</b>
{line}
ʜᴇʟʟᴏ {mention} 👋

ʏᴇʜ ᴇᴋ <b>ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ</b> ʜᴀɪ.
ᴀᴅᴍɪɴ ᴋᴀ ᴅɪʏᴀ ʜᴜᴀ ʟɪɴᴋ ᴏᴘᴇɴ ᴋᴀʀᴏ — sᴀᴀʀɪ ғɪʟᴇs ʏᴀʜɪ ᴍɪʟ ᴊᴀᴇɴɢɪ.

⚠️ <b>ɴᴏᴛᴇ:</b> ғɪʟᴇs <b>{ad}</b> ᴋᴇ ʙᴀᴀᴅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʜᴏ ᴊᴀᴀᴛɪ ʜᴀɪɴ.
ᴋʜᴜᴅ ᴋᴇ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴍᴇ <b>ғᴏʀᴡᴀʀᴅ</b> ᴋᴀʀ ʟᴏ.
{line}"""

START_ADMIN = """<b>{bot} {ver}</b>
{line}
ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, <b>ᴀᴅᴍɪɴ</b> ★

◉ ᴜsᴇʀs: <code>{users}</code>
◆ ʙᴀᴛᴄʜᴇs: <code>{batches}</code>
▪️ ғɪʟᴇs: <code>{files}</code>

<code>/batch</code> — ᴍᴜʟᴛɪᴘʟᴇ ғɪʟᴇs ᴋᴀ ʟɪɴᴋ
<code>/panel</code> — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ
{line}"""

PANEL = """<b>⚙️ ᴀᴅᴍɪɴ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</b>
{line}
◉ ᴜsᴇʀs: <code>{users}</code>  ·  ✘ ʙᴀɴɴᴇᴅ: <code>{banned}</code>
◆ ʙᴀᴛᴄʜᴇs: <code>{batches}</code>  ·  ▪️ ғɪʟᴇs: <code>{files}</code>
❖ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: <code>{ad}</code>
⏱ ᴜᴘᴛɪᴍᴇ: <code>{up}</code>
{line}
<i>ɴᴇᴇᴄʜᴇ sᴇ ᴏᴘᴛɪᴏɴ ᴄʜᴜɴᴏ ↓</i>"""

BATCH_START = """<b>◆ ʙᴀᴛᴄʜ ᴍᴏᴅᴇ ᴏɴ</b>
{line}
ᴀʙ ᴇᴋ sᴀᴀᴛʜ ᴀᴘɴɪ <b>sᴀᴀʀɪ ғɪʟᴇs ʙʜᴇᴊ ᴅᴏ</b>.
ᴍᴀɪɴ ᴄʜᴜᴘ-ᴄʜᴀᴘ sᴀʙ sᴀᴠᴇ ᴋᴀʀᴛᴀ ʀᴀʜᴜɴɢᴀ — ᴋᴏɪ ʀᴇᴘʟʏ ɴᴀʜɪ ᴀᴀᴇɢᴀ.

ᴊᴀʙ sᴀʙ ʙʜᴇᴊ ᴅᴏ ᴛᴏ sɪʀғ <code>/done</code> ʟɪᴋʜᴏ — ʟɪɴᴋ ᴍɪʟ ᴊᴀᴇɢᴀ ✓
{line}
<i>/status — ᴋɪᴛɴɪ ʜᴜɪ · /cancel — ʀᴏᴋᴏ</i>"""

SINGLE_MODE = """<b>◈ sɪɴɢʟᴇ ᴍᴏᴅᴇ ᴏɴ</b>
{line}
ᴀʙ ᴊᴏ ʙʜɪ ғɪʟᴇ ʙʜᴇᴊᴏɢᴇ ᴜsᴋᴀ <b>ᴀʟᴀɢ ʟɪɴᴋ</b> ᴛᴜʀᴀɴᴛ ᴍɪʟᴇɢᴀ.

ᴍᴜʟᴛɪᴘʟᴇ ғɪʟᴇs ᴋᴀ <b>ᴇᴋ</b> ʟɪɴᴋ ᴄʜᴀʜɪʏᴇ? ᴛᴏ <code>/batch</code> ᴋᴀʀᴏ.
{line}"""

SINGLE_DONE = """<b>✅ ʟɪɴᴋ ʀᴇᴀᴅʏ</b>
{line}
◈ ᴄᴏᴅᴇ: <code>{code}</code>
❖ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: <code>{ad}</code>

🔗 <code>{link}</code>
{line}"""

BATCH_ADDED = "✓ <b>{n}</b> ғɪʟᴇs ᴄᴏʟʟᴇᴄᴛᴇᴅ · <code>/done</code> ᴛᴏ ғɪɴɪsʜ"

BATCH_DONE = """<b>✅ ʙᴀᴛᴄʜ ʟɪɴᴋ ʀᴇᴀᴅʏ</b>
{line}
▪️ ғɪʟᴇs: <code>{n}</code>
◈ ᴄᴏᴅᴇ: <code>{code}</code>
❖ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: <code>{ad}</code>

🔗 <code>{link}</code>

<i>ʏᴇʜ ʟɪɴᴋ ᴋɪsɪ ᴋᴏ ʙʜɪ ᴅᴏ — ʙᴏᴛ sᴛᴀʀᴛ ʜᴏᴛᴇ ʜɪ sᴀᴀʀɪ ғɪʟᴇs ᴍɪʟ ᴊᴀᴇɴɢɪ.</i>
{line}"""

SENDING = "⏳ <b>{n}</b> ғɪʟᴇs ʙʜᴇᴊ ʀᴀʜᴀ ʜᴏᴏɴ...\n{bar}"

DELETE_WARN = """<b>⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ</b>
{line}
ʏᴇʜ <b>{n}</b> ғɪʟᴇs <b>{ad}</b> ᴋᴇ ʙᴀᴀᴅ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʜᴏ ᴊᴀᴇɴɢɪ.
ᴊᴀʟᴅɪ sᴇ ᴀᴘɴᴇ <b>sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs</b> ᴍᴇ ғᴏʀᴡᴀʀᴅ ᴋᴀʀ ʟᴏ 📥
{line}"""

DELETED = """<b>🗑 ғɪʟᴇs ᴅᴇʟᴇᴛᴇᴅ</b>
{line}
ᴛɪᴍᴇ ᴋʜᴀᴛᴀᴍ — <b>{n}</b> ғɪʟᴇs ʜᴀᴛᴀ ᴅɪ ɢᴀʏɪ.
ᴅᴏʙᴀʀᴀ ᴄʜᴀʜɪʏᴇ? ɴᴇᴇᴄʜᴇ ᴋᴀ ʙᴜᴛᴛᴏɴ ᴅᴀʙᴀᴏ ↓
{line}"""

BANNED_MSG = """<b>🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ</b>
{line}
ʀᴇᴀsᴏɴ: <code>{reason}</code>
ᴀᴅᴍɪɴ sᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴏ.
{line}"""

MAINT_MSG = """<b>⚠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ</b>
{line}
ʙᴏᴛ ᴀʙʜɪ ᴜᴘɢʀᴀᴅᴇ ʜᴏ ʀᴀʜᴀ ʜᴀɪ. ᴛʜᴏᴅɪ ᴅᴇʀ ʙᴀᴀᴅ ᴛʀʏ ᴋᴀʀᴏ 🙏
{line}"""

FSUB_MSG = """<b>⚑ ᴊᴏɪɴ ʀᴇǫᴜɪʀᴇᴅ</b>
{line}
ғɪʟᴇ ʟᴇɴᴇ sᴇ ᴘᴇʜʟᴇ ɴᴇᴇᴄʜᴇ ᴅɪʏᴇ <b>sᴀᴀʀᴇ ᴄʜᴀɴɴᴇʟ ᴊᴏɪɴ</b> ᴋᴀʀᴏ,
ғɪʀ <b>↻ ᴛʀʏ ᴀɢᴀɪɴ</b> ᴅᴀʙᴀᴏ — ғɪʟᴇs ᴛᴜʀᴀɴᴛ ᴍɪʟ ᴊᴀᴇɴɢɪ.
{line}"""

DEV = """<b>👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ</b>
{line}
<b><a href="https://new-profotilo-flame.vercel.app">ʜᴀʀsʜ ᴜᴘᴀᴅʜʏᴀʏ</a></b>
<i>Full Stack Web Developer</i>

▪️ ʙᴄᴀ 1sᴛ sᴇᴍᴇsᴛᴇʀ sᴛᴜᴅᴇɴᴛ
▪️ sᴇʟғ-ᴛᴀᴜɢʜᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ
▪️ ғᴀʀɪᴅᴀʙᴀᴅ, ʜᴀʀʏᴀɴᴀ 🇮🇳
{line}
<b>◈ sᴋɪʟʟs</b>
ʀᴇᴀᴄᴛ · ɴᴏᴅᴇ.ᴊs · ᴇxᴘʀᴇss · ᴍᴏɴɢᴏᴅʙ
ᴍʏsǫʟ · ᴛᴀɪʟᴡɪɴᴅ · ᴛʏᴘᴇsᴄʀɪᴘᴛ · ɴᴇxᴛ.ᴊs

<b>◆ ᴘʀᴏᴊᴇᴄᴛs</b>
• <b>ᴄɪɴᴇᴠᴏᴏᴅ</b> — ᴍᴏᴠɪᴇ ᴅɪsᴄᴏᴠᴇʀʏ ᴀᴘᴘ
• <b>ᴛᴀʀᴀᴢᴜ</b> — ᴄᴀʟᴄᴜʟᴀᴛᴏʀ ᴜᴛɪʟɪᴛʏ
• <b>ᴄʟɪᴍᴀᴛᴇᴋ</b> — ᴡᴇᴀᴛʜᴇʀ ᴅᴀsʜʙᴏᴀʀᴅ
• <b>ᴛʜɪs ʙᴏᴛ</b> — ғɪʟᴇ sᴛᴏʀᴇ + ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ
{line}
<i>|| ॐ ɴᴀᴍᴀʜ sʜɪᴠᴀʏᴀ ||</i>

<b>ᴍᴀᴅᴇ ʙʏ ʜᴀʀsʜ ᴜᴘᴀᴅʜʏᴀʏ</b> ❤️"""

HELP_USER = """<b>◈ ʜᴏᴡ ᴛᴏ ᴜsᴇ</b>
{line}
1. ᴀᴅᴍɪɴ ᴋᴀ ʟɪɴᴋ ᴏᴘᴇɴ ᴋᴀʀᴏ
2. <b>sᴛᴀʀᴛ</b> ᴅᴀʙᴀᴏ
3. sᴀᴀʀɪ ғɪʟᴇs ᴀᴀ ᴊᴀᴇɴɢɪ
4. ᴛᴜʀᴀɴᴛ <b>ғᴏʀᴡᴀʀᴅ</b> ᴋᴀʀ ʟᴏ — {ad} ᴍᴇ ᴅᴇʟᴇᴛᴇ ʜᴏ ᴊᴀᴇɢɪ
{line}"""

HELP_ADMIN = """<b>⚙️ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>
{line}
<code>/batch</code> — ᴍᴜʟᴛɪ-ғɪʟᴇ ᴍᴏᴅᴇ ᴏɴ
<code>/done</code> — ʙᴀᴛᴄʜ ᴋʜᴀᴛᴀᴍ, ʟɪɴᴋ ʟᴏ
<code>/status</code> — ᴋɪᴛɴɪ ғɪʟᴇs ʜᴜɪ
<code>/cancel</code> — ʙᴀᴛᴄʜ ᴄᴀɴᴄᴇʟ
<code>/single</code> — ʜᴀʀ ғɪʟᴇ ᴋᴀ ᴀʟᴀɢ ʟɪɴᴋ
<code>/link</code> — sɪɴɢʟᴇ ғɪʟᴇ (ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ)
<code>/panel</code> — ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ
<code>/stats</code> — sᴛᴀᴛɪsᴛɪᴄs
<code>/broadcast</code> — sᴀʙ ᴋᴏ ᴍᴇssᴀɢᴇ (ʀᴇᴘʟʏ)
<code>/ban</code> · <code>/unban</code> <code>id</code>
<code>/addadmin</code> · <code>/rmadmin</code> <code>id</code>
<code>/autodel</code> <code>1800</code> — sᴇᴄᴏɴᴅs
<code>/backup</code> — ᴅʙ ғɪʟᴇ
<code>/revoke</code> <code>code</code> — ʟɪɴᴋ ʙᴀɴᴅ
{line}"""

ABOUT = """<b>◉ ᴀʙᴏᴜᴛ</b>
{line}
▪️ ɴᴀᴍᴇ: <b>{bot}</b>
▪️ ᴠᴇʀsɪᴏɴ: <code>{ver}</code>
▪️ ʟɪʙʀᴀʀʏ: <code>ᴘʏʀᴏɢʀᴀᴍ</code>
▪️ ᴅᴀᴛᴀʙᴀsᴇ: <code>sǫʟɪᴛᴇ · ʀᴀɪʟᴡᴀʏ ᴠᴏʟᴜᴍᴇ</code>
▪️ ʜᴏsᴛ: <code>ʀᴀɪʟᴡᴀʏ</code>
{line}
ᴅᴇᴠᴇʟᴏᴘᴇʀ: <b><a href="https://new-profotilo-flame.vercel.app">ʜᴀʀsʜ ᴜᴘᴀᴅʜʏᴀʏ</a></b>
{line}"""

NOT_ADMIN = "✘ ʏᴇʜ ᴄᴏᴍᴍᴀɴᴅ sɪʀғ ᴀᴅᴍɪɴ ᴋᴇ ʟɪʏᴇ ʜᴀɪ."
LINK_DEAD = "✘ ʏᴇʜ ʟɪɴᴋ ɪɴᴠᴀʟɪᴅ ʏᴀ ʀᴇᴠᴏᴋᴇ ʜᴏ ᴄʜᴜᴋᴀ ʜᴀɪ."
