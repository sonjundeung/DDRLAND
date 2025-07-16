from aiogram import BaseMiddleware
from core.user_storage import get_user, set_user

class UpdateNicknameMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        message = data.get("event_message") or data.get("message")
        if not message or not message.from_user:
            return await handler(event, data)
        user = await get_user(message.from_user.id)
        if user is not None and user.get("name") != message.from_user.full_name:
            user["name"] = message.from_user.full_name
            try:
                await set_user(message.from_user.id, user)
            except Exception:
                pass
        return await handler(event, data)
