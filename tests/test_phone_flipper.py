import pytest
import importlib
from unittest.mock import patch, MagicMock

from phone_flipper.main import (
    read_ip_addresses_from_csv,
    read_credentials,
    get_provisioning_url,
    check_connectivity,
    execute_action,
)

# Mocked data for testing
mock_csv_data = """ip_address,phone_model,phone_type,destination
10.10.20.13,vvx350,Polycom,Zoom
10.10.20.15,t54w,Yealink,Ringcentral
"""
mock_creds_data = """[DEFAULT]
polycom_current_password = 789789
yealink_username = admin
yealink_current_password = 789789
"""


@pytest.fixture
def mock_csv_file(tmp_path):
    csv_file = tmp_path / "phones.csv"
    csv_file.write_text(mock_csv_data)
    return str(csv_file)


@pytest.fixture
def mock_creds_file(tmp_path):
    creds_file = tmp_path / "phone_creds.cfg"
    creds_file.write_text(mock_creds_data)
    return str(creds_file)


def test_read_ip_addresses_from_csv(mock_csv_file):
    ip_addresses = read_ip_addresses_from_csv(mock_csv_file)
    assert len(ip_addresses) == 2
    assert ip_addresses[0] == ("10.10.20.13", "vvx350", "Polycom", "Zoom")
    assert ip_addresses[1] == ("10.10.20.15", "t54w", "Yealink", "Ringcentral")


def test_read_credentials(mock_creds_file):
    creds = read_credentials(mock_creds_file)
    assert creds["DEFAULT"]["polycom_current_password"] == "789789"
    assert creds["DEFAULT"]["yealink_username"] == "admin"
    assert creds["DEFAULT"]["yealink_current_password"] == "789789"


def test_get_provisioning_url():
    url = get_provisioning_url("Zoom", "vvx350", "Polycom")
    assert url == "https://provpp.zoom.us/api/v2/pbx/provisioning/"
    url = get_provisioning_url("Ringcentral", "t54w", "Yealink")
    assert url == "https://yp.ringcentral.com/provisioning/yealink/$PN"
    url = get_provisioning_url("Other", "vvx350", "Polycom")
    assert url == "https://other-provisioning-url.com/"


def test_check_connectivity():
    with patch("subprocess.run") as mocked_run:
        mocked_run.return_value.returncode = 0
        assert check_connectivity("10.10.20.13") == True
        mocked_run.return_value.returncode = 1
        assert check_connectivity("10.10.20.13") == False


def test_execute_action_factory_reset_polycom(monkeypatch, mock_creds_file):
    def mock_check_connectivity(ip):
        return True

    def mock_factory_reset(ip, password, log_file):
        print(f"Factory reset for {ip} with password {password}")

    monkeypatch.setattr(
        "phone_flipper.main.check_connectivity", mock_check_connectivity
    )
    monkeypatch.setattr("phone_flipper.poly.factory_reset", mock_factory_reset)

    execute_action(
        "factory_reset",
        "Polycom",
        "10.10.20.13",
        None,
        "789789",
        None,
        "polycom_errors.log",
    )


def test_execute_action_factory_reset_yealink(monkeypatch, mock_creds_file):
    def mock_check_connectivity(ip):
        return True

    def mock_factory_reset(ip, username, password, log_file):
        print(
            f"Factory reset for {ip} with username {username} and password {password}"
        )

    monkeypatch.setattr(
        "phone_flipper.main.check_connectivity", mock_check_connectivity
    )
    monkeypatch.setattr(
        "phone_flipper.yealink.yealink_factory_reset", mock_factory_reset
    )

    execute_action(
        "factory_reset",
        "Yealink",
        "10.10.20.15",
        "admin",
        "789789",
        None,
        "yealink_errors.log",
    )


# def test_execute_action_unsupported_model():
#     with pytest.raises(ImportError, match=r"Unsupported model: SomeOtherModel"):
#         execute_action(
#             "factory_reset",
#             "SomeOtherModel",
#             "192.168.1.10",
#             None,
#             "password",
#             "provisioning_url",
#             "log_file",
#         )
