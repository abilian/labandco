from __future__ import annotations

from typing import Dict

from flask import g, request
from flask_mail import Mail, Message
from jsonrpcserver import method
from werkzeug import exceptions


@method
def send_message(mail: Mail) -> Dict[str, str]:
    message_body = request.json.get("message")

    if not message_body:
        raise exceptions.BadRequest()

    mail.send(make_message(message_body))
    return {"status": "ok"}


def make_message(body: str) -> Message:
    subject = "Message reçu sur Lab&co"
    sender = "direction.recherche@upmc.fr"
    body = f"Message de: {g.current_user.email}\n\n{body}\n"
    html_body = f"<pre>{body}</pre>"
    recipients = ["direction.recherche@upmc.fr"]
    return Message(
        subject, recipients=recipients, sender=sender, body=body, html=html_body
    )
