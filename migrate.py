import asyncio
import time
import bcrypt
from sqlalchemy.exc import OperationalError
from app.models import Base, User, Account
from app.config import config
from app.database import engine, async_session


async def wait_for_db(engine, timeout=30):
    start = time.time()
    while True:
        try:
            async with engine.connect() as conn:
                return
        except OperationalError as e:
            if time.time() - start > timeout:
                raise Exception("Database connection timeout") from e
            print("Ожидание запуска базы данных...")
            await asyncio.sleep(1)


async def migrate():
    await wait_for_db(engine, timeout=30)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_test_data():
    async with async_session() as session:
        user_password = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
        test_user = User(email="user@example.com", full_name="Test User", password=user_password, role="user")
        session.add(test_user)
        await session.commit()

        test_account = Account(user_id=test_user.id, balance=0)
        session.add(test_account)

        admin_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        admin_user = User(email="admin@example.com", full_name="Test Admin", password=admin_password, role="admin")
        session.add(admin_user)
        await session.commit()


async def main():
    await migrate()
    await create_test_data()
    print("Миграция и создание тестовых данных завершены.")


if __name__ == "__main__":
    asyncio.run(main())
