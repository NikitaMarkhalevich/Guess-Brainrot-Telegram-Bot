from aiogram import Bot, Dispatcher
import asyncio

from dotenv import load_dotenv
import os
load_dotenv() 

from handlers import router

dp = Dispatcher()

async def main():
    bot = Bot(os.getenv('BOT_TOKEN'))
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')