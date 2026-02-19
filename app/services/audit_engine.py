from app.services.instagram_scraper import InstagramScraper
from app.services.telegram_scraper import TelegramScraper
from app.services.gemini_service import GeminiService
from app.db import AsyncSessionLocal
from app.models import Audit
from datetime import datetime
from loguru import logger

class AuditEngine:
    def __init__(self):
        self.ig = InstagramScraper()
        self.tg = TelegramScraper()
        self.ai = GeminiService()

    async def perform_audit(self, audit_id: str, ig_url: str, tg_url: str):
        async with AsyncSessionLocal() as db:
            audit = await db.get(Audit, audit_id)
            if not audit: return None
            
            audit.status = "scraping"
            await db.commit()

            data = {"instagram": {}, "telegram": {}, "meta": {"collected_at": datetime.utcnow().isoformat()}}
            
            # Use default limits defined in scrapers/config
            if ig_url: data["instagram"] = await self.ig.scrape_profile(ig_url)
            if tg_url: data["telegram"] = await self.tg.scrape_channel(tg_url)

            audit.collected_data_json = data
            audit.status = "analyzing"
            await db.commit()

            try:
                report = await self.ai.analyze_social_presence(data)
                audit.report_json = report
                audit.status = "completed"
            except Exception as e:
                audit.status = "failed"
                audit.error_message = str(e)
                logger.error(f"Audit failed: {e}")
            
            await db.commit()
            return audit
