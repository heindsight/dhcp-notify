from email.message import EmailMessage
from unittest.mock import call

import pytest

from dhcp_notify import email_notify

from .. import prune_config


SMTP_CLASS = {"off": "SMTP", "starttls": "SMTP", "tls": "SMTP_SSL"}


@pytest.fixture(scope="class")
def email():
    return EmailMessage()


@pytest.fixture(autouse=True)
def mock_smtp_lib(mocker):
    return mocker.patch("dhcp_notify.email_notify.smtplib", autospec=True)


@pytest.fixture(scope="class", params=["off", "starttls", "tls"])
def smtp_tls_setting(request):
    return request.param


@pytest.fixture(scope="class", params=("credentials", None), ids=["Anon", "Login"])
def smtp_config(smtp_config, request):
    return prune_config(smtp_config, request.param)


@pytest.fixture
def smtp_class(mock_smtp_lib, smtp_tls_setting):
    return getattr(mock_smtp_lib, SMTP_CLASS[smtp_tls_setting])


@pytest.fixture
def smtp(smtp_class):
    return smtp_class.return_value


@pytest.fixture
def smtp_context(smtp):
    return smtp.__enter__.return_value


@pytest.fixture(autouse=True)
def send_email(loaded_config, email, mock_smtp_lib):
    email_notify.send_email(loaded_config.smtp, email)


def test_sends_email(smtp_context, email):
    assert smtp_context.mock_calls[-1] == call.send_message(email)


class TestLogin:
    @pytest.fixture(
        scope="class",
        params=(
            pytest.param("credentials", id="Anon", marks=pytest.mark.xfail),
            pytest.param(None, id="Login"),
        ),
    )
    def smtp_config(self, smtp_config, request):
        return prune_config(smtp_config, request.param)

    def test_login(self, smtp_context):
        assert (
            call.login(user="test-user", password="test-password")
            in smtp_context.mock_calls
        )


class TestStartTLS:
    @pytest.fixture(
        scope="class",
        params=(
            pytest.param("off", marks=pytest.mark.xfail),
            pytest.param("starttls"),
            pytest.param("tls", marks=pytest.mark.xfail),
        ),
    )
    def smtp_tls_setting(self, request):
        return request.param

    def test_start_tls(self, smtp_context):
        assert smtp_context.mock_calls[0] == call.starttls()
