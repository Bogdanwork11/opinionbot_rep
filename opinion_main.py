import asyncio
from aiogram import Bot, Dispatcher
from handlers import message_origin
from alive_progress import alive_bar
import time
from db.db import db_pool
# from db.tortoise_conf import init_tortoise, close_tortoise
from handlers.admins import router as admins_router 
from handlers.stats import router as stats_router
from handlers.help import router as help_router




bot_token = "8220005101:AAFxqWdhCoevrbHtW1gAn396YioLKVP0sWM"


bot = Bot(bot_token)
dp = Dispatcher()

dp.include_router(message_origin.router)#, status_router)
dp.include_router(admins_router)

dp.include_router(stats_router)
dp.include_router(help_router)

    
async def main():
    # await init_tortoise()     
    await db_pool()
    await dp.start_polling(bot)# await close_tortoise()

    
# Использование progress bar
with alive_bar(100) as bar:
    for i in range(100):  
        #Вставка задачи 
        time.sleep(0.01) # Время для загрузки
        bar()
print("Готово к полноценной работе")
        
if __name__ == '__main__':
    asyncio.run(main())
 
    