"""
Saare inline button callbacks — panel ka dimaag.
"""
import logging
import os
import platform
import time

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardMarkup as IKM

import config
import database as db
from handlers.admin import do_broadcast, panel_text, stats_text
from utils import keyboards as kb
from utils.buttons import blue, green, grey, red
from utils import texts as T
from utils.helpers import ago, human_size, human_time, uptime_since

log = logging.getLogger("cb")


async def _guard(q: CallbackQuery):
    if not db.is_admin(q.from_user.id):
        await q.answer("✘ sɪʀғ ᴀᴅᴍɪɴ ᴋᴇ ʟɪʏᴇ!", show_alert=True)
        return False
    return True


async def _edit(q, text, markup):
    try:
        if q.message.photo:
            await q.message.edit_caption(text, reply_markup=markup)
        else:
            await q.message.edit_text(text, reply_markup=markup,
                                      disable_web_page_preview=True)
    except Exception as e:
        log.debug("edit skip: %s", e)


# ───────────────────────────── USER SIDE ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^u:"))
async def user_cb(client, q: CallbackQuery):
    action = q.data.split(":", 1)[1]
    ad = human_time(db.get_int("auto_delete", 1800))
    if action == "help":
        await _edit(q, T.HELP_USER.format(line=T.LINE, ad=ad),
                    IKM([[grey("« ʙᴀᴄᴋ", callback_data="u:home")]]))
    elif action == "about":
        await _edit(q, T.ABOUT.format(line=T.LINE, bot=config.BOT_NAME,
                                      ver=config.BOT_VERSION),
                    IKM([[grey("« ʙᴀᴄᴋ", callback_data="u:home")]]))
    elif action == "home":
        is_adm = db.is_admin(q.from_user.id)
        if is_adm:
            txt = T.START_ADMIN.format(bot=config.BOT_NAME, ver=config.BOT_VERSION,
                                       line=T.LINE, users=db.count_users(),
                                       batches=db.count_batches(), files=db.count_files())
        else:
            txt = T.START_USER.format(bot=config.BOT_NAME, line=T.LINE,
                                      mention=q.from_user.mention, ad=ad)
        await _edit(q, txt, kb.start_kb(is_adm))
    await q.answer()


# ───────────────────────────── BATCH BUTTONS ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^batch:"))
async def batch_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    action = q.data.split(":", 1)[1]
    uid = q.from_user.id

    if action == "done":
        from handlers.batch import _finish
        await q.answer("ʟɪɴᴋ ʙᴀɴ ʀᴀʜᴀ ʜᴀɪ...")
        await _finish(client, uid, q.message)
    elif action == "clear":
        client.batch_cache[uid] = []
        await q.answer("↺ ᴄʟᴇᴀʀᴇᴅ", show_alert=False)
        await _edit(q, T.BATCH_START.format(line=T.LINE), kb.batch_collect_kb(0))
    elif action == "cancel":
        client.batch_cache.pop(uid, None)
        await q.answer("✘ ᴄᴀɴᴄᴇʟʟᴇᴅ")
        await _edit(q, "✘ ʙᴀᴛᴄʜ ᴄᴀɴᴄᴇʟʟᴇᴅ.", None)


@Client.on_callback_query(filters.regex(r"^lnk:"))
async def link_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    _, act, code = q.data.split(":", 2)
    batch = db.get_batch(code)
    if not batch:
        return await q.answer("✘ ɴᴏᴛ ғᴏᴜɴᴅ", show_alert=True)
    if act == "rv":
        db.revoke_batch(code, 0 if batch["revoked"] else 1)
        state = "ᴀᴄᴛɪᴠᴇ" if batch["revoked"] else "ʀᴇᴠᴏᴋᴇᴅ"
        await q.answer(f"ʟɪɴᴋ {state}", show_alert=True)
    elif act == "in":
        await q.answer(
            f"ᴄᴏᴅᴇ: {code}\nғɪʟᴇs: {batch['count']}\nᴏᴘᴇɴs: {batch['opens']}\n"
            f"sᴛᴀᴛᴜs: {'revoked' if batch['revoked'] else 'active'}",
            show_alert=True)


# ───────────────────────────── TOGGLES ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^tg:"))
async def toggle_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    key = q.data.split(":", 1)[1]
    default = True if key == "auto_delete_on" else False
    new = db.toggle(key, default)
    db.log(q.from_user.id, "toggle", f"{key}={new}")
    await q.answer(f"{key} → {'ON' if new else 'OFF'}")
    await _edit(q, panel_text(client), kb.admin_panel(q.from_user.id))


@Client.on_callback_query(filters.regex(r"^set:"))
async def set_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    _, key, val = q.data.split(":", 2)
    db.set(key, val)
    if key == "auto_delete":
        db.set("auto_delete_on", "1" if int(val) > 0 else "0")
        await q.answer(f"✓ {human_time(int(val))}")
        return await _edit(q, autodel_text(), kb.autodel_kb())
    await q.answer("✓ sᴀᴠᴇᴅ")


def autodel_text():
    cur = db.get_int("auto_delete", 1800)
    on = db.get_bool("auto_delete_on", True)
    return (f"<b>❖ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n{T.LINE}\n"
            f"ᴀʙʜɪ: <code>{human_time(cur) if on else 'ᴏғғ'}</code>\n\n"
            f"ғɪʟᴇs ɪᴛɴᴇ ᴛɪᴍᴇ ʙᴀᴀᴅ ᴜsᴇʀ ᴋᴇ ᴄʜᴀᴛ sᴇ ʜᴀᴛ ᴊᴀᴀᴛɪ ʜᴀɪɴ.\n"
            f"ɴᴇᴇᴄʜᴇ sᴇ ᴄʜᴜɴᴏ ʏᴀ <code>/autodel 900</code> ʟɪᴋʜᴏ.\n{T.LINE}")


# ───────────────────────────── ADMIN REMOVE ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^adm:rm:"))
async def adm_rm_cb(client, q: CallbackQuery):
    if not db.is_owner(q.from_user.id):
        return await q.answer("✘ sɪʀғ ᴏᴡɴᴇʀ", show_alert=True)
    uid = int(q.data.split(":")[2])
    db.rm_admin(uid)
    await q.answer(f"✓ {uid} removed")
    await _edit(q, admins_text(), kb.admins_kb())


def admins_text():
    ids = db.admin_ids()
    txt = f"<b>◇ ᴀᴅᴍɪɴs ({len(ids)})</b>\n{T.LINE}\n"
    for uid in ids:
        tag = " ★ ᴏᴡɴᴇʀ" if uid == config.OWNER_ID else ""
        txt += f"• <code>{uid}</code>{tag}\n"
    txt += f"{T.LINE}\n<code>/addadmin id</code> sᴇ ɴᴇᴡ ᴀᴅᴍɪɴ ᴀᴅᴅ ᴋᴀʀᴏ"
    return txt


@Client.on_callback_query(filters.regex(r"^fsub:rm:"))
async def fsub_rm_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    db.rm_fsub(int(q.data.split(":")[2]))
    await q.answer("✓ removed")
    await _edit(q, fsub_text(), kb.fsub_kb())


def fsub_text():
    rows = db.fsub_list()
    txt = (f"<b>⚑ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ</b>\n{T.LINE}\n"
           f"sᴛᴀᴛᴜs: <code>{'ᴏɴ' if db.get_bool('force_sub') else 'ᴏғғ'}</code>\n"
           f"ᴄʜᴀɴɴᴇʟs: <code>{len(rows)}</code>\n{T.LINE}\n")
    for r in rows:
        mode = (r["mode"] if "mode" in r.keys() else "join") or "join"
        tag = " ⏳ʀᴇǫ" if mode == "request" else ""
        txt += f"• <b>{r['title']}</b>{tag}\n  <code>{r['chat_id']}</code>\n"
    if not rows:
        txt += "<i>ᴀʙʜɪ ᴋᴏɪ ᴄʜᴀɴɴᴇʟ ɴᴀʜɪ</i>\n"
    txt += (f"{T.LINE}\n"
            f"<code>/addfsub -100xxxx</code> — ᴀᴅᴅ\n"
            f"<code>/addfsub @username</code> — ᴘᴜʙʟɪᴄ\n"
            f"<code>/addfsub -100xxxx request</code> — ʀᴇǫᴜᴇsᴛ ᴍᴏᴅᴇ\n"
            f"<code>/delfsub -100xxxx</code> — ʀᴇᴍᴏᴠᴇ\n\n"
            f"<i>ʙᴏᴛ ᴋᴏ ʜᴀʀ ᴄʜᴀɴɴᴇʟ ᴍᴇ ᴀᴅᴍɪɴ ʙᴀɴᴀɴᴀ ᴢᴀʀᴏᴏʀɪ ʜᴀɪ</i>")
    return txt


# ───────────────────────────── MAIN PANEL ─────────────────────────────
@Client.on_callback_query(filters.regex(r"^ap:"))
async def panel_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    action = q.data.split(":", 1)[1]
    uid = q.from_user.id

    if action == "home":
        await _edit(q, panel_text(client), kb.admin_panel(uid))

    elif action == "close":
        try:
            await q.message.delete()
        except Exception:
            pass

    elif action == "stats":
        await _edit(q, stats_text(client), kb.stats_kb())

    elif action == "system":
        import shutil
        du = shutil.disk_usage(config.DATA_DIR)
        txt = (f"<b>✦ sʏsᴛᴇᴍ ɪɴғᴏ</b>\n{T.LINE}\n"
               f"🐍 ᴘʏᴛʜᴏɴ: <code>{platform.python_version()}</code>\n"
               f"💻 ᴏs: <code>{platform.system()} {platform.release()}</code>\n"
               f"📁 ᴅᴀᴛᴀ ᴅɪʀ: <code>{config.DATA_DIR}</code>\n"
               f"💾 ᴅʙ: <code>{human_size(db.db_size())}</code>\n"
               f"🗄 ᴅɪsᴋ ғʀᴇᴇ: <code>{human_size(du.free)}</code> / {human_size(du.total)}\n"
               f"⏱ ᴜᴘᴛɪᴍᴇ: <code>{uptime_since(client.uptime)}</code>\n{T.LINE}")
        await _edit(q, txt, kb.back())

    elif action == "users":
        rows = db.recent_users(15)
        txt = (f"<b>◉ ᴜsᴇʀs</b>\n{T.LINE}\n"
               f"ᴛᴏᴛᴀʟ: <code>{db.count_users()}</code> · "
               f"ʙᴀɴɴᴇᴅ: <code>{db.count_banned()}</code>\n{T.LINE}\n")
        for r in rows:
            txt += f"• <code>{r['user_id']}</code> {(r['name'] or '')[:18]} · {ago(r['joined'])}\n"
        await _edit(q, txt, kb.users_kb())

    elif action == "banned":
        rows = db.banned_list()
        txt = f"<b>✘ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ({len(rows)})</b>\n{T.LINE}\n"
        for r in rows[:30]:
            txt += f"• <code>{r['user_id']}</code> — {r['ban_reason'] or '—'}\n"
        if not rows:
            txt += "ᴋᴏɪ ɴᴀʜɪ ✓"
        await _edit(q, txt, kb.users_kb())

    elif action == "export":
        ids = db.all_users(only_active=False)
        path = os.path.join(config.DATA_DIR, "users.txt")
        with open(path, "w") as f:
            f.write("\n".join(map(str, ids)))
        await q.message.reply_document(path, caption=f"◉ <code>{len(ids)}</code> ᴜsᴇʀ ɪᴅs")
        await q.answer("✓ exported")

    elif action in ("files", "batches"):
        rows = db.recent_batches(12)
        txt = (f"<b>◆ ʀᴇᴄᴇɴᴛ ʙᴀᴛᴄʜᴇs</b>\n{T.LINE}\n"
               f"ᴛᴏᴛᴀʟ: <code>{db.count_batches()}</code> · "
               f"ғɪʟᴇs: <code>{db.count_files()}</code>\n{T.LINE}\n")
        for r in rows:
            mark = "🚫" if r["revoked"] else "✓"
            txt += (f"{mark} <code>{r['code']}</code> · {r['count']}ғ · "
                    f"{r['opens']} ᴏᴘᴇɴs · {ago(r['created'])}\n")
        if not rows:
            txt += "ᴀʙʜɪ ᴋᴏɪ ʙᴀᴛᴄʜ ɴᴀʜɪ."
        await _edit(q, txt, kb.files_kb())

    elif action == "topfiles":
        rows = db.top_batches(12)
        txt = f"<b>★ ᴛᴏᴘ ᴏᴘᴇɴᴇᴅ</b>\n{T.LINE}\n"
        for i, r in enumerate(rows, 1):
            txt += f"{i}. <code>{r['code']}</code> — {r['opens']} ᴏᴘᴇɴs ({r['count']}ғ)\n"
        await _edit(q, txt, kb.files_kb())

    elif action == "autodel":
        await _edit(q, autodel_text(), kb.autodel_kb())

    elif action == "protect":
        new = db.toggle("protect")
        await q.answer(f"ᴘʀᴏᴛᴇᴄᴛ {'ON' if new else 'OFF'}", show_alert=True)
        await _edit(q, panel_text(client), kb.admin_panel(uid))

    elif action == "fsub":
        await _edit(q, fsub_text(), kb.fsub_kb())

    elif action == "admins":
        await _edit(q, admins_text(), kb.admins_kb())

    elif action == "addadmin":
        client.await_input[uid] = "addadmin"
        await _edit(q, f"<b>⊕ ᴀᴅᴅ ᴀᴅᴍɪɴ</b>\n{T.LINE}\n"
                       f"ᴀʙ ᴜsᴇʀ ɪᴅ ʙʜᴇᴊᴏ (sɪʀғ ɴᴜᴍʙᴇʀ).\n"
                       f"ᴄᴀɴᴄᴇʟ ᴋᴇ ʟɪʏᴇ <code>/cancel</code>\n{T.LINE}", kb.back())

    elif action == "ban":
        client.await_input[uid] = "ban"
        await _edit(q, f"<b>✘ ʙᴀɴ / ᴜɴʙᴀɴ</b>\n{T.LINE}\n"
                       f"ʙᴀɴ ᴋᴇ ʟɪʏᴇ: <code>123456 reason</code>\n"
                       f"ᴜɴʙᴀɴ ᴋᴇ ʟɪʏᴇ: <code>-123456</code>\n"
                       f"ᴄᴀɴᴄᴇʟ: <code>/cancel</code>\n{T.LINE}", kb.back())

    elif action == "bc":
        client.await_input[uid] = "broadcast"
        await _edit(q, f"<b>⚑ ʙʀᴏᴀᴅᴄᴀsᴛ</b>\n{T.LINE}\n"
                       f"ᴀʙ ᴠᴏʜ ᴍᴇssᴀɢᴇ ʙʜᴇᴊᴏ ᴊᴏ sᴀʙ ᴜsᴇʀs ᴋᴏ ᴊᴀᴀɴᴀ ʜᴀɪ.\n"
                       f"(ᴛᴇxᴛ / ᴘʜᴏᴛᴏ / ᴠɪᴅᴇᴏ ᴋᴜᴄʜ ʙʜɪ)\n"
                       f"ᴄᴀɴᴄᴇʟ: <code>/cancel</code>\n{T.LINE}", kb.back())

    elif action == "logs":
        rows = db.get_logs(15)
        txt = f"<b>◉ ᴀᴜᴅɪᴛ ʟᴏɢ</b>\n{T.LINE}\n"
        for r in rows:
            txt += f"• <code>{r['actor']}</code> {r['action']} · {r['detail'][:28]} · {ago(r['ts'])}\n"
        if not rows:
            txt += "ᴇᴍᴘᴛʏ"
        await _edit(q, txt, kb.back(extra=[[red("🗑 ᴄʟᴇᴀʀ ʟᴏɢs", callback_data="ok:clearlogs:")]]))

    elif action == "backup":
        await q.answer("⏳ ʙᴀᴄᴋᴜᴘ...")
        try:
            await q.message.reply_document(
                config.DB_PATH,
                caption=f"💾 ʙᴀᴄᴋᴜᴘ · {human_size(db.db_size())}",
                file_name=f"filestore-{int(time.time())}.db")
        except Exception as e:
            await q.answer(f"✘ {e}", show_alert=True)

    elif action == "sec":
        txt = (f"<b>▣ sᴇᴄᴜʀɪᴛʏ</b>\n{T.LINE}\n"
               f"✿ ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ: <code>{'ᴏɴ' if db.get_bool('protect') else 'ᴏғғ'}</code>\n"
               f"⚑ ғᴏʀᴄᴇ sᴜʙ: <code>{'ᴏɴ' if db.get_bool('force_sub') else 'ᴏғғ'}</code>\n"
               f"❖ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: <code>{human_time(db.get_int('auto_delete',1800))}</code>\n"
               f"✘ ʙᴀɴɴᴇᴅ ᴜsᴇʀs: <code>{db.count_banned()}</code>\n"
               f"◇ ᴀᴅᴍɪɴs: <code>{len(db.admin_ids())}</code>\n{T.LINE}\n"
               f"<i>ᴘʀᴏᴛᴇᴄᴛ ᴏɴ = ᴜsᴇʀ ғᴏʀᴡᴀʀᴅ / sᴀᴠᴇ ɴᴀʜɪ ᴋᴀʀ ᴘᴀᴀᴇɢᴀ</i>")
        await _edit(q, txt, kb.back(extra=[
            [blue("✿ ᴘʀᴏᴛᴇᴄᴛ ᴛᴏɢɢʟᴇ", callback_data="tg:protect"),
             blue("⚑ ғsᴜʙ ᴛᴏɢɢʟᴇ", callback_data="tg:force_sub")]]))

    elif action == "maint":
        new = db.toggle("maintenance")
        await q.answer(f"ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ {'ON' if new else 'OFF'}", show_alert=True)
        await _edit(q, panel_text(client), kb.admin_panel(uid))

    elif action == "settings":
        txt = (f"<b>⚙️ sᴇᴛᴛɪɴɢs</b>\n{T.LINE}\n"
               f"❖ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: <code>{human_time(db.get_int('auto_delete',1800))}</code>\n"
               f"✿ ᴘʀᴏᴛᴇᴄᴛ: <code>{'ᴏɴ' if db.get_bool('protect') else 'ᴏғғ'}</code>\n"
               f"⚑ ғᴏʀᴄᴇ sᴜʙ: <code>{'ᴏɴ' if db.get_bool('force_sub') else 'ᴏғғ'}</code>\n"
               f"⚠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ: <code>{'ᴏɴ' if db.get_bool('maintenance') else 'ᴏғғ'}</code>\n"
               f"▲ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ: <code>{'sᴇᴛ' if db.get('start_photo') else 'ɴᴏɴᴇ'}</code>\n"
               f"📁 sᴛᴏʀᴀɢᴇ: <code>{config.DATA_DIR}</code>\n{T.LINE}")
        await _edit(q, txt, kb.back(extra=[
            [blue("❖ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="ap:autodel"),
             blue("▲ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ", callback_data="ap:photo")],
            [green("🎨 ᴄᴏʟᴏᴜʀs: ᴏɴ", callback_data="tg:colors")
             if db.get_bool("colors", True) else
             grey("🎨 ᴄᴏʟᴏᴜʀs: ᴏғғ", callback_data="tg:colors")]]))

    elif action == "photo":
        client.await_input[uid] = "photo"
        await _edit(q, f"<b>▲ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ</b>\n{T.LINE}\n"
                       f"ᴀʙ ᴇᴋ ᴘʜᴏᴛᴏ ʙʜᴇᴊᴏ ʏᴀ ᴜsᴋᴀ ʟɪɴᴋ.\n"
                       f"ʜᴀᴛᴀɴᴇ ᴋᴇ ʟɪʏᴇ <code>remove</code> ʟɪᴋʜᴏ.\n{T.LINE}", kb.back())

    elif action == "restart":
        await q.answer("↻ ʀᴇsᴛᴀʀᴛɪɴɢ...", show_alert=True)
        os._exit(0)

    else:
        await q.answer("sᴏᴏɴ...", show_alert=False)


@Client.on_callback_query(filters.regex(r"^ok:"))
async def confirm_cb(client, q: CallbackQuery):
    if not await _guard(q):
        return
    _, action, arg = q.data.split(":", 2)
    if action == "clearlogs":
        db.clear_logs()
        await q.answer("✓ ʟᴏɢs ᴄʟᴇᴀʀᴇᴅ")
        await _edit(q, panel_text(client), kb.admin_panel(q.from_user.id))


@Client.on_callback_query(filters.regex(r"^noop$"))
async def noop_cb(client, q: CallbackQuery):
    await q.answer()


# ───────────────────────────── PANEL TEXT INPUT ─────────────────────────────
@Client.on_message(filters.private & ~filters.command(["start", "help", "panel", "batch",
                                                       "done", "cancel", "stats"]), group=2)
async def await_input_handler(client, message):
    uid = message.from_user.id if message.from_user else 0
    mode = client.await_input.get(uid)
    if not mode or not db.is_admin(uid):
        return

    client.await_input.pop(uid, None)
    text = (message.text or "").strip()

    if mode == "addadmin":
        try:
            new_id = int(text)
        except ValueError:
            return await message.reply("✘ ɢᴀʟᴀᴛ ɪᴅ.")
        db.add_admin(new_id, uid)
        db.log(uid, "add_admin", str(new_id))
        await message.reply(f"★ <code>{new_id}</code> ᴀʙ ᴀᴅᴍɪɴ ʜᴀɪ.",
                            reply_markup=kb.admin_panel(uid))

    elif mode == "ban":
        parts = text.split(maxsplit=1)
        try:
            target = int(parts[0])
        except (ValueError, IndexError):
            return await message.reply("✘ ɢᴀʟᴀᴛ ғᴏʀᴍᴀᴛ.")
        if target < 0:
            db.unban_user(abs(target))
            await message.reply(f"✓ <code>{abs(target)}</code> ᴜɴʙᴀɴɴᴇᴅ.",
                                reply_markup=kb.admin_panel(uid))
        else:
            reason = parts[1] if len(parts) > 1 else "No reason"
            db.ban_user(target, reason)
            await message.reply(f"🚫 <code>{target}</code> ʙᴀɴɴᴇᴅ.",
                                reply_markup=kb.admin_panel(uid))

    elif mode == "broadcast":
        await do_broadcast(client, message, message)

    elif mode == "photo":
        if text.lower() == "remove":
            db.set("start_photo", "")
            return await message.reply("✓ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ ʜᴀᴛᴀ ᴅɪʏᴀ.")
        if message.photo:
            db.set("start_photo", message.photo.file_id)
        elif text.startswith("http"):
            db.set("start_photo", text)
        else:
            return await message.reply("✘ ᴘʜᴏᴛᴏ ʏᴀ ʟɪɴᴋ ʙʜᴇᴊᴏ.")
        await message.reply("✓ sᴛᴀʀᴛ ᴘʜᴏᴛᴏ sᴇᴛ ʜᴏ ɢᴀʏᴀ.", reply_markup=kb.admin_panel(uid))
