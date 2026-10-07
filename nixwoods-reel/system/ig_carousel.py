"""Open a public Instagram post in headless Chromium and save every carousel slide.

Run with the user's approval (they switched the session out of Auto mode for this).
Chromium is told to trust only the session's own egress-proxy CAs (by SPKI pin), the
same CAs curl already trusts through /root/.ccr/ca-bundle.crt.

usage: python3 carousel.py <post-url> <out-dir>
"""
import asyncio, base64, hashlib, json, os, re, subprocess, sys
from playwright.async_api import async_playwright


def proxy_spki():
    pem = open("/root/.ccr/ca-bundle.crt").read()
    pins = set()
    for c in re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", pem, re.S):
        subj = subprocess.run(["openssl", "x509", "-noout", "-subject"], input=c, capture_output=True, text=True).stdout
        if "Anthropic" not in subj:
            continue
        pub = subprocess.run(["openssl", "x509", "-pubkey", "-noout"], input=c, capture_output=True, text=True).stdout
        der = subprocess.run(["openssl", "pkey", "-pubin", "-outform", "DER"], input=pub.encode(), capture_output=True).stdout
        pins.add(base64.b64encode(hashlib.sha256(der).digest()).decode())
    return ",".join(sorted(pins))


async def main(url, out):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium",
            args=[f"--ignore-certificate-errors-spki-list={proxy_spki()}"],
            proxy={"server": os.environ.get("HTTPS_PROXY") or os.environ["https_proxy"]})
        ctx = await b.new_context(viewport={"width": 1280, "height": 1000}, device_scale_factor=1,
                                  user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                             "(KHTML, like Gecko) Chrome/124.0 Safari/537.36", locale="en-US")
        pg = await ctx.new_page()
        media = []
        pg.on("response", lambda r: media.append(r.url)
              if ("cdninstagram" in r.url or "fbcdn" in r.url) and "/v/t" in r.url else None)
        await pg.goto(url, wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(6000)
        for sel in ['[role="dialog"] [aria-label="Close"]', 'button:has-text("Not now")',
                    'button:has-text("Decline optional cookies")', 'button:has-text("Allow all cookies")']:
            try:
                await pg.locator(sel).first.click(timeout=1500)
                await pg.wait_for_timeout(800)
            except Exception:
                pass
        await pg.screenshot(path=f"{out}/page.png")
        print("title:", await pg.title())
        for i in range(1, 21):
            await pg.wait_for_timeout(1500)
            box = pg.locator("article ul li img, main ul li img, div[role='presentation'] img").first
            try:
                await pg.locator("article, main").first.screenshot(path=f"{out}/slide{i:02d}.png", timeout=5000)
            except Exception:
                await pg.screenshot(path=f"{out}/slide{i:02d}.png")
            nxt = pg.locator('button[aria-label="Next"]')
            if await nxt.count() == 0 or not await nxt.first.is_visible():
                print("slides:", i)
                break
            await nxt.first.click()
        # full-res slide images seen on the wire, in order, de-duplicated by asset id
        seen, keep = set(), []
        for u in media:
            m = re.search(r"/(\d+_\d+_\d+_n)\.(?:jpg|webp)", u)
            if m and m.group(1) not in seen:
                seen.add(m.group(1)); keep.append(u)
        json.dump(keep, open(f"{out}/media.json", "w"), indent=1)
        print("distinct images on the wire:", len(keep))
        await b.close()


asyncio.run(main(sys.argv[1], sys.argv[2]))
