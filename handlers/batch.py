"""
/batch  — silent bulk collect, /done par direct link
/single — har file ka apna alag link
"""
import asyncio
import logging
import time

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

import config
import database as db
from utils import keyboards as kb
from utils import texts as T
from utils import fsub
from utils.helpers import human_time, make_code, no_preview

log = logging.getLogger("batch")

MEDIA = (filters.document | filters.video | filters.audio | filters.photo |
         filters.animation | filters.voice | filters.video_note | filters.sticker)


def admin_only(_, __, m):
    return bool(m.from_user) and db.is_admin(m.from_user.id)


ADMIN = filters.create(admin_only)


# ───────────────────────────── MODE COMMANDS ─────────────────────────────
@Client.on_message(filters.command("batch") & filters.private)
async def batch_start(client, message):
    """Batch mode — sirf admin. Normal user ko /single suggest karo."""
    uid = message.from_user.id
    if not db.is_admin(uid):
        return await message.reply(T.BATCH_LOCKED.format(line=T.LINE))
    client.batch_cache[uid] = []
    client.batch_mode = getattr(client, "batch_mode", {})
    client.batch_mode[uid] = "batch"

    await message.reply(T.BATCH_START.format(line=T.LINE), **no_preview())
    db.log(uid, "batch_start")


@Client.on_message(filters.command("single") & filters.private)
async def single_mode(client, message):
    """Single mode — har file ka turant alag link. Sabke liye khula."""
    uid = message.from_user.id
    if db.is_banned(uid):
        return
    if db.get_bool("maintenance") and not db.is_admin(uid):
        return await message.reply(T.MAINT_MSG.format(line=T.LINE))
    if await fsub.guard(client, message):
        return
    client.batch_cache.pop(uid, None)
    client.batch_mode = getattr(client, "batch_mode", {})
    client.batch_mode[uid] = "single"

    await message.reply(T.SINGLE_MODE.format(line=T.LINE), **no_preview())
    db.log(uid, "single_mode")


@Client.on_message(filters.command(["done", "finish"]) & filters.private & ADMIN)
async def batch_done(client, message):
    await _finish(client, message.from_user.id, message)


@Client.on_message(filters.command("cancel") & filters.private & ADMIN)
async def batch_cancel(client, message):
    uid = message.from_user.id
    n = len(client.batch_cache.pop(uid, []))
    client.await_input.pop(uid, None)
    if hasattr(client, "batch_mode"):
        client.batch_mode.pop(uid, None)
    await message.reply(f"✘ ʙᴀᴛᴄʜ ᴄᴀɴᴄᴇʟʟᴇᴅ · <code>{n}</code> ғɪʟᴇs ᴅɪsᴄᴀʀᴅ.")


# ───────────────────────────── LINK BANAO ─────────────────────────────
async def _make_link(client, uid, msg_ids, title=""):
    """Batch DB me save karke link return karo."""
    code = make_code(9)
    db.save_batch(code, uid, msg_ids, title=title or f"Batch {len(msg_ids)} files",
                  protect=1 if db.get_bool("protect") else 0)
    return code, f"https://t.me/{client.username}?start={code}"


async def _finish(client, uid, message):
    """/done — direct link, koi button spam nahi."""
    ids = client.batch_cache.get(uid)
    if not ids:
        return await message.reply(
            f"✘ ᴋᴏɪ ғɪʟᴇ ɴᴀʜɪ ᴍɪʟɪ.\n"
            f"ᴘᴇʜʟᴇ <code>/batch</code> ᴋᴀʀᴏ, ғɪʀ ғɪʟᴇs ʙʜᴇᴊᴏ."
        )

    code, link = await _make_link(client, uid, ids)
    client.batch_cache.pop(uid, None)
    if hasattr(client, "batch_mode"):
        client.batch_mode.pop(uid, None)

    ad = human_time(db.get_int("auto_delete", 1800)) \
        if db.get_bool("auto_delete_on", True) else "ᴏғғ"

    await message.reply(
        T.BATCH_DONE.format(line=T.LINE, n=len(ids), code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code),
        **no_preview(),
    )
    db.log(uid, "batch_done", f"code={code} n={len(ids)}")

    try:
        await client.send_message(
            config.LOG_CHANNEL,
            f"◆ <b>ɴᴇᴡ ʙᴀᴛᴄʜ</b>\nʙʏ: <code>{uid}</code>\n"
            f"ғɪʟᴇs: <code>{len(ids)}</code>\nᴄᴏᴅᴇ: <code>{code}</code>",
        )
    except Exception:
        pass


# ───────────────────────────── MEDIA COLLECT ─────────────────────────────
@Client.on_message(MEDIA & filters.private, group=1)
async def collect_media(client, message):
    """
    Admin  + batch mode -> silently collect (koi reply nahi, fast)
    Admin  + single     -> turant link
    Normal user         -> turant link (single only)
    """
    uid = message.from_user.id

    if db.is_banned(uid):
        return
    if db.get_bool("maintenance") and not db.is_admin(uid):
        return await message.reply(T.MAINT_MSG.format(line=T.LINE))

    # panel text-input chal raha hai to media ignore
    if client.await_input.get(uid):
        return

    # ⚑ force sub — bina join kiye link nahi milega
    if await fsub.guard(client, message):
        return

    # non-admin ke liye batch mode hai hi nahi
    in_batch = db.is_admin(uid) and uid in client.batch_cache

    # ── DB channel me store ──
    try:
        stored = await message.copy(config.DB_CHANNEL)
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        try:
            stored = await message.copy(config.DB_CHANNEL)
        except Exception as err:
            if not in_batch:
                await message.reply(f"✘ sᴛᴏʀᴇ ғᴀɪʟ: <code>{err}</code>")
            return
    except Exception as e:
        log.warning("store fail: %s", e)
        if not in_batch:
            await message.reply(f"✘ sᴛᴏʀᴇ ғᴀɪʟ: <code>{e}</code>")
        return

    # ── BATCH MODE: chup-chaap collect ──
    if in_batch:
        client.batch_cache[uid].append(stored.id)
        return                      # ← koi reply nahi, isliye tez

    # ── SINGLE MODE: turant link ──
    code, link = await _make_link(client, uid, [stored.id], "Single file")
    ad = human_time(db.get_int("auto_delete", 1800))
    await message.reply(
        T.SINGLE_DONE.format(line=T.LINE, code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code),
        **no_preview(),
    )


@Client.on_message(filters.command("status") & filters.private & ADMIN)
async def batch_status(client, message):
    """Abhi kitni files collect hui hain."""
    uid = message.from_user.id
    ids = client.batch_cache.get(uid)
    if ids is None:
        return await message.reply(
            f"▪️ ʙᴀᴛᴄʜ ᴍᴏᴅᴇ <b>ᴏғғ</b> ʜᴀɪ.\n<code>/batch</code> sᴇ ᴏɴ ᴋᴀʀᴏ."
        )
    await message.reply(
        f"<b>◆ ʙᴀᴛᴄʜ sᴛᴀᴛᴜs</b>\n{T.LINE}\n"
        f"▪️ ᴄᴏʟʟᴇᴄᴛᴇᴅ: <code>{len(ids)}</code> ғɪʟᴇs\n"
        f"{T.LINE}\n<code>/done</code> — ʟɪɴᴋ ʟᴏ · <code>/cancel</code> — ᴄᴀɴᴄᴇʟ"
    )


# ───────────────────────────── SINGLE FILE (reply) ─────────────────────────────
@Client.on_message(filters.command("link") & filters.private)
async def single_link(client, message):
    if db.is_banned(message.from_user.id):
        return
    if await fsub.guard(client, message):
        return
    if not message.reply_to_message:
        return await message.reply("↩️ ᴋɪsɪ ғɪʟᴇ ᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ <code>/link</code> ʟɪᴋʜᴏ.")
    try:
        stored = await message.reply_to_message.copy(config.DB_CHANNEL)
    except Exception as e:
        return await message.reply(f"✘ sᴛᴏʀᴇ ғᴀɪʟ: <code>{e}</code>")

    code, link = await _make_link(client, message.from_user.id, [stored.id], "Single file")
    ad = human_time(db.get_int("auto_delete", 1800))
    await message.reply(
        T.SINGLE_DONE.format(line=T.LINE, code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code),
        **no_preview(),
    )


@Client.on_message(filters.command("revoke") & filters.private & ADMIN)
async def revoke_cmd(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("ᴜsᴀɢᴇ: <code>/revoke &lt;code&gt;</code>")
    code = parts[1].strip()
    if not db.get_batch(code):
        return await message.reply(T.LINK_DEAD)
    db.revoke_batch(code)
    db.log(message.from_user.id, "revoke", code)
    await message.reply(f"✓ ʟɪɴᴋ <code>{code}</code> ʀᴇᴠᴏᴋᴇᴅ.")
