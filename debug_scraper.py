import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting Playwright...")
    async with async_playwright() as p:
        print("Launching Browser...")
        try:
            browser = await p.chromium.launch(headless=True)
            print("Browser Launched!")
            page = await browser.new_page()
            print("Page created. Navigating to Telegram...")
            await page.goto("https://t.me/s/telegram", timeout=20000, wait_until="domcontentloaded")
            print("Navigated to Telegram!")
            title = await page.title()
            print(f"Title: {title}")
            await browser.close()
            print("Browser Closed.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
