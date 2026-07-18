from unittest.mock import call, patch

from app.utils import send_email_with_retry


def test_send_email_with_retry_retries_then_succeeds() -> None:
    with (
        patch(
            "app.utils.send_email", side_effect=[RuntimeError("smtp timeout"), None]
        ) as send_email_mock,
        patch("app.utils.time.sleep", return_value=None) as sleep_mock,
        patch("app.core.config.settings.SMTP_MAX_ATTEMPTS", 3),
        patch("app.core.config.settings.SMTP_RETRY_BACKOFF_SECONDS", 0.1),
    ):
        send_email_with_retry(
            email_to="user@example.com",
            subject="subject",
            html_content="<p>body</p>",
        )

    assert send_email_mock.call_count == 2
    sleep_mock.assert_called_once_with(0.1)


def test_send_email_with_retry_exhausts_attempts_without_raising() -> None:
    with (
        patch(
            "app.utils.send_email", side_effect=RuntimeError("smtp down")
        ) as send_email_mock,
        patch("app.utils.time.sleep", return_value=None) as sleep_mock,
        patch("app.core.config.settings.SMTP_MAX_ATTEMPTS", 3),
        patch("app.core.config.settings.SMTP_RETRY_BACKOFF_SECONDS", 0.2),
    ):
        send_email_with_retry(
            email_to="user@example.com",
            subject="subject",
            html_content="<p>body</p>",
        )

    assert send_email_mock.call_count == 3
    assert sleep_mock.call_args_list == [call(0.2), call(0.4)]
