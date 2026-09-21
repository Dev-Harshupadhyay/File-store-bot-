"""
Harsh File Store Bot — main client
Railway + SQLite volume ke liye banaya gaya.
"""
import asyncio
import logging
import os
import sys
import time

from pyrogram import Client
from pyrogram.enums import ParseMode

import config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s · %(name)s · %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
log = logging.getLogger("bot")

START_TIME = time.time()


class FileStoreBot(Client):
    def __init__(self):
        super().__init__(
            name="filestore",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workdir=config.SESSION_DIR,
            plugins=dict(root="handlers"),
            workers=config.WORKERS,
            parse_mode=ParseMode.HTML,
            sleep_threshold=20,
        )
        self.uptime = START_TIME
        self.username = None
        self.batch_cache = {}   # user_id -> [msg_ids]  (batch mode buffer)
        self.await_input = {}   # user_id -> action string (panel text input)

    async def start(self):
        missing = config.validate()
        if missing:
            log.error("❌ Missing env vars: %s", ", ".join(missing))
            sys.exit(1)

        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.mention = me.mention

        # DB channel check
        try:
            ch = await self.get_chat(config.DB_CHANNEL)
            test = await self.send_message(config.DB_CHANNEL, "✅ Bot started · DB channel OK")
            await test.delete()
            log.info("DB channel ready: %s", ch.title)
        except Exception as e:
            log.error("❌ DB_CHANNEL error: %s — bot ko us channel me admin banao!", e)
            sys.exit(1)

        # Railway health-check web server (bot ke hi event loop par)
        try:
            from web import start_web
            self.web_runner = await start_web(config.PORT)
            log.info("🌐 health server on :%s", config.PORT)
        except Exception as e:
            log.warning("web server skip: %s", e)

        log.info("🤖 @%s live · data dir: %s", self.username, config.DATA_DIR)

        try:
            import database as db
            await self.send_message(
                config.LOG_CHANNEL,
                f"<b>🤖 {config.BOT_NAME} {config.BOT_VERSION} sᴛᴀʀᴛᴇᴅ</b>\n"
                f"◉ ᴜsᴇʀs: <code>{db.count_users()}</code>\n"
                f"◆ ʙᴀᴛᴄʜᴇs: <code>{db.count_batches()}</code>\n"
                f"▪️ sᴛᴏʀᴀɢᴇ: <code>{config.DATA_DIR}</code>",
            )
        except Exception:
            pass

    async def stop(self, *args):
        await super().stop()
        log.info("Bot stopped.")


app = FileStoreBot()

if __name__ == "__main__":
    app.run()
