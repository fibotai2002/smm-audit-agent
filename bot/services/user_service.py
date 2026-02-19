from bot.models import User
from django.conf import settings
from loguru import logger
from asgiref.sync import sync_to_async

class UserService:
    async def get_or_create_user(self, telegram_id: int, username: str = None, full_name: str = None):
        user, created = await User.objects.aget_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": username,
                "full_name": full_name,
                "tier": "free"
            }
        )
        
        if not created:
            if user.username != username or user.full_name != full_name:
                user.username = username
                user.full_name = full_name
                await user.asave()
        
        return user, created

    async def get_user(self, telegram_id: int):
        try:
            return await User.objects.aget(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None

    async def upgrade_tier(self, telegram_id: int, tier_name: str, days: int = 30):
        user = await self.get_user(telegram_id)
        if user:
            user.tier = tier_name
            from datetime import timedelta
            from django.utils import timezone
            user.subscription_expires_at = timezone.now() + timedelta(days=days)
            await user.asave()
            return True
        return False
