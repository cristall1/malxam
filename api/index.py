import os
import sys
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types

# Vercel specific: Set DB_PATH to /tmp if running on Vercel and not set
# This prevents crash on read-only file system, but data is ephemeral!
if os.environ.get("VERCEL") and not os.environ.get("DB_PATH"):
    os.environ["DB_PATH"] = "/tmp/hafiz_bot.db"

# Add parent directory to path so we can import from handlers, etc.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import BOT_TOKEN
from handlers import user_handlers, admin_handlers
from database.db import init_db

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(user_handlers.router)
dp.include_router(admin_handlers.router)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = types.Update.model_validate(data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error in webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def index():
    return {"status": "Bot is running"}
