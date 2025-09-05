import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from storage import init_data
from handlers import router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    logger.debug("Starting bot initialization...")
    logger.debug(f"TOKEN: {TOKEN[:10]}...")
    try:
        logger.debug("Calling init_data...")
        init_data()
        logger.debug("init_data completed")
        storage = MemoryStorage()
        logger.debug("MemoryStorage initialized")
        bot = Bot(token=TOKEN)
        logger.debug("Bot initialized")
        dp = Dispatcher(storage=storage)
        logger.debug("Dispatcher initialized")
        dp.include_router(router)
        logger.debug("Router included")
        logger.info("Bot started. Waiting for messages...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        logger.debug("Closing bot session...")
        await bot.session.close()

if __name__ == "__main__":
    logger.debug("Running main...")
    asyncio.run(main())