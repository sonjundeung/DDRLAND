from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import aioredis
from core.config import API_TOKEN, REDIS_URL
from handlers.join_router import join_router
from handlers.recovery_router import recovery_router
from middleware.update_nickname import UpdateNicknameMiddleware

redis = aioredis.from_url(REDIS_URL, decode_responses=True)
storage = RedisStorage(redis)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)
dp.message.middleware(UpdateNicknameMiddleware())
dp.include_router(join_router)
dp.include_router(recovery_router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
