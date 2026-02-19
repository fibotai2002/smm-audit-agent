from django.core.management.base import BaseCommand
from bot.models import User, Audit
from bot.services.audit_engine import AuditEngine
from unittest.mock import MagicMock, patch
import asyncio
import json

class Command(BaseCommand):
    help = 'Tests the audit flow with mocked scrapers'

    def handle(self, *args, **options):
        self.stdout.write("Starting Audit Flow Verification (Mocked Scrapers)...")

        # 1. Create/Get User
        user, created = User.objects.get_or_create(
            telegram_id=999999999,
            defaults={"username": "mock_user", "full_name": "Mock User", "tier": "pro"}
        )
        self.stdout.write(f"User: {user} (Created: {created})")

        # 2. Create Audit
        audit = Audit.objects.create(user=user, telegram_url="https://t.me/telegram")
        self.stdout.write(f"Audit Created: {audit.id}")

        # 3. Run Engine with Mocks
        engine = AuditEngine()
        
        # Mock Telegram Scraper
        mock_tg_data = {
            "channel_name": "Telegram News",
            "description": "Official Telegram Channel",
            "subscribers_count": "10M",
            "posts": [{"text": "Hello World", "views": "1M"} for _ in range(5)],
            "error": None
        }
        engine.tg.scrape_channel = MagicMock(return_value=asyncio.Future())
        engine.tg.scrape_channel.return_value.set_result(mock_tg_data)
        
        # Mock Instagram Scraper (return empty or error)
        engine.ig.scrape_profile = MagicMock(return_value=asyncio.Future())
        engine.ig.scrape_profile.return_value.set_result({"error": "No URL provided"})

        async def run_audit():
            self.stdout.write("Running audit execution...")
            result = await engine.perform_audit(audit.id, ig_url=None, tg_url="https://t.me/telegram")
            return result

        try:
            # Use asyncio.run directly
            result_audit = asyncio.run(run_audit())
            
            # 4. Verify
            audit.refresh_from_db()
            self.stdout.write(f"Final Status: {audit.status}")
            
            if audit.status == "completed":
                self.stdout.write(self.style.SUCCESS("✅ Audit Completed Successfully!"))
                self.stdout.write(f"Collected Data: {json.dumps(audit.collected_data_json, indent=2)}")
                self.stdout.write(f"Report Keys: {audit.report_json.keys() if audit.report_json else 'None'}")
                if audit.report_json:
                     self.stdout.write(f"Report Preview: {str(audit.report_json)[:200]}...")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Audit Failed. Error: {audit.error_message}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Exception during execution: {e}"))
