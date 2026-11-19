"""Private owner-only user export and confirmed, non-destructive import."""
import asyncio
import io
import json
import logging
import secrets
import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as Button, InlineKeyboardMarkup as Markup

import config
import database as db

log = logging.getLogger(__name__)
MAX_BYTES = 20 * 1024 * 1024
OWNER = filters.private & filters.user(config.OWNER_ID)


def choices(token):
    return Markup([[Button('Yes', callback_data=f'bak:{token}:yes'),
                    Button('No', callback_data=f'bak:{token}:no')]])


async def startup_prompt(client):
    token = secrets.token_hex(8)
    client.backup_prompt = token
    try:
        await client.send_message(config.OWNER_ID,
            'Bot start ho gaya. Abhi user backup chahiye?\n'
            'Restore ke liye purani backup file yahan bhejo.', reply_markup=choices(token))
    except Exception:
        log.warning('Could not DM owner. Open the bot and press Start.', exc_info=True)


async def send_user_backup(client):
    payload = await asyncio.to_thread(db.export_users)
    data = io.BytesIO(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
    data.name = f'filestore-users-{time.time_ns()}.json'
    await client.send_document(config.OWNER_ID, data,
        caption=f"User backup: {len(payload['users'])} records. Restore ke liye ye file bot ko bhejo.")


@Client.on_message(filters.command('backup') & OWNER)
async def backup_cmd(client, message):
    try:
        await send_user_backup(client)
    except Exception:
        log.exception('User backup failed')
        await message.reply('Backup nahi ban paya. Dobara try karo.')


@Client.on_message(OWNER & filters.document & filters.create(
    lambda _, __, m: (m.document.file_name or '').startswith('filestore-users-')
    and m.document.file_name.endswith('.json')), group=-1)
async def offer_restore(client, message):
    if not 0 < (message.document.file_size or 0) <= MAX_BYTES:
        await message.reply('Backup file limit: 20 MB.')
    else:
        token = secrets.token_hex(8)
        client.pending_user_restore = (token, message)
        await message.reply('Missing users restore karein? Existing users change nahi honge.',
                            reply_markup=choices(token))
    message.stop_propagation()


@Client.on_callback_query(filters.regex(r'^bak:[0-9a-f]{16}:(yes|no)$'))
async def backup_choice(client, q):
    if (not q.from_user or not db.is_owner(q.from_user.id) or not q.message
            or q.message.chat.id != config.OWNER_ID):
        return await q.answer('Owner only', show_alert=True)
    _, token, choice = q.data.split(':')
    pending = getattr(client, 'pending_user_restore', None)
    restore = pending is not None and pending[0] == token
    if restore:
        client.pending_user_restore = None
    elif token == getattr(client, 'backup_prompt', None):
        client.backup_prompt = None
    else:
        return await q.answer('Prompt expired', show_alert=True)
    await q.answer()
    if choice == 'no':
        return await q.message.edit_text('Skipped. Koi change nahi hua.')
    try:
        if restore:
            file = await client.download_media(pending[1], in_memory=True)
            if file is None or file.getbuffer().nbytes > MAX_BYTES:
                raise ValueError('Missing or oversized backup')
            count = await asyncio.to_thread(db.restore_users, json.loads(file.getvalue()))
            status = f'Restore complete: {count} new users added.'
        else:
            await send_user_backup(client)
            status = 'Backup sent.'
    except Exception:
        log.exception('Backup operation failed')
        status = 'Operation failed. Sahi backup file bhejo ya /backup dobara try karo.'
    await q.message.edit_text(status)
