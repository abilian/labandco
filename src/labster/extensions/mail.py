from __future__ import annotations

import flask_mail
import html2text
from flask import current_app
from flask_mail import Message

# logger = logging.getLogger(__name__)


class Mail(flask_mail.Mail):
    def send(self, message: Message) -> None:
        config = current_app.config

        substitute_address = config.get("TEST_EMAIL_ADRESS")
        if substitute_address:
            assert isinstance(substitute_address, str)
            message.subject += f" [pour: {', '.join(message.recipients)}]"
            message.recipients = [substitute_address]
            message.cc = []
            message.bcc = []

        if not message.body:
            message.body = html2text.html2text(message.html)

        if not message.sender:
            message.sender = config["MAIL_SENDER"]

        email_cc = config.get("EMAIL_CC")
        if email_cc:
            if isinstance(email_cc, list) or isinstance(email_cc, tuple):
                message.bcc = email_cc
            else:
                assert isinstance(email_cc, str)
                message.bcc = [email_cc]

        # if message.sender and config[""]:
        #     flask_mail.Mail.send(self, message)
        flask_mail.Mail.send(self, message)
