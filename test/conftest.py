import pytest
import toml

from dhcp_notify import config as dhcp_notify_config


@pytest.fixture(scope="class")
def smtp_credentials():
    return {
        "username": "test-user",
        "password": "test-password",
    }


@pytest.fixture(scope="class")
def smtp_tls_setting():
    return "off"


@pytest.fixture(scope="class")
def smtp_config(smtp_credentials, smtp_tls_setting):
    return {
        "host": "smtp.example.test",
        "port": "25",
        "tls": smtp_tls_setting,
        "credentials": smtp_credentials,
    }


@pytest.fixture(scope="class")
def message_config():
    return {
        "from_addr": "Test <test-from@example.test>",
        "to_addr": "Test <test-to@example.test>",
        "subject": "Test Subject",
    }


@pytest.fixture(scope="class")
def ignore_macs():
    return [
        "67:ad:98:cd:56:71",
        "2a:15:ed:3a:6a:47",
        "28:84:1E:e7:29:91",
        "C2:02:EA:34:23:D0",
        "96:56:A2:C3:B8:16",
    ]


@pytest.fixture(scope="class")
def config(smtp_config, message_config, ignore_macs):
    return {
        "smtp": smtp_config,
        "message": message_config,
        "ignore_macs": ignore_macs,
    }


@pytest.fixture(scope="class")
def tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("etc")


@pytest.fixture(scope="class")
def config_path(tmp_path):
    return tmp_path / "dhcp_notify_test.toml"


@pytest.fixture(scope="class")
def config_file(config, config_path):
    with open(config_path, "w") as stream:
        toml.dump(config, stream)


@pytest.fixture(scope="class")
def loaded_config(config_path, config_file):
    return dhcp_notify_config.load(str(config_path))
