import logging
from playwright.async_api import async_playwright


async def polycom_factory_reset(ip_address, current_password, log_file, headless):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:
            await page.goto(f"https://{ip_address}/login.htm")
            await page.fill('input[name="password"]', current_password)
            await page.click('input[type="submit"]')
            await page.click("text=Utilities")
            await page.click("text=Phone Backup & Restore")
            await page.click("text=Global Settings")
            await page.click('input[name="RestoreToFacrotyBtn"]')
            await page.click("button#popupbtn0")

            print(f"Factory reset initiated for Poly phone at {ip_address}")
        except Exception as e:
            logging.error(f"Error resetting Poly phone at {ip_address}: {e}")
            print(f"Error resetting Poly phone at {ip_address}: {e}")
        finally:
            await context.close()
            await browser.close()


async def polycom_provision(
    ip_address, new_password, provisioning_server_address, log_file, headless
):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:
            await page.goto(f"https://{ip_address}/login.htm")
            await page.fill('input[name="password"]', new_password)
            await page.click('input[type="submit"]')
            await page.click("text=Settings")
            await page.click("text=Provisioning Server")
            await page.select_option('select[name="ServerType"]', "HTTPS")
            await page.fill('input[name="ServerAddress"]', provisioning_server_address)
            await page.fill('input[name="ServerUser"]', "")
            await page.fill('input[name="ServerPassword"]', "")
            await page.click("text=DHCP Menu")
            await page.select_option('select[name="BootServer"]', "Static")
            await page.click('input[type="submit"]')

            print(f"Provisioning server set for Poly phone at {ip_address}")
        except Exception as e:
            logging.error(f"Error provisioning Poly phone at {ip_address}: {e}")
        finally:
            await context.close()
            await browser.close()
