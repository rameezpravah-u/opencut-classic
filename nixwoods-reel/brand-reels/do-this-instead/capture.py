"""Capture the nixwoods.com pages the how-to reel walks through (1280x800 css viewport at 2x, full page) into work/.
Lazy images are triggered by scrolling the page first. work/ is not committed; re-run this to refresh the screens.

    python3 brand-reels/do-this-instead/capture.py
"""
import asyncio, os

from playwright.async_api import async_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
PAGES = [("home", "https://nixwoods.com/"), ("floor", "https://nixwoods.com/collections/wooden-floor-lamps"),
         ("minimalist", "https://nixwoods.com/products/wooden-floor-lamp-minimalist-standing-light")]


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        ctx = await b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        pg = await ctx.new_page()
        for name, url in PAGES:
            await pg.goto(url, wait_until="networkidle", timeout=90000)
            await pg.wait_for_timeout(3000)
            h = await pg.evaluate("document.body.scrollHeight")
            for y in range(0, h, 600):
                await pg.evaluate(f"window.scrollTo(0,{y})")
                await pg.wait_for_timeout(250)
            await pg.evaluate("window.scrollTo(0,0)")
            await pg.wait_for_timeout(1500)
            await pg.screenshot(path=os.path.join(OUT, f"{name}-full.png"), full_page=True)
            print(name, h)
        await b.close()


asyncio.run(main())
