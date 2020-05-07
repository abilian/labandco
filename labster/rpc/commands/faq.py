from __future__ import annotations

from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from jsonrpcserver import method
from werkzeug import exceptions

from labster.di import injector
from labster.domain2.model.profile import Profile
from labster.domain.models.faq import FaqEntry
from labster.rpc.queries.faq import check_user_can_edit
from labster.security import get_current_profile

db = injector.get(SQLAlchemy)


@method
def send_message(message):
    mail = injector.get(Mail)
    current_profile = get_current_profile()

    if not message:
        raise exceptions.BadRequest()

    mail.send(make_message(message, current_profile))


@method
def view_entry(id: int):
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


#
# Admin
#
@method
def update_faq_entry(entry):
    check_user_can_edit()

    entry_id = entry.get("id")
    if entry_id:
        faq_entry = FaqEntry.query.get_or_404(entry_id)
    else:
        faq_entry = FaqEntry()
        db.session.add(faq_entry)

    faq_entry.title = entry["title"]
    faq_entry.body = entry["body"]
    faq_entry.category = entry["category"]

    db.session.commit()


@method
def delete_faq_entry(entry):
    check_user_can_edit()

    entry_id = entry["id"]
    faq_entry = FaqEntry.query.get_or_404(entry_id)
    db.session.delete(faq_entry)
    db.session.commit()
