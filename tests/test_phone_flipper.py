import pytest
import csv
import configparser
from phone_flipper import (
    read_ip_addresses_from_csv,
    read_credentials,
    get_provisioning_url,
    check_connectivity,
)

# Sample CSV and credentials data
sample_csv_data = """ip_address,phone_model,phone_type,destination
192.168.1.10,vvx350,Polycom,Zoom
192.168.1.11,T54W,Yealink,Ringcentral
192.168.1.12,T46U,Yealink,Other
"""

sample_creds_data = """
[DEFAULT]
polycom_username = default
polycom_password = 789789
yealink_username = admin
yealink_password = 789789
cisco_username = TBD
cisco_password = TBD
"""


def test_read_ip_addresses_from_csv(tmp_path):
    # Create a temporary CSV file
    csv_file = tmp_path / "phones.csv"
    csv_file.write_text(sample_csv_data)

    # Read the CSV file
    ip_addresses = read_ip_addresses_from_csv(csv_file)

    # Check if the data is read correctly
    assert ip_addresses == [
        ("192.168.1.10", "vvx350", "Polycom", "Zoom"),
        ("192.168.1.11", "T54W", "Yealink", "Ringcentral"),
        ("192.168.1.12", "T46U", "Yealink", "Other"),
    ]


def test_read_credentials(tmp_path):
    # Create a temporary credentials file
    creds_file = tmp_path / "phone_creds.cfg"
    creds_file.write_text(sample_creds_data)

    # Read the credentials file
    credentials = read_credentials(creds_file)

    # Check if the credentials are read correctly
    assert credentials["DEFAULT"]["polycom_username"] == "default"
    assert credentials["DEFAULT"]["polycom_password"] == "789789"
    assert credentials["DEFAULT"]["yealink_username"] == "admin"
    assert credentials["DEFAULT"]["yealink_password"] == "789789"


def test_get_provisioning_url():
    # Check if the correct provisioning URL is returned based on destination and model
    assert (
        get_provisioning_url("Zoom", "vvx350", "Polycom")
        == "https://provpp.zoom.us/api/v2/pbx/provisioning/"
    )
    assert (
        get_provisioning_url("Ringcentral", "T54W", "Yealink")
        == "https://yp.ringcentral.com/provisioning/yealink/$PN"
    )
    assert (
        get_provisioning_url("Ringcentral", "vvx250", "Polycom")
        == "https://pp.ringcentral.com/pp"
    )


def test_check_connectivity(monkeypatch):
    # Mock the subprocess.run function to simulate connectivity check
    def mock_run(*args, **kwargs):
        class MockResponse:
            returncode = 0

        return MockResponse()

    monkeypatch.setattr("subprocess.run", mock_run)

    # Check connectivity
    assert check_connectivity("192.168.1.10") == True

    # Mock the subprocess.run function to simulate failed connectivity check
    def mock_run_fail(*args, **kwargs):
        class MockResponse:
            returncode = 1

        return MockResponse()

    monkeypatch.setattr("subprocess.run", mock_run_fail)

    # Check connectivity
    assert check_connectivity("192.168.1.10") == False
