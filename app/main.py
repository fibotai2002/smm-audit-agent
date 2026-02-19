from app.db import init_db
from app.bot.bot import create_bot
from loguru import logger
from telegram.ext import Application

async def post_init(application: Application):
    print("Beginning DB Initialization...")
    await init_db()
    print("DB Initialized.")
    logger.info("DB Initialized.")

def main():
    print("Starting Bot Process...")
    logger.info("Starting Bot Process...")
    
    app = create_bot(post_init=post_init)
    
    print("Polling starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
