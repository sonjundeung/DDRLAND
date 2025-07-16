from core.user_storage import set_user
from core.tx import add_transaction, make_txid
import time

BONUS_AMOUNT = 100

async def give_signup_bonus(user):
    before = user.get('balance', 0)
    user['balance'] = before + BONUS_AMOUNT
    await set_user(user['id'], user)
    txid = make_txid('signup', user['id'])
    await add_transaction(
        user['id'],
        {
            "txid": txid,
            "type": "signup",
            "amount": BONUS_AMOUNT,
            "balance_before": before,
            "balance_after": user['balance'],
            "ts": int(time.time()),
            "desc": "가입보너스"
        }
    )
