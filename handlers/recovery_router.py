from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from core.user_storage import get_user, set_user, generate_recovery_code, hash_recovery_code, get_redis
from filters import RequireUserFilter, RequirePrivateFilter
from utils.message_manager import MessageManager
import json

MAX_RESET = 3
recovery_router = Router()
recovery_router.message.filter(RequireUserFilter(), RequirePrivateFilter())

class RecoverySetup(StatesGroup):
    confirm_reset = State()
    waiting_code = State()

@recovery_router.message(Command(commands=["복구코드", "backup"]))
async def recovery_code_handler(message: Message, state: FSMContext, bot):
    user = await get_user(message.from_user.id)
    msg_mgr = MessageManager(state, bot)
    reset_count = user.get("recovery_reset_count", 0)
    if user.get("recovery_hash"):
        if reset_count >= MAX_RESET:
            msg = await message.answer("복구코드 재설정은 3회까지만 가능합니다.")
            await msg_mgr.push(msg)
            return
        remain = MAX_RESET - reset_count
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"예(남은 {remain}회)", callback_data="recovery_reset_yes"),
             InlineKeyboardButton(text="아니오", callback_data="recovery_reset_no")]
        ])
        msg = await message.answer(
            "이미 복구코드가 있습니다.\n새 코드로 재설정할까요?",
            reply_markup=kb
        )
        await msg_mgr.push(msg)
        await state.set_state(RecoverySetup.confirm_reset)
        return
    await issue_new_recovery_code(message, state, bot, reset_count=0)

@recovery_router.callback_query(lambda c: c.data in ["recovery_reset_yes", "recovery_reset_no"])
async def recovery_reset_confirm(query: CallbackQuery, state: FSMContext, bot):
    user = await get_user(query.from_user.id)
    msg_mgr = MessageManager(state, bot)
    reset_count = user.get("recovery_reset_count", 0)
    await query.message.delete()
    if query.data == "recovery_reset_yes":
        if reset_count >= MAX_RESET:
            msg = await query.message.answer("재설정 한도를 초과했습니다.")
            await msg_mgr.push(msg)
            await state.clear()
            return
        msg = await query.message.answer("새 복구코드를 발급합니다.")
        await msg_mgr.push(msg)
        await issue_new_recovery_code(query.message, state, bot, reset_count=reset_count+1)
    else:
        msg = await query.message.answer("재설정이 취소되었습니다.")
        await msg_mgr.push(msg)
    await state.clear()

async def issue_new_recovery_code(message, state, bot, reset_count=0):
    uid = message.from_user.id
    recovery_code = generate_recovery_code()
    recovery_hash = hash_recovery_code(recovery_code)
    user = await get_user(uid)
    user["recovery_hash"] = recovery_hash
    user["recovery_reset_count"] = reset_count
    user["name"] = message.from_user.full_name
    await set_user(uid, user)
    remain = MAX_RESET - reset_count
    msg_mgr = MessageManager(state, bot)
    msg = await message.answer(
        f"🛡️ <b>복구코드가 발급되었습니다!</b>\n\n<code>{recovery_code}</code>\n"
        f"꼭 복사/캡처해 보관하세요.\n(남은 재설정: {remain}회)",
        parse_mode="HTML"
    )
    await msg_mgr.push(msg)

@recovery_router.message(Command(commands=["코드복구", "restore"]))
async def restore_handler(message: Message, state: FSMContext, bot):
    msg_mgr = MessageManager(state, bot)
    msg = await message.answer("복구코드를 입력해 주세요.")
    await msg_mgr.push(msg)
    await state.set_state(RecoverySetup.waiting_code)

@recovery_router.message(RecoverySetup.waiting_code)
async def restore_process(message: Message, state: FSMContext, bot):
    msg_mgr = MessageManager(state, bot)
    code = message.text.strip()
    input_hash = hash_recovery_code(code)
    r = await get_redis()
    found_user = None
    for key in await r.keys("user:*"):
        data = await r.get(key)
        user = json.loads(data)
        if user.get("recovery_hash") == input_hash:
            found_user = user
            break
    try:
        await message.delete()
    except Exception:
        pass
    if not found_user:
        msg = await message.answer("❗ 일치하는 복구코드가 없습니다. 다시 입력해 주세요.")
        await msg_mgr.push(msg)
        return

    new_uid = message.from_user.id
    old_uid = found_user["id"]
    found_user["id"] = new_uid
    found_user["name"] = message.from_user.full_name
    try:
        await r.delete(f"user:{old_uid}")
        await r.set(f"user:{new_uid}", json.dumps(found_user))
    except Exception:
        pass

    msg = await message.answer(
        "✅ <b>계정 복구가 완료되었습니다!</b>\n"
        f"닉네임: {found_user.get('name')}\n가입일: {found_user.get('joined')}",
        parse_mode="HTML"
    )
    await msg_mgr.push(msg)
    await state.clear()
