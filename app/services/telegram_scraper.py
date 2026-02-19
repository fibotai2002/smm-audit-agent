import asyncio
from playwright.async_api import async_playwright
from app.config import settings
from loguru import logger

class TelegramScraper:
    def __init__(self):
        self.headless = settings.SCRAPE_HEADLESS
    
    def normalize_url(self, url: str) -> str:
        if "/s/" in url: return url
        url = url.split("?")[0]
        if "t.me/" in url:
            parts = url.split("t.me/")
            return f"{parts[0]}t.me/s/{parts[1]}"
        return url

    async def scrape_channel(self, url: str, limit: int = 20):
        url = self.normalize_url(url)
        data = {
            "channel_name": None,
            "description": None,
            "subscribers_count": None,
            "posts": [],
            "error": None
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                logger.info(f"Telegram: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=settings.REQUEST_TIMEOUT * 1000)
                await asyncio.sleep(1)

                try:
                    data["channel_name"] = await page.locator(".tgme_header_title").inner_text()
                    data["description"] = await page.locator(".tgme_header_description").inner_text()
                    data["subscribers_count"] = await page.locator(".tgme_header_counter").inner_text()
                except Exception:
                    pass

                try:
                    posts = page.locator(".tgme_widget_message_wrap")
                    count = await posts.count()
                    start = max(0, count - limit)
                    for i in range(start, count):
                        post = posts.nth(i)
                        txt = await post.locator(".tgme_widget_message_text").inner_text() if await post.locator(".tgme_widget_message_text").count() else ""
                        views = await post.locator(".tgme_widget_message_views").inner_text() if await post.locator(".tgme_widget_message_views").count() else ""
                        data["posts"].append({"text": txt[:200], "views": views})
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"TG Fail: {e}")
                data["error"] = str(e)
            finally:
                await browser.close()
        
        return data
