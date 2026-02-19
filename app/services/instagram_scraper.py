import asyncio
import random
from playwright.async_api import async_playwright
from app.config import settings
from loguru import logger

class InstagramScraper:
    def __init__(self):
        self.headless = settings.SCRAPE_HEADLESS
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    async def scrape_profile(self, url: str, limit: int = 12):
        data = {
            "username": None,
            "full_name": None,
            "biography": None,
            "external_link": None,
            "followers_count": "Unknown",
            "following_count": "Unknown",
            "posts_count": "Unknown",
            "posts": [],
            "error": None
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={'width': 1280, 'height': 800},
                device_scale_factor=1,
            )
            await context.route("**/*.{png,jpg,jpeg,gif,css,woff,woff2}", lambda route: route.abort())
            page = await context.new_page()

            try:
                logger.info(f"Instagram: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=settings.REQUEST_TIMEOUT * 1000)
                await asyncio.sleep(random.uniform(2, 4))

                title = await page.title()
                if "Login" in title or "Page Not Found" in title:
                     logger.warning("Instagram login wall/404 detected.")
                     data["error"] = "Login wall or profile not found"
                
                try:
                    data["username"] = await page.locator("meta[property='og:title']").get_attribute("content")
                    desc = await page.locator("meta[property='og:description']").get_attribute("content")
                    if desc:
                        data["biography"] = desc 
                except Exception:
                    pass

                try:
                    posts = page.locator("article a")
                    count = await posts.count()
                    for i in range(min(count, limit)):
                        p_loc = posts.nth(i)
                        link = await p_loc.get_attribute("href")
                        alt = await p_loc.locator("img").get_attribute("alt")
                        data["posts"].append({
                            "link": f"https://instagram.com{link}",
                            "caption": alt[:100] if alt else ""
                        })
                except Exception as e:
                    logger.error(f"Post scrape error: {e}")

            except Exception as e:
                logger.error(f"IG Fail: {e}")
                data["error"] = str(e)
            finally:
                await browser.close()
        
        return data
