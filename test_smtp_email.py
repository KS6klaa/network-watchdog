from __future__ import annotations

import getpass
import json
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path


SETTINGS_PATH = Path(__file__).resolve().parent / "watchdog_settings.json"


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return {}
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def prompt_with_default(label: str, default: str = "") -> str:
    if default:
        value = input(f"{label} [{default}]: ").strip()
        return value or default
    return input(f"{label}: ").strip()


def is_valid_email(value: str) -> bool:
    parsed = parseaddr(value.strip())[1]
    return "@" in parsed and "." in parsed.rsplit("@", 1)[-1]


def send_test_email(
    smtp_host: str,
    smtp_port: int,
    sender_email: str,
    auth_code: str,
    recipient_email: str,
) -> None:
    message = EmailMessage()
    message["Subject"] = "[Network Watchdog] SMTP test"
    message["From"] = f"Network Watchdog <{sender_email}>"
    message["To"] = recipient_email
    message.set_content("This is a local SMTP test from Network Watchdog.")

    context = ssl.create_default_context()
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=20) as server:
            server.ehlo()
            server.user = sender_email
            server.password = auth_code
            server.auth("LOGIN", server.auth_login)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.user = sender_email
            server.password = auth_code
            server.auth("LOGIN", server.auth_login)
            server.send_message(message)


def main() -> None:
    settings = load_settings()
    default_recipient = str(settings.get("recipient_1", "")).strip()
    default_sender = str(settings.get("sender_email", "")).strip()
    if not is_valid_email(default_sender) and is_valid_email(default_recipient):
        default_sender = default_recipient

    print("Network Watchdog SMTP test")
    print("Use the full mailbox address as sender, for example name@qq.com.")
    print("For QQ Mail, use smtp.qq.com with port 465 and the mailbox auth code.")
    print()

    smtp_host = prompt_with_default(
        "SMTP host", str(settings.get("smtp_host", "smtp.qq.com")).strip()
    )
    smtp_port = int(
        prompt_with_default("SMTP port", str(settings.get("smtp_port", 465)).strip())
    )
    sender_email = prompt_with_default("Sender email", default_sender)
    recipient_email = prompt_with_default("Recipient email", default_recipient)

    if not is_valid_email(sender_email):
        print("ERROR: Sender email must be a full email address.")
        return
    if not is_valid_email(recipient_email):
        print("ERROR: Recipient email must be a full email address.")
        return

    saved_auth_code = str(settings.get("auth_code", "")).strip()
    if saved_auth_code:
        use_saved = input("Use saved auth code from watchdog_settings.json? [Y/n]: ").strip()
        auth_code = saved_auth_code if use_saved.lower() != "n" else ""
    else:
        auth_code = ""
    if not auth_code:
        auth_code = getpass.getpass("SMTP auth code: ").strip()

    if not auth_code:
        print("ERROR: SMTP auth code is required.")
        return

    try:
        print("Sending test email...")
        send_test_email(smtp_host, smtp_port, sender_email, auth_code, recipient_email)
    except smtplib.SMTPAuthenticationError as exc:
        print("FAILED: SMTP authentication failed.")
        print(f"Server response: {exc.smtp_code} {exc.smtp_error!r}")
        print("Check that SMTP service is enabled and that the auth code matches the sender mailbox.")
        print("For QQ Mail, generate a fresh auth code after enabling SMTP service.")
    except smtplib.SMTPConnectError as exc:
        print("FAILED: Could not connect to SMTP server.")
        print(f"Server response: {exc.smtp_code} {exc.smtp_error!r}")
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}")
    else:
        print("SUCCESS: test email sent.")


if __name__ == "__main__":
    main()
