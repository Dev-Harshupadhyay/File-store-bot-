"""
/start — user side: link open karo -> files milti hain -> 30 min me auto delete.
"""
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserIsBlocked, UserNotParticipant
from pyrogram.types import Message

import config
import database as db
from utils import keyboards as kb
from utils import texts as T
from utils import fsub
from utils.helpers import human_time, no_preview, progress_bar

log = logging.getLogger("start")


async def _auto_delete(client, chat_id, msg_ids, delay, count):
    """Delay ke baad saari files delete + notice."""
    await asyncio.sleep(delay)
    deleted = 0
    for mid in msg_ids:
        try:
            await client.delete_messages(chat_id, mid)
            deleted += 1
        except Exception:
            pass
    try:
        await client.send_message(
            chat_id,
            T.DELETED.format(line=T.LINE, n=deleted),
            reply_markup=kb.get_again_kb(),
        )
    except Exception:
        pass


async def deliver_batch(client, message, code, override_user=None):
    """Batch code se saari files bhejo."""
    user_id = override_user or message.from_user.id

    async def say(text, **kw):
        """Safe reply — retry ke baad original message delete ho chuka hota hai."""
        try:
            return await client.send_message(user_id, text, **kw)
        except Exception:
            return await message.reply(text, **kw)

    batch = db.get_batch(code)

    if not batch or batch["revoked"]:
        return await say(T.LINK_DEAD)

    chans = await fsub.pending(client, user_id)
    if chans:
        return await say(
            T.FSUB_MSG.format(line=T.LINE),
            reply_markup=kb.fsub_join_kb(chans, code),
        )

    ids = batch["msg_ids"]
    total = len(ids)
    protect = bool(batch["protect"]) or db.get_bool("protect")
    delay = db.get_int("auto_delete", 1800) if db.get_bool("auto_delete_on", True) else 0

    status = await say(T.SENDING.format(n=total, bar=progress_bar(0, total)))

    sent_ids = []
    for i, mid in enumerate(ids, 1):
        try:
            m = await client.copy_message(
                chat_id=user_id,
                from_chat_id=config.DB_CHANNEL,
                message_id=mid,
                protect_content=protect,
            )
            sent_ids.append(m.id)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            try:
                m = await client.copy_message(user_id, config.DB_CHANNEL, mid,
                                              protect_content=protect)
                sent_ids.append(m.id)
            except Exception:
                pass
        except UserIsBlocked:
            return
        except Exception as e:
            log.warning("copy fail %s: %s", mid, e)

        if i % 5 == 0 or i == total:
            try:
                await status.edit(T.SENDING.format(n=total, bar=progress_bar(i, total)))
            except Exception:
                pass
        await asyncio.sleep(0.35)

    db.bump_open(code)
    db.bump_files(user_id, len(sent_ids))
    db.log(user_id, "get_files", f"code={code} n={len(sent_ids)}")

    try:
        await status.delete()
    except Exception:
        pass

    if delay > 0 and sent_ids:
        warn = await client.send_message(
            user_id,
            T.DELETE_WARN.format(line=T.LINE, n=len(sent_ids), ad=human_time(delay)),
        )
        asyncio.create_task(
            _auto_delete(client, user_id, sent_ids + [warn.id], delay, len(sent_ids))
        )

    try:
        await client.send_message(
            config.LOG_CHANNEL,
            f"◉ <b>ғɪʟᴇs sᴇɴᴛ</b>\nᴜsᴇʀ: <code>{user_id}</code>\n"
            f"ᴄᴏᴅᴇ: <code>{code}</code> · ɴ: <code>{len(sent_ids)}</code>",
        )
    except Exception:
        pass


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    user = message.from_user
    db.add_user(user.id, user.first_name or "", user.username or "")

    if db.is_banned(user.id):
        row = db.get_user(user.id)
        return await message.reply(
            T.BANNED_MSG.format(line=T.LINE, reason=row["ban_reason"] or "—")
        )

    if db.get_bool("maintenance") and not db.is_admin(user.id):
        return await message.reply(T.MAINT_MSG.format(line=T.LINE))

    parts = message.text.split(maxsplit=1)

    # ── deep link: /start <code> ─────────────────────────────
    if len(parts) > 1:
        return await deliver_batch(client, message, parts[1].strip())

    # ── plain /start ─────────────────────────────────────────
    # force sub yahan bhi lagta hai — warna user bina join kiye bot use kar leta
    if await fsub.guard(client, message):
        return

    ad = human_time(db.get_int("auto_delete", 1800)) if db.get_bool("auto_delete_on", True) else "ᴏғғ"
    is_adm = db.is_admin(user.id)

    if is_adm:
        text = T.START_ADMIN.format(
            bot=config.BOT_NAME, ver=config.BOT_VERSION, line=T.LINE,
            users=db.count_users(), batches=db.count_batches(), files=db.count_files(),
        )
    else:
        text = T.START_USER.format(
            bot=config.BOT_NAME, line=T.LINE, mention=user.mention, ad=ad
        )

    photo = db.get("start_photo", "")
    if photo:
        try:
            return await message.reply_photo(photo, caption=text,
                                             reply_markup=kb.start_kb(is_adm))
        except Exception:
            pass
    await message.reply(text, reply_markup=kb.start_kb(is_adm),
                        **no_preview())


@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message: Message):
    if await fsub.guard(client, message):
        return
    ad = human_time(db.get_int("auto_delete", 1800))
    if db.is_admin(message.from_user.id):
        await message.reply(T.HELP_ADMIN.format(line=T.LINE), reply_markup=kb.close_only())
    else:
        await message.reply(T.HELP_USER.format(line=T.LINE, ad=ad),
                            reply_markup=kb.close_only())


@Client.on_callback_query(filters.regex(r"^fs:retry:"))
async def fsub_retry_cb(client, q):
    """'Try Again' — dobara check. Join ho gaya to kaam turant aage badhao."""
    await q.answer()
    code = q.data.split(":", 2)[2]
    user_id = q.from_user.id

    chans = await fsub.pending(client, user_id)
    if chans:
        # abhi bhi baaki — kaunse channel, wo bhi bata do
        left = ", ".join(c["title"][:18] for c in chans[:3])
        return await q.answer(
            f"✘ ᴀʙʜɪ ʙʜɪ ᴊᴏɪɴ ɴᴀʜɪ ᴋɪʏᴀ!\n\nʙᴀᴀᴋɪ: {left}\n\n"
            f"ᴊᴏɪɴ ᴋᴀʀᴋᴇ ᴅᴏʙᴀʀᴀ ᴛʀʏ ᴀɢᴀɪɴ ᴅᴀʙᴀᴏ.",
            show_alert=True,
        )

    try:
        await q.message.delete()
    except Exception:
        pass

    if code:
        # deep link se aaya tha -> files bhej do
        await client.send_message(user_id, "✓ ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ! ғɪʟᴇs ʙʜᴇᴊ ʀᴀʜᴀ ʜᴏᴏɴ...")
        await deliver_batch(client, q.message, code, override_user=user_id)
    else:
        # /start ya file upload par roka gaya tha -> ab khula hai
        await client.send_message(
            user_id,
            f"<b>✓ ᴠᴇʀɪғɪᴇᴅ</b>\n{T.LINE}\n"
            f"sʜᴜᴋʀɪʏᴀ ᴊᴏɪɴ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ!\n"
            f"ᴀʙ ʙᴏᴛ ᴘᴏᴏʀᴀ ᴜsᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴏ.\n\n"
            f"▪️ ғɪʟᴇ ʙʜᴇᴊᴏ — ᴛᴜʀᴀɴᴛ ʟɪɴᴋ ᴍɪʟᴇɢᴀ\n"
            f"▪️ ᴊᴏ ʟɪɴᴋ ᴋʜᴏʟɴᴀ ᴛʜᴀ ᴡᴏ ᴅᴏʙᴀʀᴀ ᴋʜᴏʟᴏ\n{T.LINE}",
            reply_markup=kb.close_only(),
        )


@Client.on_chat_join_request()
async def on_join_request(client, request):
    """Request-mode force sub — pending request ko approve maan lo."""
    try:
        db.add_join_request(request.chat.id, request.from_user.id)
        log.info("join request: %s -> %s", request.from_user.id, request.chat.id)
    except Exception as e:
        log.warning("join request save fail: %s", e)


@Client.on_message(filters.command(["dev", "developer", "about"]) & filters.private)
async def dev_cmd(client, message):
    """Developer info — Harsh Upadhyay."""
    await message.reply(
        T.DEV.format(line=T.LINE),
        reply_markup=kb.dev_kb(),
        **no_preview(),
    )
