import json

import pytest
import toml

from dhcp_notify import config as dhcp_notify_config

from . import prune_config


class TestSMTPHostConfig:
    @pytest.mark.parametrize(
        "smtp_host", ["smtp.example1.test", "smtp.example2.test"], scope="class",
    )
    def test_smtp_host(self, smtp_host, loaded_config):
        assert loaded_config.smtp.host == smtp_host


class TestSMTPPortConfig:
    @pytest.mark.parametrize("smtp_port", ["587", "465", "25"], scope="class")
    def test_smtp_port(self, smtp_port, loaded_config):
        assert loaded_config.smtp.port == smtp_port


class TestSMTPTLSConfig:
    @pytest.mark.parametrize(
        "smtp_tls_setting", ["tls", "starttls", "off"], scope="class",
    )
    def test_smtp_tls(self, smtp_tls_setting, loaded_config):
        assert loaded_config.smtp.tls.value == smtp_tls_setting


class TestSMTPUserConfig:
    @pytest.mark.parametrize(
        "smtp_user", ["user@example.com", "user-test"], scope="class",
    )
    def test_smtp_username(self, smtp_user, loaded_config):
        assert loaded_config.smtp.credentials.username == smtp_user


class TestSMTPPasswordConfig:
    @pytest.mark.parametrize(
        "smtp_password", ["53cr37%", "secret"], scope="class",
    )
    def test_smtp_password(self, smtp_password, loaded_config):
        assert loaded_config.smtp.credentials.password == smtp_password


class TestMessageFromAddrConfig:
    @pytest.mark.parametrize(
        "from_addr",
        ["test-from@example.test", "DHCP Test <test-from@example.test>"],
        scope="class",
    )
    def test_message_from_addr(self, from_addr, loaded_config):
        assert loaded_config.message.from_addr == from_addr


class TestMessageToAddrConfig:
    @pytest.mark.parametrize(
        "to_addr",
        ["test-to@example.test", "DHCP Test <test-to@example.test>"],
        scope="class",
    )
    def test_message_to_addr(self, to_addr, loaded_config):
        assert loaded_config.message.to_addr == to_addr


class TestMessageSubjectConfig:
    @pytest.mark.parametrize(
        "subject", ["Testing", "Test 123", "Thıß is a teṣt"], scope="class",
    )
    def test_message_subject(self, subject, loaded_config):
        assert loaded_config.message.subject == subject


class TestIgnoreMACsConfig:
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
    def test_ignore_macs(self, ignore_macs, expected_macs, loaded_config):
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
    def test_raises_for_missing(self, config_path):
        with pytest.raises(dhcp_notify_config.ConfigError) as e:
            dhcp_notify_config.load(str(config_path))

        missing = ", ".join(self.required)
        assert e.match(
            f"{self.cfg_class}: missing values for required fields: {missing}"
        )


class TestSMTPCredentialsConfigRequired(RequiredConfigTestBase):
    required = ["username", "password"]
    cfg_class = "Credentials"

    @pytest.fixture(scope="class")
    def smtp_credentials(self, smtp_credentials):
        return prune_config(smtp_credentials, *self.required)


class TestSMTPConfigRequired(RequiredConfigTestBase):
    required = ["host"]
    cfg_class = "SMTPConfig"

    @pytest.fixture(scope="class")
    def smtp_config(self, smtp_config):
        return prune_config(smtp_config, *self.required)


class TestMessageConfigRequired(RequiredConfigTestBase):
    required = ["from_addr", "to_addr"]
    cfg_class = "MessageConfig"

    @pytest.fixture(scope="class")
    def message_config(self, message_config):
        return prune_config(message_config, *self.required)


class TestTopLevelConfigRequired(RequiredConfigTestBase):
    required = ["smtp", "message"]
    cfg_class = "Config"

    @pytest.fixture(scope="class")
    def config(self, config):
        return prune_config(config, *self.required)


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
