import imaplib
import json
import os
import smtplib

from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()


class EmailManager:
    def __init__(self) -> None:
        with open("config.json", "r") as f:
            config = json.load(f)

        self.__smtp_server = smtplib.SMTP("smtp.mail.me.com", 587)
        self.__smtp_server.starttls()
        self.__smtp_server.login(
            config["email_address"],
            os.getenv("ICLOUD_PASSWORD"),
        )

        self.__imap_client = imaplib.IMAP4_SSL("imap.mail.me.com", 993)
        self.__imap_client.login(
            config["email_address"],
            os.getenv("ICLOUD_PASSWORD"),
        )

    def send_email(self, recipient: str, subject: str, body: str) -> str:
        print(f"EmailManager.send_email: {recipient=}, {subject=}, {body=}")

        with open("config.json", "r") as f:
            config = json.load(f)

        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = config["email_address"]
        message["To"] = recipient

        try:
            self.__smtp_server.sendmail(
                config["email_address"],
                recipient,
                message.as_string(),
            )
            return "Email sent successfully."
        except Exception as e:
            print(e)
            return f"Couldn't send email: EmailManager.send_email raised an exception '{str(e)}'."

    def get_latest_emails(self) -> str:
        ...