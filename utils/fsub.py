"""
Force-subscribe gate — ek hi jagah, saare handlers yahi use karte hain.

Pehle ye check sirf deliver_batch() me tha, isliye /start aur file-upload
bina join kiye chal jate the. Ab har entry point isi guard se guzarta hai.
"""
import logging

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant

import database as db
from utils import keyboards as kb
from utils import texts as T

log = logging.getLogger("fsub")

# in status me hai to "joined" maana jayega
JOINED = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.OWNER,
    ChatMemberStatus.RESTRICTED,      # restricted hai par member to hai
}


async def pending(client, user_id):
    """Jin channels me user nahi hai unki list. Khaali list = sab theek."""
    if not db.get_bool("force_sub"):
        return []

    # admin / owner ko chhoot
    if db.is_admin(user_id):
        return []

    out = []
    for ch in db.fsub_list():
        chat_id = ch["chat_id"]
        mode = (ch["mode"] if "mode" in ch.keys() else "join") or "join"

        # request mode: pending join request bhi chalega
        if mode == "request" and db.has_join_request(chat_id, user_id):
            continue

        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in JOINED:
                continue
            out.append(dict(ch))                     # LEFT / BANNED
        except UserNotParticipant:
            out.append(dict(ch))
        except Exception as e:
            # bot channel me admin nahi / channel delete — user ko block mat karo
            log.warning("fsub check fail %s: %s — skip", chat_id, e)
            continue
    return out


async def guard(client, message, code=""):
    """
    True  -> user block hua, join screen bhej diya (caller turant return kare)
    False -> user clear hai, aage badho
    """
    if not message.from_user:
        return False

    chans = await pending(client, message.from_user.id)
    if not chans:
        return False

    await message.reply(
        T.FSUB_MSG.format(line=T.LINE),
        reply_markup=kb.fsub_join_kb(chans, code),
    )
    return True


async def is_clear(client, user_id):
    """Sirf bool chahiye ho to."""
    return not await pending(client, user_id)
