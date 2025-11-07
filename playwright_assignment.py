import asyncio
from playwright.async_api import async_playwright

async def scrape_reddit_questions():
    async with async_playwright() as p:
        # ✅ Use persistent user data dir to look human
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./reddit_user_data",
            headless=False,
            args=["--start-maximized"]
        )
        page = await browser.new_page()

        await page.goto("https://old.reddit.com/r/workingmoms/top/?t=all", wait_until="networkidle")

        print("Opened old Reddit in persistent user mode.")
        await page.wait_for_timeout(5000)

        # Scroll and scrape
        for _ in range(3):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)

        titles = await page.query_selector_all('a.title')
        questions = [await t.inner_text() for t in titles if (await t.inner_text()).strip().endswith("?")]

        with open("workingmoms_questions.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(questions))

        print(f"✅ Scraped {len(questions)} questions and saved.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_reddit_questions())
