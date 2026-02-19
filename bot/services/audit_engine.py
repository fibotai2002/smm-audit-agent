from bot.services.instagram_scraper import InstagramScraper
from bot.services.telegram_scraper import TelegramScraper
from bot.services.gemini_service import GeminiService
from bot.models import Audit
from datetime import datetime
from loguru import logger
from django.utils import timezone
import json
import asyncio

class AuditEngine:
    def __init__(self):
        self.ig = InstagramScraper()
        self.tg = TelegramScraper()
        self.ai = GeminiService()

    async def perform_audit(self, audit_id: str, ig_url: str, tg_url: str, ig_limit: int = 12, tg_limit: int = 20):
        try:
            audit = await Audit.objects.aget(id=audit_id)
        except Audit.DoesNotExist:
            return None
            
        audit.status = "scraping"
        await audit.asave()

        data = {"instagram": {}, "telegram": {}, "meta": {"collected_at": timezone.now().isoformat()}}
        
        # Use limits passed from handler
        try:
            tasks = []
            if ig_url: tasks.append(self.ig.scrape_profile(ig_url, limit=ig_limit))
            if tg_url: tasks.append(self.tg.scrape_channel(tg_url, limit=tg_limit))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Map results back to data
            res_idx = 0
            if ig_url:
                res = results[res_idx]
                data["instagram"] = res if not isinstance(res, Exception) else {"error": str(res)}
                res_idx += 1
            if tg_url:
                res = results[res_idx]
                data["telegram"] = res if not isinstance(res, Exception) else {"error": str(res)}

            audit.collected_data_json = data
            audit.status = "analyzing"
            await audit.asave()

            report = await self.ai.analyze_social_presence(data)
            audit.report_json = report
            audit.status = "completed"
        except Exception as e:
            audit.status = "failed"
            audit.error_message = str(e)
            logger.error(f"Audit failed: {e}")
        
        await audit.asave()
        return audit
