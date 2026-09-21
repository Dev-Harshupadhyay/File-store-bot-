"""
Admin commands — /panel /stats /ban /broadcast /addadmin /autodel /backup ...
"""
import asyncio
import io
import logging
import os
import time

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked

import config
import database as db
from utils import keyboards as kb
from utils import texts as T
from utils.helpers import human_size, human_time, parse_target, uptime_since

log = logging.getLogger("admin")


def _is_admin(_, __, m):
    return bool(m.from_user) and db.is_admin(m.from_user.id)


def _is_owner(_, __, m):
    return bool(m.from_user) and db.is_owner(m.from_user.id)


ADMIN = filters.create(_is_admin)
OWNER = filters.create(_is_owner)


def panel_text(client):
    ad = human_time(db.get_int("auto_delete", 1800)) if db.get_bool("auto_delete_on", True) else "ᴏғғ"
    return T.PANEL.format(
        line=T.LINE, users=db.count_users(), banned=db.count_banned(),
        batches=db.count_batches(), files=db.count_files(), ad=ad,
        up=uptime_since(client.uptime),
    )


@Client.on_message(filters.command(["panel", "admin", "settings"]) & filters.private & ADMIN)
async def panel_cmd(client, message):
    await message.reply(panel_text(client), reply_markup=kb.admin_panel(message.from_user.id))


@Client.on_message(filters.command("stats") & filters.private & ADMIN)
async def stats_cmd(client, message):
    await message.reply(stats_text(client), reply_markup=kb.stats_kb())


def stats_text(client):
    week = int(time.time()) - 7 * 86400
    day = int(time.time()) - 86400
    return (
        f"<b>▪️ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs</b>\n{T.LINE}\n"
        f"◉ ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{db.count_users()}</code>\n"
        f"✘ ʙᴀɴɴᴇᴅ: <code>{db.count_banned()}</code>\n"
        f"✦ ɴᴇᴡ (24ʜ): <code>{db.new_users_since(day)}</code>\n"
        f"✦ ɴᴇᴡ (7ᴅ): <code>{db.new_users_since(week)}</code>\n{T.LINE}\n"
        f"◆ ʙᴀᴛᴄʜᴇs: <code>{db.count_batches()}</code>\n"
        f"▪️ ғɪʟᴇs sᴛᴏʀᴇᴅ: <code>{db.count_files()}</code>\n"
        f"▸ ᴛᴏᴛᴀʟ ᴏᴘᴇɴs: <code>{db.total_opens()}</code>\n{T.LINE}\n"
        f"❖ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: <code>{human_time(db.get_int('auto_delete',1800))}</code>\n"
        f"✿ ᴘʀᴏᴛᴇᴄᴛ: <code>{'ᴏɴ' if db.get_bool('protect') else 'ᴏғғ'}</code>\n"
        f"⚑ ғᴏʀᴄᴇ sᴜʙ: <code>{'ᴏɴ' if db.get_bool('force_sub') else 'ᴏғғ'}</code>\n"
        f"⚠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ: <code>{'ᴏɴ' if db.get_bool('maintenance') else 'ᴏғғ'}</code>\n{T.LINE}\n"
        f"💾 ᴅʙ sɪᴢᴇ: <code>{human_size(db.db_size())}</code>\n"
        f"📁 sᴛᴏʀᴀɢᴇ: <code>{config.DATA_DIR}</code>\n"
        f"⏱ ᴜᴘᴛɪᴍᴇ: <code>{uptime_since(client.uptime)}</code>"
    )


# ───────────────────────────── BAN / UNBAN ─────────────────────────────
@Client.on_message(filters.command("ban") & filters.private & ADMIN)
async def ban_cmd(client, message):
    uid, reason = parse_target(message.text, message)
    if not uid:
        return await message.reply("ᴜsᴀɢᴇ: <code>/ban &lt;user_id&gt; [reason]</code>")
    if db.is_admin(uid):
        return await message.reply("✘ ᴀᴅᴍɪɴ ᴋᴏ ʙᴀɴ ɴᴀʜɪ ᴋᴀʀ sᴀᴋᴛᴇ.")
    db.ban_user(uid, reason)
    db.log(message.from_user.id, "ban", f"{uid} · {reason}")
    await message.reply(f"🚫 <code>{uid}</code> ʙᴀɴɴᴇᴅ.\nʀᴇᴀsᴏɴ: <code>{reason}</code>")
    try:
        await client.send_message(uid, T.BANNED_MSG.format(line=T.LINE, reason=reason))
    except Exception:
        pass


@Client.on_message(filters.command("unban") & filters.private & ADMIN)
async def unban_cmd(client, message):
    uid, _ = parse_target(message.text, message)
    if not uid:
        return await message.reply("ᴜsᴀɢᴇ: <code>/unban &lt;user_id&gt;</code>")
    db.unban_user(uid)
    db.log(message.from_user.id, "unban", str(uid))
    await message.reply(f"✓ <code>{uid}</code> ᴜɴʙᴀɴɴᴇᴅ.")


@Client.on_message(filters.command("banned") & filters.private & ADMIN)
async def banned_cmd(client, message):
    rows = db.banned_list()
    if not rows:
        return await message.reply("✓ ᴋᴏɪ ʙᴀɴɴᴇᴅ ᴜsᴇʀ ɴᴀʜɪ.")
    txt = f"<b>✘ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ({len(rows)})</b>\n{T.LINE}\n"
    for r in rows[:40]:
        txt += f"• <code>{r['user_id']}</code> — {r['ban_reason'] or '—'}\n"
    await message.reply(txt)


# ───────────────────────────── ADMINS ─────────────────────────────
@Client.on_message(filters.command("addadmin") & filters.private & OWNER)
async def addadmin_cmd(client, message):
    uid, _ = parse_target(message.text, message)
    if not uid:
        return await message.reply("ᴜsᴀɢᴇ: <code>/addadmin &lt;user_id&gt;</code>")
    db.add_admin(uid, message.from_user.id)
    db.log(message.from_user.id, "add_admin", str(uid))
    await message.reply(f"★ <code>{uid}</code> ᴀʙ ᴀᴅᴍɪɴ ʜᴀɪ.")
    try:
        await client.send_message(uid, "★ ᴛᴜᴍʜᴇ <b>ᴀᴅᴍɪɴ</b> ʙᴀɴᴀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ.\n<code>/panel</code> ᴛʀʏ ᴋᴀʀᴏ.")
    except Exception:
        pass


@Client.on_message(filters.command("rmadmin") & filters.private & OWNER)
async def rmadmin_cmd(client, message):
    uid, _ = parse_target(message.text, message)
    if not uid:
        return await message.reply("ᴜsᴀɢᴇ: <code>/rmadmin &lt;user_id&gt;</code>")
    if uid == config.OWNER_ID:
        return await message.reply("✘ ᴏᴡɴᴇʀ ᴋᴏ ʜᴀᴛᴀ ɴᴀʜɪ sᴀᴋᴛᴇ.")
    db.rm_admin(uid)
    db.log(message.from_user.id, "rm_admin", str(uid))
    await message.reply(f"✓ <code>{uid}</code> ᴀᴅᴍɪɴ sᴇ ʜᴀᴛᴀ ᴅɪʏᴀ.")


@Client.on_message(filters.command("admins") & filters.private & ADMIN)
async def admins_cmd(client, message):
    ids = db.admin_ids()
    txt = f"<b>◇ ᴀᴅᴍɪɴs ({len(ids)})</b>\n{T.LINE}\n"
    for uid in ids:
        tag = " ★ ᴏᴡɴᴇʀ" if uid == config.OWNER_ID else ""
        txt += f"• <code>{uid}</code>{tag}\n"
    await message.reply(txt, reply_markup=kb.admins_kb())


# ───────────────────────────── SETTINGS ─────────────────────────────
@Client.on_message(filters.command("autodel") & filters.private & ADMIN)
async def autodel_cmd(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        cur = db.get_int("auto_delete", 1800)
        return await message.reply(
            f"❖ ᴀʙʜɪ: <code>{human_time(cur)}</code>\n"
            f"ᴜsᴀɢᴇ: <code>/autodel 1800</code> (sᴇᴄᴏɴᴅs, 0 = ᴏғғ)",
            reply_markup=kb.autodel_kb())
    val = int(parts[1].strip())
    db.set("auto_delete", val)
    db.set("auto_delete_on", "1" if val > 0 else "0")
    db.log(message.from_user.id, "autodel", str(val))
    await message.reply(f"✓ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: <code>{human_time(val)}</code>")


@Client.on_message(filters.command("backup") & filters.private & OWNER)
async def backup_cmd(client, message):
    m = await message.reply("⏳ ʙᴀᴄᴋᴜᴘ ʙᴀɴᴀ ʀᴀʜᴀ ʜᴏᴏɴ...")
    try:
        await message.reply_document(
            config.DB_PATH,
            caption=f"💾 <b>ᴅᴀᴛᴀʙᴀsᴇ ʙᴀᴄᴋᴜᴘ</b>\n"
                    f"◉ ᴜsᴇʀs: <code>{db.count_users()}</code>\n"
                    f"◆ ʙᴀᴛᴄʜᴇs: <code>{db.count_batches()}</code>\n"
                    f"📦 sɪᴢᴇ: <code>{human_size(db.db_size())}</code>",
            file_name=f"filestore-backup-{int(time.time())}.db",
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"✘ ʙᴀᴄᴋᴜᴘ ғᴀɪʟ: <code>{e}</code>")


# ───────────────────────────── BROADCAST ─────────────────────────────
@Client.on_message(filters.command(["broadcast", "bc"]) & filters.private & ADMIN)
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply("↩️ ᴊᴏ ᴍᴇssᴀɢᴇ ʙʜᴇᴊɴᴀ ʜᴀɪ ᴜsᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ <code>/broadcast</code> ʟɪᴋʜᴏ.")
    await do_broadcast(client, message, message.reply_to_message)


async def do_broadcast(client, message, src):
    users = db.all_users()
    total = len(users)
    status = await message.reply(f"⚑ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛ · <code>{total}</code> ᴜsᴇʀs")
    ok = fail = blocked = 0
    t0 = time.time()

    for i, uid in enumerate(users, 1):
        try:
            await src.copy(uid)
            ok += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            try:
                await src.copy(uid)
                ok += 1
            except Exception:
                fail += 1
        except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
            blocked += 1
        except Exception:
            fail += 1

        if i % 25 == 0:
            try:
                await status.edit(
                    f"⚑ <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ</b>\n{T.LINE}\n"
                    f"▸ ᴅᴏɴᴇ: <code>{i}/{total}</code>\n"
                    f"✓ sᴇɴᴛ: <code>{ok}</code> · ✘ ғᴀɪʟ: <code>{fail}</code>\n"
                    f"🚫 ʙʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>")
            except Exception:
                pass
        await asyncio.sleep(0.06)

    db.log(message.from_user.id, "broadcast", f"ok={ok} fail={fail}")
    await status.edit(
        f"<b>✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ</b>\n{T.LINE}\n"
        f"◉ ᴛᴏᴛᴀʟ: <code>{total}</code>\n"
        f"✓ sᴇɴᴛ: <code>{ok}</code>\n"
        f"🚫 ʙʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>\n"
        f"✘ ғᴀɪʟᴇᴅ: <code>{fail}</code>\n"
        f"⏱ ᴛɪᴍᴇ: <code>{human_time(time.time()-t0)}</code>")


# ───────────────────────────── FORCE SUB ─────────────────────────────
@Client.on_message(filters.command("addfsub") & filters.private & ADMIN)
async def addfsub_cmd(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("ᴜsᴀɢᴇ: <code>/addfsub -100xxxxxxxxxx</code>\n"
                                   "(ʙᴏᴛ ᴋᴏ ᴜs ᴄʜᴀɴɴᴇʟ ᴍᴇ ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ)")
    try:
        cid = int(parts[1].strip())
        chat = await client.get_chat(cid)
        invite = chat.invite_link or await client.export_chat_invite_link(cid)
        db.add_fsub(cid, chat.title, invite)
        db.set("force_sub", "1")
        await message.reply(f"✓ ғᴏʀᴄᴇ sᴜʙ ᴀᴅᴅᴇᴅ: <b>{chat.title}</b>")
    except Exception as e:
        await message.reply(f"✘ ᴇʀʀᴏʀ: <code>{e}</code>")


@Client.on_message(filters.command("delfsub") & filters.private & ADMIN)
async def delfsub_cmd(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("ᴜsᴀɢᴇ: <code>/delfsub -100xxxxxxxxxx</code>")
    db.rm_fsub(int(parts[1].strip()))
    await message.reply("✓ ʀᴇᴍᴏᴠᴇᴅ.")


# ───────────────────────────── MISC ─────────────────────────────
@Client.on_message(filters.command("users") & filters.private & ADMIN)
async def users_cmd(client, message):
    rows = db.recent_users(15)
    txt = f"<b>◉ ʀᴇᴄᴇɴᴛ ᴜsᴇʀs</b> · ᴛᴏᴛᴀʟ <code>{db.count_users()}</code>\n{T.LINE}\n"
    for r in rows:
        txt += f"• <code>{r['user_id']}</code> — {(r['name'] or '')[:20]}\n"
    await message.reply(txt, reply_markup=kb.users_kb())


@Client.on_message(filters.command("id") & filters.private)
async def id_cmd(client, message):
    u = message.from_user
    txt = f"◉ ʏᴏᴜʀ ɪᴅ: <code>{u.id}</code>"
    if message.reply_to_message and message.reply_to_message.from_user:
        txt += f"\n◉ ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ: <code>{message.reply_to_message.from_user.id}</code>"
    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        txt += f"\n◆ ᴄʜᴀɴɴᴇʟ ɪᴅ: <code>{message.reply_to_message.forward_from_chat.id}</code>"
    await message.reply(txt)


@Client.on_message(filters.command("restart") & filters.private & OWNER)
async def restart_cmd(client, message):
    await message.reply("↻ ʀᴇsᴛᴀʀᴛɪɴɢ...")
    os._exit(0)
