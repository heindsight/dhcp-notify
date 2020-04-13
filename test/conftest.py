import pytest
import toml

from dhcp_notify import config as dhcp_notify_config


@pytest.fixture(scope="class")
def smtp_host():
    return "smtp.example.test"


@pytest.fixture(scope="class")
def smtp_port():
    return "25"


@pytest.fixture(scope="class")
def smtp_tls_setting():
    return "off"


@pytest.fixture(scope="class")
def smtp_user():
    return "test-user"


@pytest.fixture(scope="class")
def smtp_password():
    return "test-password"


@pytest.fixture(scope="class")
def smtp_credentials(smtp_user, smtp_password):
    return {
        "username": smtp_user,
        "password": smtp_password,
    }


@pytest.fixture(scope="class")
def smtp_config(smtp_host, smtp_port, smtp_tls_setting, smtp_credentials):
    return {
        "host": smtp_host,
        "port": smtp_port,
        "tls": smtp_tls_setting,
        "credentials": smtp_credentials,
    }


@pytest.fixture(scope="class")
def from_addr():
    return "Test <test-from@example.test>"


@pytest.fixture(scope="class")
def to_addr():
    return "Test <test-to@example.test>"


@pytest.fixture(scope="class")
def subject():
    return "Test Subject"


@pytest.fixture(scope="class")
def message_config(from_addr, to_addr, subject):
    return {
        "from_addr": from_addr,
        "to_addr": to_addr,
        "subject": subject,
    }


@pytest.fixture(scope="class")
def ignore_macs():
    return [
        "67:ad:98:cd:56:71",
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
