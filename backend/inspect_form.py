"""Inspect form to get actual field selectors."""
import asyncio
from playwright.async_api import async_playwright


async def inspect_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://mendrika-alma.github.io/form-submission/")
        await page.wait_for_timeout(2000)

        # Get all input fields
        inputs = await page.query_selector_all("input, select")

        print("Form Fields Found:")
        print("=" * 80)

        for inp in inputs:
            name = await inp.get_attribute("name") or ""
            id_attr = await inp.get_attribute("id") or ""
            type_attr = await inp.get_attribute("type") or "text"
            placeholder = await inp.get_attribute("placeholder") or ""

            # Get label if available
            label_text = ""
            try:
                label = await page.query_selector(f'label[for="{id_attr}"]')
                if label:
                    label_text = await label.inner_text()
            except:
                pass

            if name or id_attr:
                print(f"name='{name}' | id='{id_attr}' | type='{type_attr}' | label='{label_text}' | placeholder='{placeholder}'")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_form())
