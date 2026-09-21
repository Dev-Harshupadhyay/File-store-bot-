"""
Railway health check ke liye minimal web server (aiohttp).
"""
import time

from aiohttp import web

import config
import database as db

START = time.time()


async def _root(request):
    return web.json_response({
        "status": "alive",
        "bot": config.BOT_NAME,
        "version": config.BOT_VERSION,
        "uptime_sec": int(time.time() - START),
        "users": db.count_users(),
        "batches": db.count_batches(),
        "storage": config.DATA_DIR,
    })


async def _health(request):
    return web.Response(text="OK")


async def start_web(port=8080):
    app = web.Application()
    app.router.add_get("/", _root)
    app.router.add_get("/health", _health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    return runner
