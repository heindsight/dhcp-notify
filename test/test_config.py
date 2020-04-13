import json

import pytest
import toml

from dhcp_notify import config as dhcp_notify_config

from . import prune_config


@pytest.mark.parametrize(
    "smtp_host", ["smtp.example1.test", "smtp.example2.test"], scope="class",
)
def test_smtp_host(smtp_host, loaded_config):
    assert loaded_config.smtp.host == smtp_host


@pytest.mark.parametrize("smtp_port", ["587", "465", "25"], scope="class")
def test_smtp_port(smtp_port, loaded_config):
    assert loaded_config.smtp.port == smtp_port


@pytest.mark.parametrize("smtp_tls_setting", ["tls", "starttls", "off"], scope="class")
def test_smtp_tls(smtp_tls_setting, loaded_config):
    assert loaded_config.smtp.tls.value == smtp_tls_setting


@pytest.mark.parametrize("smtp_user", ["user@example.com", "user-test"], scope="class")
def test_smtp_username(smtp_user, loaded_config):
    assert loaded_config.smtp.credentials.username == smtp_user


@pytest.mark.parametrize("smtp_password", ["53cr37%", "secret"], scope="class")
def test_smtp_password(smtp_password, loaded_config):
    assert loaded_config.smtp.credentials.password == smtp_password


@pytest.mark.parametrize(
    "from_addr",
    ["test-from@example.test", "DHCP Test <test-from@example.test>"],
    scope="class",
)
def test_message_from_addr(from_addr, loaded_config):
    assert loaded_config.message.from_addr == from_addr


@pytest.mark.parametrize(
    "to_addr",
    ["test-to@example.test", "DHCP Test <test-to@example.test>"],
    scope="class",
)
def test_message_to_addr(to_addr, loaded_config):
    assert loaded_config.message.to_addr == to_addr


@pytest.mark.parametrize(
    "subject", ["Testing", "Test 123", "Thıß is a teṣt"], scope="class",
)
def test_message_subject(subject, loaded_config):
    assert loaded_config.message.subject == subject


@pytest.mark.parametrize(
    "ignore_macs, expected_macs",
    [
        ([], []),
        (["28:84:1E:e7:29:91"], ["28:84:1e:e7:29:91"]),
        (
            ["67:ad:98:cd:56:71", "C2:02:EA:34:23:D0"],
            ["67:ad:98:cd:56:71", "c2:02:ea:34:23:d0"],
        ),
    ],
    scope="class",
)
def test_ignore_macs(ignore_macs, expected_macs, loaded_config):
    assert sorted(loaded_config.ignore_macs) == sorted(expected_macs)


class TestOptionalConfig:
    defaults = {
        "smtp_config": {
            "port": "465",
            "tls": dhcp_notify_config.SMTPTLSConfig.tls,
            "credentials": None,
        },
        "message_config": {"subject": dhcp_notify_config.DEFAULT_EMAIL_SUBJECT},
        "top_level": {"ignore_macs": ()},
    }

    @pytest.fixture(scope="class")
    def smtp_config(self, smtp_config):
        return prune_config(smtp_config, *self.defaults["smtp_config"])

    @pytest.fixture(scope="class")
    def message_config(self, message_config):
        return prune_config(message_config, *self.defaults["message_config"])

    @pytest.fixture(scope="class")
    def config(self, config):
        return prune_config(config, *self.defaults["top_level"])

    @pytest.mark.parametrize("missing, default", defaults["smtp_config"].items())
    def test_smtp_config_default(self, loaded_config, missing, default):
        assert getattr(loaded_config.smtp, missing) == default

    @pytest.mark.parametrize("missing, default", defaults["message_config"].items())
    def test_message_config_default(self, loaded_config, missing, default):
        assert getattr(loaded_config.message, missing) == default

    @pytest.mark.parametrize("missing, default", defaults["top_level"].items())
    def test_top_level_config_default(self, loaded_config, missing, default):
        assert getattr(loaded_config, missing) == default


class TestIgnoreExtraConfig:
    @pytest.fixture(scope="class")
    def smtp_credentials(self, smtp_credentials):
        return {**smtp_credentials, "extra": "ignored"}

    @pytest.fixture(scope="class")
    def smtp_config(self, smtp_config):
        return {**smtp_config, "extra": "ignored"}

    @pytest.fixture(scope="class")
    def message_config(self, message_config):
        return {**message_config, "extra": "ignored"}

    @pytest.fixture(scope="class")
    def config(self, config):
        return {**config, "extra": "ignored"}

    def test_ignore_extra_smtp_credentials(self, loaded_config):
        assert not hasattr(loaded_config.smtp.credentials, "extra")

    def test_ignore_extra_smtp_config(self, loaded_config):
        assert not hasattr(loaded_config.smtp, "extra")

    def test_ignore_extra_message_config(self, loaded_config):
        assert not hasattr(loaded_config.message, "extra")

    def test_ignore_extra_top_level_config(self, loaded_config):
        assert not hasattr(loaded_config, "extra")


class RequiredConfigTestBase:
    @pytest.mark.usefixtures("config_file")
    def test_raises_for_missing(self, config_path, cfg_class, missing):
        with pytest.raises(dhcp_notify_config.ConfigError) as e:
            dhcp_notify_config.load(str(config_path))

        missing = ", ".join(missing)
        assert e.match(f"{cfg_class}: missing values for required fields: {missing}")


class TestSMTPCredentialsConfigRequired(RequiredConfigTestBase):
    @pytest.fixture(scope="class")
    def cfg_class(self):
        return "Credentials"

    @pytest.fixture(
        params=[["username"], ["password"], ["username", "password"]], scope="class",
    )
    def missing(self, request):
        return request.param

    @pytest.fixture(scope="class")
    def smtp_credentials(self, smtp_credentials, missing):
        return prune_config(smtp_credentials, *missing)


class TestSMTPConfigRequired(RequiredConfigTestBase):
    @pytest.fixture(scope="class")
    def cfg_class(self):
        return "SMTPConfig"

    @pytest.fixture(scope="class")
    def missing(self):
        return ["host"]

    @pytest.fixture(scope="class")
    def smtp_config(self, smtp_config, missing):
        return prune_config(smtp_config, *missing)


class TestMessageConfigRequired(RequiredConfigTestBase):
    @pytest.fixture(scope="class")
    def cfg_class(self):
        return "MessageConfig"

    @pytest.fixture(
        params=[["from_addr"], ["to_addr"], ["from_addr", "to_addr"]], scope="class",
    )
    def missing(self, request):
        return request.param

    @pytest.fixture(scope="class")
    def message_config(self, message_config, missing):
        return prune_config(message_config, *missing)


class TestTopLevelConfigRequired(RequiredConfigTestBase):
    @pytest.fixture
    def cfg_class(self):
        return "Config"

    @pytest.fixture(
        params=[["smtp"], ["message"], ["smtp", "message"]], scope="class",
    )
    def missing(self, request):
        return request.param

    @pytest.fixture(scope="class")
    def config(self, config, missing):
        return prune_config(config, *missing)


class TestInvalidConfigFile:
    @pytest.fixture
    def config_file(self, config, config_path):
        with open(config_path, "w") as stream:
            json.dump(config, stream)
        yield
        config_path.unlink()

    def test_config_file_not_found(self, config_path):
        with pytest.raises(FileNotFoundError) as e:
            dhcp_notify_config.load(str(config_path))

        assert e.match(f"No such file or directory: '{config_path}'")

    @pytest.mark.usefixtures("config_file")
    def test_malformed_toml_file(self, config_path):
        with pytest.raises(toml.TomlDecodeError):
            dhcp_notify_config.load(str(config_path))
