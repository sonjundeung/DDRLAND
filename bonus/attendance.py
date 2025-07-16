from core.user_storage import set_user
from core.tx import add_transaction, make_txid
import time

BONUS_AMOUNT = 50

async def give_attendance_bonus(user, message):
    before = user.get('balance', 0)
    user['balance'] = before + BONUS_AMOUNT
    await set_user(user['id'], user)
    txid = make_txid('attendance', user['id'])
    await add_transaction(
        user['id'],
        {
            "txid": txid,
            "type": "attendance",
            "amount": BONUS_AMOUNT,
            "balance_before": before,
            "balance_after": user['balance'],
            "ts": int(time.time()),
            "desc": "출석보너스"
        }
    )
    try:
        await message.answer(
            f"🗓️ <b>출석 보너스 {BONUS_AMOUNT} 딸러 지급!</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
