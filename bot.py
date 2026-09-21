"""
Harsh File Store Bot — main client
Railway + SQLite volume ke liye banaya gaya.
"""
import logging
import os
import sys
import time

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    AccessTokenExpired,
    AccessTokenInvalid,
    AuthKeyUnregistered,
    SessionRevoked,
)

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
        self.web_runner = None  # aiohttp health server

    async def start(self, *args, **kwargs):
        missing = config.validate()
        if missing:
            log.error("❌ Missing env vars: %s", ", ".join(missing))
            log.error("   Railway -> Variables me ye set karo.")
            sys.exit(1)

        problem = config.token_problem()
        if problem:
            log.error("❌ BOT_TOKEN me dikkat: %s", problem)
            log.error("   @BotFather se sahi token lo aur Railway me paste karo.")
            sys.exit(1)

        try:
            await super().start(*args, **kwargs)

        except (AccessTokenExpired, AccessTokenInvalid) as e:
            tok = config.BOT_TOKEN or ""
            masked = f"{tok[:12]}…{tok[-4:]}" if len(tok) > 18 else "(khaali)"
            log.error("")
            log.error("=" * 62)
            log.error("❌  BOT_TOKEN GALAT YA EXPIRED HAI  (%s)", type(e).__name__)
            log.error("=" * 62)
            log.error("Railway me jo token hai: %s", masked)
            log.error("")
            log.error("Ye code ka error NAHI hai. Token revoke ho chuka hai")
            log.error("ya galat paste hua hai. Theek karne ke liye:")
            log.error("")
            log.error("  1. @BotFather kholo  ->  /mybots  ->  apna bot")
            log.error("  2. API Token -> Revoke current token")
            log.error("  3. NAYA token copy karo (pura, space ke bina)")
            log.error("  4. Railway -> Variables -> BOT_TOKEN update karo")
            log.error("  5. Redeploy")
            log.error("")
            log.error("Dhyan: token ke aage/peeche space ya quotes nahi hone chahiye.")
            log.error("=" * 62)
            sys.exit(1)

        except (SessionRevoked, AuthKeyUnregistered):
            # purani session file kharab — delete karke dobara login
            import glob
            removed = 0
            for f in glob.glob(os.path.join(config.SESSION_DIR, "*.session*")):
                try:
                    os.remove(f)
                    removed += 1
                    log.warning("purani session hata di: %s", f)
                except OSError:
                    pass
            log.error("❌ session revoked — %d file hatai. Bot restart karo, "
                      "nayi session apne aap ban jayegi.", removed)
            sys.exit(1)

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

        # coloured buttons status
        try:
            import database as _db
            from utils import buttons as _btn
            _db.set("colors", "1" if config.COLOR_BUTTONS else "0")
            _btn.set_colors(config.COLOR_BUTTONS)
            st = _btn.status()
            log.info("🎨 coloured buttons: lib=%s enabled=%s",
                     st["library_supports"], st["enabled"])
            if not st["library_supports"]:
                log.warning("⚠️  library purani hai — buttons plain dikhenge. "
                            "requirements.txt me kurigram>=2.2.26 chahiye.")
        except Exception as e:
            log.warning("colour setup skip: %s", e)

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

    async def stop(self, *args, **kwargs):
        try:
            if getattr(self, "web_runner", None):
                await self.web_runner.cleanup()
        except Exception:
            pass
        await super().stop(*args, **kwargs)
        log.info("Bot stopped.")


app = FileStoreBot()

if __name__ == "__main__":
    app.run()
