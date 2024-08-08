import logging
from playwright.sync_api import sync_playwright


def factory_reset(ip_address, current_password, log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    browser = sync_playwright().start().chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    try:
        page.goto(f"https://{ip_address}/login.htm")
        page.fill('input[name="password"]', current_password)
        page.click('input[type="submit"]')
        page.click("text=Utilities")
        page.click("text=Phone Backup & Restore")
        page.click("text=Global Settings")
        page.click('input[name="RestoreToFacrotyBtn"]')
        page.click("button#popupbtn0")

        print(f"Factory reset initiated for Poly phone at {ip_address}")
    except Exception as e:
        logging.error(f"Error resetting Poly phone at {ip_address}: {e}")
        print(f"Error resetting Poly phone at {ip_address}: {e}")
    finally:
        context.close()
        browser.close()


def provision(
    ip_address, new_username, new_password, provisioning_server_address, log_file
):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    browser = sync_playwright().start().chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    try:
        page.goto(f"https://{ip_address}/login.htm")
        page.fill('input[name="username"]', new_username)
        page.fill('input[name="password"]', new_password)
        page.click('input[type="submit"]')
        page.click("text=Settings")
        page.click("text=Provisioning Server")
        page.select_option('select[name="ServerType"]', "HTTPS")
        page.fill('input[name="ServerAddress"]', provisioning_server_address)
        page.fill('input[name="ServerUser"]', "")
        page.fill('input[name="ServerPassword"]', "")
        page.click("text=DHCP Menu")
        page.select_option('select[name="BootServer"]', "Static")
        page.click('input[type="submit"]')

        print(f"Provisioning server set for Poly phone at {ip_address}")
    except Exception as e:
        logging.error(f"Error provisioning Poly phone at {ip_address}: {e}")
        print(f"Error provisioning Poly phone at {ip_address}: {e}")
    finally:
        context.close()
        browser.close()
