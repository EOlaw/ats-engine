"""Seed test users into the database."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import sessionmanager
from app.core.config import get_settings
from app.models import user, resume, export  # noqa: F401 — register all models
from app.schemas.user import UserCreate
from app.services.user_service import UserService


TEST_USERS = [
    UserCreate(
        email="test@example.com",
        password="Test1234!",
        full_name="Test User",
    ),
    UserCreate(
        email="admin@ats-engine.com",
        password="Admin1234!",
        full_name="Admin User",
    ),
]


async def seed():
    settings = get_settings()
    sessionmanager.initialize()

    async with sessionmanager.get_session() as session:
        service = UserService(session)
        for user_data in TEST_USERS:
            existing = await service.get_user_by_email(user_data.email)
            if existing:
                print(f"  [skip] {user_data.email} already exists")
                continue
            user = await service.create_user(user_data)
            print(f"  [created] {user.email} (id={user.id})")

    await sessionmanager.close()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
