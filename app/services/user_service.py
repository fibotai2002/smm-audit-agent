from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import User
from app.config import settings
from loguru import logger

class UserService:
    async def get_or_create_user(self, telegram_id: int, username: str = None, full_name: str = None):
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
            user = result.scalars().first()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    full_name=full_name,
                    balance=settings.TIERS["free"]["tokens"],
                    tier="free"
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                logger.info(f"New user created: {telegram_id}")
            else:
                # Update info if changed
                if user.username != username or user.full_name != full_name:
                    user.username = username
                    user.full_name = full_name
                    await db.commit()
            
            return user

    async def check_balance(self, telegram_id: int, cost: int) -> bool:
        async with AsyncSessionLocal() as db:
            user = await db.get(User, telegram_id)
            return user and user.balance >= cost

    async def deduct_balance(self, telegram_id: int, cost: int):
        async with AsyncSessionLocal() as db:
            user = await db.get(User, telegram_id)
            if user and user.balance >= cost:
                user.balance -= cost
                await db.commit()
                return True
            return False

    async def upgrade_tier(self, telegram_id: int, tier_name: str):
        if tier_name not in settings.TIERS:
            return False
            
        async with AsyncSessionLocal() as db:
            user = await db.get(User, telegram_id)
            if user:
                user.tier = tier_name
                # Add tokens for the new tier
                user.balance += settings.TIERS[tier_name]["tokens"]
                await db.commit()
                return True
            return False
    
    async def get_user_limits(self, telegram_id: int):
        async with AsyncSessionLocal() as db:
            user = await db.get(User, telegram_id)
            if not user:
                return settings.TIERS["free"]
            return settings.TIERS.get(user.tier, settings.TIERS["free"])
