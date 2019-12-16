from __future__ import annotations

from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from werkzeug import exceptions

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain.models.faq import FaqEntry
from labster.security import get_current_profile


@method
def send_message(message):
    mail = injector.get(Mail)
    current_profile = get_current_profile()

    if not message:
        raise exceptions.BadRequest()

    mail.send(make_message(message, current_profile))


@method
def view_entry(id: int):
    db = injector.get(SQLAlchemy)

    entry: FaqEntry = FaqEntry.query.get(id)
    entry.view_count = (entry.view_count or 0) + 1
    db.session.commit()


def make_message(body: str, user: Profile) -> Message:
    subject = "Message reçu sur Lab&co"
    sender = "direction.recherche@upmc.fr"
    body = f"Message de: {user.email}\n\n{body}\n"
    html_body = f"<pre>{body}</pre>"
    recipients = ["direction.recherche@upmc.fr"]
    return Message(
        subject, recipients=recipients, sender=sender, body=body, html=html_body
    )
