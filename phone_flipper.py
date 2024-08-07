import csv
import logging
import configparser
import importlib
import subprocess
import argparse
from playwright.sync_api import sync_playwright

# Path to your CSV file and credentials file
csv_file_path = "phones.csv"
creds_file_path = "phone_creds.cfg"


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


# Function to read credentials from config file
def read_credentials(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config


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

    return base_urls.get(destination, base_urls["Other"]).get(
        model_type, "https://default-provisioning-url.com/"
    )


# Function to check connectivity
def check_connectivity(ip_address):
    try:
        response = subprocess.run(
            ["ping", "-c", "1", ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Error pinging IP address {ip_address}: {e}")
        return False


def execute_action(
    action, phone_type, ip, username, password, provisioning_server_address, log_file
):
    with sync_playwright() as playwright:
        if check_connectivity(ip):
            try:
                if phone_type.lower() == "polycom":
                    module = importlib.import_module("phone_tool.poly")
                elif phone_type.lower() == "yealink":
                    module = importlib.import_module("phone_tool.yealink")
                elif phone_type.lower() == "cisco":
                    module = importlib.import_module("phone_tool.cisco")
                else:
                    print(f"Unsupported phone type: {phone_type}")
                    return

                if action == "factory_reset":
                    module.factory_reset(ip, username, password, log_file)
                elif action == "provision":
                    module.provision(
                        ip, username, password, provisioning_server_address, log_file
                    )
                else:
                    print(f"Unsupported action: {action}")

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


# Main function
def main():
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

    for ip, phone_model, phone_type, destination in ip_addresses:
        log_file = f"{phone_type.lower()}_errors.log"
        provisioning_server_address = get_provisioning_url(
            destination, phone_model, phone_type
        )

        execute_action(
            args.action,
            phone_type,
            ip,
            credentials["DEFAULT"][f"{phone_type.lower()}_username"],
            credentials["DEFAULT"][f"{phone_type.lower()}_password"],
            provisioning_server_address,
            log_file,
        )


if __name__ == "__main__":
    main()
