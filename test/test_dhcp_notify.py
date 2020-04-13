from unittest.mock import call

import pytest

import dhcp_notify


@pytest.fixture
def patch_config_path(mocker, config_path):
    return mocker.patch("dhcp_notify.CONFIG_PATH", new=str(config_path))


@pytest.fixture
def mock_email_notify(mocker):
    return mocker.patch("dhcp_notify.email_notify", autospec=True)


@pytest.fixture
def mock_send_email(mock_email_notify):
    return mock_email_notify.send_email


@pytest.fixture
def mock_make_email(mock_email_notify):
    return mock_email_notify.make_email


@pytest.fixture
def patch_sys_args(monkeypatch, cmdline):
    with monkeypatch.context() as m:
        yield m.setattr("sys.argv", ["dhcp-notify", *cmdline.split()])


@pytest.fixture
def run_script(patch_config_path, patch_sys_args, mock_email_notify, config_file):
    dhcp_notify.main()


def test_config_path():
    assert dhcp_notify.CONFIG_PATH == "/etc/dhcp_notify.toml"


class TestDHCPNotification:
    @pytest.fixture(
        scope="class",
        params=[
            "add 2d:29:0e:1d:d1:03 192.0.2.11",
            "old 2d:29:0e:1d:d1:03 192.0.2.11",
            "del 2d:29:0e:1d:d1:03 192.0.2.11",
            "add 7D:0e:60:8C:81:13 192.0.2.13 test-host",
            "old 7D:0e:60:8C:81:13 192.0.2.13 test-host",
            "del 7D:0e:60:8C:81:13 192.0.2.13 test-host",
        ],
    )
    def cmdline(self, request):
        return request.param

    def test_composes_email(
        self, run_script, mock_make_email, loaded_config, cmdline,
    ):
        assert mock_make_email.call_args_list == [
            call(msg_config=loaded_config.message, msg_text=cmdline),
        ]

    def test_sends_email(
        self, run_script, mock_make_email, mock_send_email, loaded_config,
    ):
        assert mock_send_email.call_args_list == [
            call(smtp_config=loaded_config.smtp, message=mock_make_email.return_value),
        ]


class IgnoreEventTestBase:
    def test_no_message_composed(self, run_script, mock_make_email):
        assert mock_make_email.call_args_list == []

    def test_no_message_sent(self, run_script, mock_send_email):
        assert mock_send_email.call_args_list == []


class TestIgnoreMACs(IgnoreEventTestBase):
    @pytest.fixture(scope="class")
    def ignore_macs(self):
        return [
            "67:ad:98:cd:56:71",
            "C2:02:EA:34:23:D0",
            "96:56:A2:C3:B8:16",
        ]

    @pytest.fixture(scope="class", params=range(3))
    def mac_address(self, ignore_macs, request):
        return ignore_macs[request.param]

    @pytest.fixture(scope="class")
    def cmdline(self, mac_address):
        return f"add {mac_address} 192.0.2.13 test-host"


class TestIgnoreActions(IgnoreEventTestBase):
    @pytest.fixture(scope="class", params=["add", "del", "old"])
    def action(self, request):
        return request.param

    @pytest.fixture(scope="class")
    def cmdline(self, action):
        return f"{action} 7D:0e:60:8C:81:13 192.0.2.13 test-host"

    @pytest.fixture(scope="class")
    def ignore_actions(self, action):
        return [action]
