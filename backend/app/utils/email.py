import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(to_email: str, verify_url: str):
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to_email,
        "subject": "Verify your Splitly account",
        "html": f"<p>Click the link below to verify your email:</p><a href='{verify_url}'>{verify_url}</a>",
    })


def send_invite_email(to_email: str, inviter_name: str, invite_url: str):
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": to_email,
        "subject": f"{inviter_name} invited you to Splitly",
        "html": f"<p>{inviter_name} has invited you to join Splitly.</p><a href='{invite_url}'>Accept Invite</a>",
    })


def send_expense_notification(to_emails: list[str], expense_title: str, total: float, paid_by_name: str):
    for email in to_emails:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": f"New expense: {expense_title}",
            "html": f"<p>{paid_by_name} added an expense: <strong>{expense_title}</strong> for ₹{total}.</p>",
        })


def send_settlement_notification(payer_email: str, payee_email: str, amount: float, payer_name: str):
    for email in [payer_email, payee_email]:
        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": "Settlement recorded on Splitly",
            "html": f"<p>{payer_name} settled ₹{amount}.</p>",
        })
