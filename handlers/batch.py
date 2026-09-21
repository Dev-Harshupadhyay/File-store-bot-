"""
/batch flow — admin multiple videos bhejta hai -> /done -> ek link milta hai.
"""
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

import config
import database as db
from utils import keyboards as kb
from utils import texts as T
from utils.helpers import human_time, make_code

log = logging.getLogger("batch")

MEDIA = filters.document | filters.video | filters.audio | filters.photo | \
        filters.animation | filters.voice | filters.video_note | filters.sticker


def admin_only(_, __, m):
    return bool(m.from_user) and db.is_admin(m.from_user.id)


ADMIN = filters.create(admin_only)


@Client.on_message(filters.command("batch") & filters.private & ADMIN)
async def batch_start(client, message):
    uid = message.from_user.id
    client.batch_cache[uid] = []
    await message.reply(
        T.BATCH_START.format(line=T.LINE),
        reply_markup=kb.batch_collect_kb(0),
    )
    db.log(uid, "batch_start")


@Client.on_message(filters.command(["done", "finish"]) & filters.private & ADMIN)
async def batch_done(client, message):
    await _finish(client, message.from_user.id, message)


@Client.on_message(filters.command("cancel") & filters.private & ADMIN)
async def batch_cancel(client, message):
    client.batch_cache.pop(message.from_user.id, None)
    client.await_input.pop(message.from_user.id, None)
    await message.reply("✘ ʙᴀᴛᴄʜ ᴄᴀɴᴄᴇʟʟᴇᴅ.")


async def _finish(client, uid, message):
    ids = client.batch_cache.get(uid)
    if not ids:
        return await message.reply("✘ ᴋᴏɪ ғɪʟᴇ ɴᴀʜɪ ᴍɪʟɪ. ᴘᴇʜʟᴇ <code>/batch</code> ᴋᴀʀᴋᴇ ғɪʟᴇs ʙʜᴇᴊᴏ.")

    code = make_code(9)
    db.save_batch(code, uid, ids, title=f"Batch {len(ids)} files",
                  protect=1 if db.get_bool("protect") else 0)
    client.batch_cache.pop(uid, None)

    link = f"https://t.me/{client.username}?start={code}"
    ad = human_time(db.get_int("auto_delete", 1800)) if db.get_bool("auto_delete_on", True) else "ᴏғғ"

    await message.reply(
        T.BATCH_DONE.format(line=T.LINE, n=len(ids), code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code),
        disable_web_page_preview=True,
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


@Client.on_message(MEDIA & filters.private & ADMIN, group=1)
async def collect_media(client, message):
    """Batch mode ON -> collect. OFF -> instant single link."""
    uid = message.from_user.id

    # panel text input mode me media ignore
    if client.await_input.get(uid):
        return

    try:
        stored = await message.copy(config.DB_CHANNEL)
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        stored = await message.copy(config.DB_CHANNEL)
    except Exception as e:
        return await message.reply(f"✘ sᴛᴏʀᴇ ғᴀɪʟ: <code>{e}</code>")

    if uid in client.batch_cache:
        client.batch_cache[uid].append(stored.id)
        n = len(client.batch_cache[uid])
        if n % 3 == 0 or n == 1:
            try:
                await message.reply(T.BATCH_ADDED.format(n=n),
                                    reply_markup=kb.batch_collect_kb(n), quote=True)
            except Exception:
                pass
        return

    # single file -> turant link
    code = make_code(9)
    db.save_batch(code, uid, [stored.id], title="Single file",
                  protect=1 if db.get_bool("protect") else 0)
    link = f"https://t.me/{client.username}?start={code}"
    ad = human_time(db.get_int("auto_delete", 1800))
    await message.reply(
        T.BATCH_DONE.format(line=T.LINE, n=1, code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code), quote=True, disable_web_page_preview=True,
    )


@Client.on_message(filters.command("link") & filters.private & ADMIN)
async def single_link(client, message):
    if not message.reply_to_message:
        return await message.reply("↩️ ᴋɪsɪ ғɪʟᴇ ᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ <code>/link</code> ʟɪᴋʜᴏ.")
    stored = await message.reply_to_message.copy(config.DB_CHANNEL)
    code = make_code(9)
    db.save_batch(code, message.from_user.id, [stored.id], title="Single file")
    link = f"https://t.me/{client.username}?start={code}"
    ad = human_time(db.get_int("auto_delete", 1800))
    await message.reply(
        T.BATCH_DONE.format(line=T.LINE, n=1, code=code, link=link, ad=ad),
        reply_markup=kb.link_kb(link, code), disable_web_page_preview=True,
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
