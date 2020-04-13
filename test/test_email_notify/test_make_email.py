import pytest

from dhcp_notify import email_notify


@pytest.fixture(scope="class")
def message_text():
    return "Test email"


@pytest.fixture(scope="class")
def email(loaded_config, message_text):
    return email_notify.make_email(loaded_config.message, message_text)


class TestMakeEmail:
    def test_email_from_address(self, email):
        assert email["From"] == "Test <test-from@example.test>"

    def test_email_to_address(self, email):
        assert email["To"] == "Test <test-to@example.test>"

    def test_email_subject(self, email):
        assert email["Subject"] == "Test Subject"

    def test_email_text(self, email):
        assert email.get_content() == "Test email\n"
