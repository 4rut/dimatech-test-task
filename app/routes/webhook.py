import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Account, Payment
from app.database import get_db
from app.config import config

router = APIRouter()


@router.post("/webhook/payment")
async def payment_webhook(data: dict, db: AsyncSession = Depends(get_db)):
    secret_key = config["SECRET_KEY"]

    string_to_hash = f"{data['account_id']}{data['amount']}{data['transaction_id']}{data['user_id']}{secret_key}"
    calculated_signature = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()

    if calculated_signature != data.get("signature"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    result = await db.execute(
        select(Account).where(Account.id == data["account_id"], Account.user_id == data["user_id"])
    )
    account = result.scalars().first()
    if not account:
        account = Account(id=data["account_id"], user_id=data["user_id"], balance=0)
        db.add(account)
        await db.commit()

    result = await db.execute(
        select(Payment).where(Payment.transaction_id == data["transaction_id"])
    )
    existing_payment = result.scalars().first()
    if existing_payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction already processed")

    payment = Payment(
        transaction_id=data["transaction_id"],
        amount=data["amount"],
        account_id=data["account_id"],
        user_id=data["user_id"]
    )
    db.add(payment)
    account.balance += data["amount"]
    await db.commit()

    return {"status": "Payment processed"}
