from aiogram import Router
from aiogram.types import Message
from core.user_storage import get_user, set_user
join_router = Router()

@join_router.message(commands=["가입", "start"])
async def join_handler(message: Message):
    user = await get_user(message.from_user.id)
    if user is not None:
        try:
            await message.answer("이미 가입되어 있습니다.")
        except Exception:
            pass
        return
    user = {
        "id": message.from_user.id,
        "name": message.from_user.full_name,
        "joined": message.date.isoformat(),
        "recovery_hash": None,
        "recovery_reset_count": 0
    }
    try:
        await set_user(message.from_user.id, user)
        await message.answer(
            "🎉 <b>가입이 완료되었습니다!</b>\n이제 복구코드를 발급받을 수 있습니다.",
            parse_mode="HTML"
        )
    except Exception:
        pass
