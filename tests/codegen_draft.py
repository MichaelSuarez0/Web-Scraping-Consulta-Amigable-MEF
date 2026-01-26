import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect


async def run(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://apps5.mineco.gob.pe/transparencia/Navegador/default.aspx?y=2024&ap=ActProy")
    await page.locator("#frame0").content_frame.get_by_role("cell", name="TOTAL", exact=True).click()
    await page.locator("#frame0").content_frame.get_by_role("button", name="Nivel de Gobierno").click()
    await page.locator("#frame0").content_frame.get_by_role("cell", name="E: GOBIERNO NACIONAL").click()
    await page.locator("#frame0").content_frame.get_by_role("button", name="Sector").click()
    await page.locator("#frame0").content_frame.get_by_role("cell", name="18,261,979,624", exact=True).click()
    await page.locator("#frame0").content_frame.get_by_role("button", name="Pliego").click()

    # ---------------------
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
