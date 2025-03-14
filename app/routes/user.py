from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Account, Payment
from app.database import get_db
import bcrypt

router = APIRouter()


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/auth/login")
async def login(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or password")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


@router.get("/user/accounts")
async def get_accounts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = [{"id": acc.id, "balance": acc.balance} for acc in result.scalars()]
    return accounts


@router.get("/user/payments")
async def get_payments(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).where(Payment.user_id == current_user.id))
    payments = [
        {"transaction_id": pay.transaction_id, "amount": pay.amount, "created_at": pay.created_at.isoformat()}
        for pay in result.scalars()
    ]
    return payments
