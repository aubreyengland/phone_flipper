import logging
from playwright.sync_api import sync_playwright


def yealink_factory_reset(ip_address, current_username, current_password, log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.ERROR,
        format="%(asctime)s:%(levelname)s:%(message)s",
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

    try:
        page.goto(f"https://{ip_address}/")
        page.fill('input[name="username"]', current_username)
        page.fill('input[name="pwd"]', current_password)
        page.click('input[type="submit"]')
        page.click("text=Settings")
        page.click("text=Upgrade")
        page.click("text=Reset to Factory Settings")
        page.click("text=OK")

        print(f"Factory reset initiated for Yealink phone at {ip_address}")
    except Exception as e:
        logging.error(f"Error resetting Yealink phone at {ip_address}: {e}")
        print(f"Error resetting Yealink phone at {ip_address}: {e}")
    finally:
        context.close()
        browser.close()


def yealink_provision(
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
        page.goto(f"https://{ip_address}/")
        page.fill('input[name="username"]', new_username)
        page.fill('input[name="pwd"]', new_password)
        page.click('input[type="submit"]')
        page.click("text=Settings")
        page.click("text=Auto Provision")
        page.select_option('select[name="ServerType"]', "HTTPS")
        page.fill('input[name="ServerURL"]', provisioning_server_address)
        page.fill('input[name="ServerUserName"]', "")
        page.fill('input[name="ServerPassword"]', "")
        page.click('input[type="submit"]')

        print(f"Provisioning server set for Yealink phone at {ip_address}")
    except Exception as e:
        logging.error(f"Error provisioning Yealink phone at {ip_address}: {e}")
        print(f"Error provisioning Yealink phone at {ip_address}: {e}")
    finally:
        context.close()
        browser.close()
