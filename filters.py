from aiogram.filters import BaseFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.user_storage import get_user
from core.config import BOT_USERNAME

class RequireUserFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await get_user(message.from_user.id)
        if user is None:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="1:1 대화로 가입하기",
                    url=f"https://t.me/{BOT_USERNAME}?start=register"
                )]
            ])
            try:
                await message.reply(
                    "👋 <b>회원가입이 필요합니다!</b>\n"
                    "아래 버튼을 눌러 봇과 1:1 대화에서 /가입 을 입력해 주세요.",
                    reply_markup=kb,
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return False
        return True

class RequirePrivateFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type != "private":
            try:
                await message.answer("⚠️ 이 명령은 1:1대화에서만 사용 가능합니다.", message_auto_delete_time=7)
            except Exception:
                pass
            return False
        return True
