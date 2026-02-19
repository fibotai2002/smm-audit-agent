from django.core.management.base import BaseCommand
from bot.services.user_service import UserService
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Sets the tier for a user. Usage: python manage.py set_tier <telegram_id> <tier>'

    def add_arguments(self, parser):
        parser.add_argument('telegram_id', type=int)
        parser.add_argument('tier', type=str, choices=['free', 'pro', 'agency'])

    def handle(self, *args, **options):
        telegram_id = options['telegram_id']
        tier = options['tier']
        
        service = UserService()
        
        async def run():
            success = await service.upgrade_tier(telegram_id, tier)
            return success

        success = async_to_sync(run)()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'Successfully set user {telegram_id} to tier {tier}'))
        else:
            self.stdout.write(self.style.ERROR(f'User {telegram_id} not found'))
