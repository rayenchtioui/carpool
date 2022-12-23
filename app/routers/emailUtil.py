from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import settings
from jinja2 import Environment, select_autoescape, PackageLoader
from ..enums import EmailTemplate

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=587,
    MAIL_SERVER=settings.mail_server,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


async def send_email(subject: str, recipients: List, email_template: EmailTemplate, email: str, code: str):
    template_name = 'reset_pass_mail.html' if email_template == EmailTemplate.ResetPassword else 'confirm_mail.html'
    template = env.get_template(template_name)
    html = template.render(
        name=email,
        code=code,
        subject=subject
    )

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        html=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
