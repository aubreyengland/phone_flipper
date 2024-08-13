import configparser
import os
import csv
import logging
import configparser
import importlib
import subprocess
import argparse
import sys
from playwright.async_api import async_playwright
from pathlib import Path
import platform
import asyncio

# Path to your CSV file and credentials file
csv_file_path = "phones.csv"
creds_file_path = "phone_creds.cfg"
config_file_path = "config.cfg"

# Load the configuration file
config = configparser.ConfigParser()
config.read(config_file_path)

# Set PLAYWRIGHT_BROWSERS_PATH environment variable from config file
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = config.get(
    "Paths",
    "PLAYWRIGHT_BROWSERS_PATH",
    fallback="C:/Users/Admin/AppData/Local/ms-playwright/",
)

# Read the headless setting from the config file and convert it to a boolean
headless = config.getboolean("Settings", "headless", fallback=True)


def read_credentials(file_path):
    credentials = configparser.ConfigParser()
    credentials.read(file_path)
    return credentials


# Function to read IP addresses from CSV file
def read_ip_addresses_from_csv(file_path):
    ip_addresses = []
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            ip_addresses.append(
                (
                    row["ip_address"],
                    row["phone_model"],
                    row["phone_type"],
                    row["destination"],
                )
            )
    return ip_addresses


# Function to check connectivity
def check_connectivity(ip_address):
    try:
        # Determine the ping command and parameters based on the OS
        param = "-n" if platform.system().lower() == "windows" else "-c"

        response = subprocess.run(
            ["ping", param, "1", ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Return True if the ping was successful (return code 0)
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Error pinging IP address {ip_address}: {e}")
        return False


# Function to determine provisioning URL based on destination and model
def get_provisioning_url(destination, phone_model, phone_type):
    base_urls = {
        "Zoom": {
            "Polycom": "https://provpp.zoom.us/api/v2/pbx/provisioning/",
            "Yealink": "https://yp.zoom.us/provisioning/yealink/$PN",
        },
        "Ringcentral": {
            "Polycom": "https://pp.ringcentral.com/pp",
            "Yealink": "https://yp.ringcentral.com/provisioning/yealink/$PN",
        },
        "Other": {
            "Polycom": "https://other-provisioning-url.com/",
            "Yealink": "https://other-provisioning-url.com/yealink/$PN",
        },
    }

    supported_yealink_models = [
        "T21P",
        "T33G",
        "T42S",
        "T46S",
        "T48S",
        "T57W",
        "W52P",
        "W56P",
        "W56H",
        "W60P",
        "T31P",
        "T43U",
        "T46U",
        "T48U",
        "T53",
        "T53W",
        "T54W",
        "CP930W",
    ]

    phone_type = phone_type.lower().capitalize()
    model_type = (
        "Yealink" if phone_model.upper() in supported_yealink_models else phone_type
    )

    if destination == "Zoom" and phone_type.lower() == "polycom":
        return f"{base_urls['Zoom']['Polycom']}{phone_model}"

    return base_urls.get(destination, base_urls["Other"]).get(
        model_type, "https://default-provisioning-url.com/"
    )


async def execute_action(
    action, phone_type, ip, username, password, provisioning_server_address, log_file
):
    async with async_playwright() as p:
        if check_connectivity(ip):
            try:
                if phone_type.lower() == "polycom":
                    module = importlib.import_module("phone_flipper.polycom")
                    if action == "factory_reset":
                        await module.polycom_factory_reset(
                            ip, password, log_file, headless
                        )
                    elif action == "provision":
                        await module.polycom_provision(
                            ip,
                            password,
                            provisioning_server_address,
                            log_file,
                            headless,
                        )
                    else:
                        print(f"Unsupported action: {action}")
                elif phone_type.lower() == "yealink":
                    module = importlib.import_module("phone_flipper.yealink")
                    if action == "factory_reset":
                        await module.factory_reset(ip, password, log_file, headless)
                    elif action == "provision":
                        await module.provision(
                            ip,
                            password,
                            provisioning_server_address,
                            log_file,
                            headless,
                        )
                    else:
                        print(f"Unsupported action: {action}")
                elif phone_type.lower() == "cisco":
                    module = importlib.import_module("phone_flipper.cisco")
                    if action == "factory_reset":
                        await module.factory_reset(
                            ip, username, password, log_file, headless
                        )
                    elif action == "provision":
                        await module.provision(
                            ip,
                            username,
                            password,
                            provisioning_server_address,
                            log_file,
                            headless,
                        )
                    else:
                        print(f"Unsupported action: {action}")
                else:
                    raise ImportError(f"Unsupported model: {phone_type}")
            except Exception as e:
                logging.basicConfig(
                    filename="main_errors.log",
                    level=logging.ERROR,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                )
                logging.error(f"Unexpected error for phone at {ip} ({phone_type}): {e}")
                print(f"Unexpected error for phone at {ip} ({phone_type}): {e}")
        else:
            logging.basicConfig(
                filename=log_file,
                level=logging.ERROR,
                format="%(asctime)s:%(levelname)s:%(message)s",
            )
            logging.error(f"Cannot reach IP address {ip}, skipping...")
            print(f"Cannot reach IP address {ip}, skipping...")


async def main():
    parser = argparse.ArgumentParser(description="Phone management tool")
    parser.add_argument(
        "action", choices=["factory_reset", "provision"], help="Action to perform"
    )
    parser.add_argument("--ip", help="IP address of the phone", required=False)
    parser.add_argument("--username", help="Username for the phone", required=False)
    parser.add_argument("--password", help="Password for the phone", required=False)
    parser.add_argument(
        "--csv",
        help="Path to the CSV file with phone details",
        required=False,
        default=csv_file_path,
    )

    args = parser.parse_args()

    ip_addresses = read_ip_addresses_from_csv(args.csv)
    credentials = read_credentials(creds_file_path)

    tasks = []
    for ip, phone_model, phone_type, destination in ip_addresses:
        log_file = f"{phone_type.lower()}_errors.log"
        provisioning_server_address = get_provisioning_url(
            destination, phone_model, phone_type
        )

        task = execute_action(
            args.action,
            phone_type,
            ip,
            credentials["DEFAULT"].get(f"{phone_type.lower()}_username"),
            credentials["DEFAULT"].get(f"{phone_type.lower()}_current_password"),
            provisioning_server_address,
            log_file,
        )
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
