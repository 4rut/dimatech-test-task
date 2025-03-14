from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.database import get_db
import bcrypt

router = APIRouter()


@router.post("/admin/auth/login")
async def admin_login(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or password")
    result = await db.execute(select(User).where(User.email == email, User.role == "admin"))
    admin_user = result.scalars().first()
    if not admin_user or not bcrypt.checkpw(password.encode(), admin_user.password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"id": admin_user.id, "email": admin_user.email, "full_name": admin_user.full_name}


@router.get("/admin/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role} for u in result.scalars()]
    return users


@router.post("/admin/users")
async def create_user(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    full_name = data.get("full_name")
    password = data.get("password")
    role = data.get("role", "user")
    if not email or not full_name or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields")
    password_hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = User(email=email, full_name=full_name, password=password_hashed, role=role)
    db.add(new_user)
    await db.commit()
    return {"status": "User created"}


@router.put("/admin/users/{user_id}")
async def update_user(user_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.email = data.get("email", user.email)
    user.full_name = data.get("full_name", user.full_name)
    if "password" in data:
        user.password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    await db.commit()
    return {"status": "User updated"}


@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"status": "User deleted"}
