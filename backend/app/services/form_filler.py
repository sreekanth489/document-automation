import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page

from app.config import get_settings
from app.schemas.documents import PassportData, G28Data, FormFillResponse


async def fill_by_label(page: Page, label_text: str, value: Optional[str]) -> bool:
    """Fill a field by finding it via its label text."""
    if not value:
        return False
    try:
        # Try multiple strategies to find the input
        # Strategy 1: Label with for attribute
        label = page.locator(f'label:has-text("{label_text}")')
        if await label.count() > 0:
            for_attr = await label.first.get_attribute('for')
            if for_attr:
                input_el = page.locator(f'#{for_attr}')
                if await input_el.count() > 0:
                    await input_el.fill(value)
                    return True

        # Strategy 2: Input near label
        field = page.locator(f'label:has-text("{label_text}") + input, '
                            f'label:has-text("{label_text}") ~ input').first
        if await field.count() > 0:
            await field.fill(value)
            return True

        # Strategy 3: Input within same container as label
        container = page.locator(f':has(> label:has-text("{label_text}")) input').first
        if await container.count() > 0:
            await container.fill(value)
            return True

        return False
    except Exception:
        return False


async def fill_field(page: Page, selectors: list[str], value: Optional[str]) -> bool:
    """Try multiple selectors to fill a field."""
    if not value:
        return False
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if await locator.count() > 0:
                tag = await locator.evaluate("el => el.tagName.toLowerCase()")
                if tag == "select":
                    await locator.select_option(value)
                else:
                    await locator.fill(value)
                return True
        except Exception:
            continue
    return False


async def click_radio_by_label(page: Page, group_label: str, value: str) -> bool:
    """Click a radio button by finding it near a label."""
    if not value:
        return False
    try:
        # Try to find radio button with matching value
        radio = page.locator(f'input[type="radio"][value="{value}"]').first
        if await radio.count() > 0:
            await radio.click()
            return True

        # Try finding by label text
        radio = page.locator(f'label:has-text("{value}") input[type="radio"]').first
        if await radio.count() > 0:
            await radio.click()
            return True

        return False
    except Exception:
        return False


async def fill_form(
    passport: Optional[PassportData],
    g28: Optional[G28Data],
    session_id: str,
    headless: bool = True
) -> FormFillResponse:
    """Navigate to form and fill fields with extracted data."""
    settings = get_settings()

    screenshot_dir = Path(settings.screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 1280, "height": 2000})
        page = await context.new_page()

        filled_fields = []
        failed_fields = []

        try:
            await page.goto(settings.form_url, wait_until="networkidle")
            await page.wait_for_timeout(1500)

            # Part 1: Attorney/Representative Information (from G-28)
            if g28:
                field_mappings = [
                    ("Attorney Family Name", g28.attorney_family_name, [
                        'input[name*="family" i]', 'input[id*="family" i]',
                        'input[placeholder*="Family" i]'
                    ]),
                    ("Attorney Given Name", g28.attorney_given_name, [
                        'input[name*="given" i]', 'input[id*="given" i]',
                        'input[placeholder*="Given" i]'
                    ]),
                    ("Attorney Middle Name", g28.attorney_middle_name, [
                        'input[name*="middle" i]', 'input[id*="attorney"][id*="middle" i]'
                    ]),
                    ("Street Address", g28.street_address, [
                        'input[name*="street" i]', 'input[id*="street" i]',
                        'input[placeholder*="Street" i]'
                    ]),
                    ("City", g28.city, [
                        'input[name*="city" i]', 'input[id*="city" i]'
                    ]),
                    ("State", g28.state, [
                        'select[name*="state" i]', 'select[id*="state" i]',
                        'input[name*="state" i]'
                    ]),
                    ("ZIP Code", g28.zip_code, [
                        'input[name*="zip" i]', 'input[id*="zip" i]',
                        'input[placeholder*="ZIP" i]'
                    ]),
                    ("Country", g28.country, [
                        'input[name*="country" i]:not([name*="issue"])',
                        'input[id*="country" i]:not([id*="issue"])'
                    ]),
                    ("Daytime Phone", g28.daytime_phone, [
                        'input[name*="daytime" i]', 'input[id*="daytime" i]',
                        'input[type="tel"]:first-of-type'
                    ]),
                    ("Mobile Phone", g28.mobile_phone, [
                        'input[name*="mobile" i]', 'input[id*="mobile" i]'
                    ]),
                    ("Email", g28.email, [
                        'input[type="email"]', 'input[name*="email" i]',
                        'input[id*="email" i]'
                    ]),
                    ("Licensing Authority", g28.licensing_authority, [
                        'input[name*="licensing" i]', 'input[id*="licensing" i]',
                        'input[name*="authority" i]'
                    ]),
                    ("Bar Number", g28.bar_number, [
                        'input[name*="bar" i]', 'input[id*="bar" i]'
                    ]),
                    ("Law Firm Name", g28.law_firm_name, [
                        'input[name*="firm" i]', 'input[id*="firm" i]',
                        'input[name*="organization" i]'
                    ]),
                ]

                for label, value, selectors in field_mappings:
                    if value:
                        success = await fill_field(page, selectors, value)
                        if not success:
                            success = await fill_by_label(page, label, value)
                        if success:
                            filled_fields.append(label)
                        else:
                            failed_fields.append(label)

            # Part 3: Beneficiary Passport Details
            if passport:
                passport_mappings = [
                    ("Beneficiary Last Name", passport.last_name, [
                        'input[name*="last" i][name*="name" i]',
                        'input[id*="last" i][id*="name" i]',
                        'input[name*="beneficiary" i][name*="last" i]'
                    ]),
                    ("Beneficiary First Name", passport.first_name, [
                        'input[name*="first" i][name*="name" i]',
                        'input[id*="first" i][id*="name" i]',
                        'input[name*="beneficiary" i][name*="first" i]'
                    ]),
                    ("Beneficiary Middle Name", passport.middle_name, [
                        'input[name*="beneficiary" i][name*="middle" i]',
                        'input[id*="beneficiary" i][id*="middle" i]'
                    ]),
                    ("Passport Number", passport.passport_number, [
                        'input[name*="passport" i][name*="number" i]',
                        'input[id*="passport" i]',
                        'input[name*="passport" i]'
                    ]),
                    ("Country of Issue", passport.country_of_issue, [
                        'input[name*="country" i][name*="issue" i]',
                        'input[id*="country" i][id*="issue" i]'
                    ]),
                    ("Nationality", passport.nationality, [
                        'input[name*="nationality" i]',
                        'input[id*="nationality" i]'
                    ]),
                    ("Date of Birth", passport.date_of_birth, [
                        'input[name*="birth" i][type="date"]',
                        'input[id*="birth" i][type="date"]',
                        'input[name*="dob" i]'
                    ]),
                    ("Place of Birth", passport.place_of_birth, [
                        'input[name*="place" i][name*="birth" i]',
                        'input[id*="place" i][id*="birth" i]'
                    ]),
                    ("Date of Issue", passport.date_of_issue, [
                        'input[name*="issue" i][type="date"]:not([name*="country"])',
                        'input[id*="issue" i][type="date"]'
                    ]),
                    ("Date of Expiration", passport.date_of_expiration, [
                        'input[name*="expir" i][type="date"]',
                        'input[id*="expir" i][type="date"]'
                    ]),
                ]

                for label, value, selectors in passport_mappings:
                    if value:
                        success = await fill_field(page, selectors, value)
                        if not success:
                            success = await fill_by_label(page, label, value)
                        if success:
                            filled_fields.append(label)
                        else:
                            failed_fields.append(label)

                # Handle sex radio button
                if passport.sex:
                    sex = passport.sex.upper()
                    if sex in ["M", "F", "X"]:
                        success = await click_radio_by_label(page, "Sex", sex)
                        if success:
                            filled_fields.append("Sex")
                        else:
                            failed_fields.append("Sex")

            await page.wait_for_timeout(500)

            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = screenshot_dir / f"form_{session_id}_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)

            message = f"Filled {len(filled_fields)} fields"
            if failed_fields:
                message += f". Could not fill: {', '.join(failed_fields[:5])}"
                if len(failed_fields) > 5:
                    message += f" (+{len(failed_fields) - 5} more)"

            return FormFillResponse(
                success=True,
                message=message,
                screenshot_path=str(screenshot_path)
            )

        except Exception as e:
            return FormFillResponse(
                success=False,
                message=f"Error filling form: {str(e)}",
                screenshot_path=None
            )

        finally:
            await browser.close()
