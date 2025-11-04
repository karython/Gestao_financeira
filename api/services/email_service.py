# app/services/email_service.py
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from api.core.config import settings


async def send_report_email(
    to_email: str,
    user_name: str,
    pdf_buffer: bytes,
    month: int,
    year: int
):
    message = MIMEMultipart()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = f"Relatório Financeiro - {month:02d}/{year}"
    
    body = f"""
    Olá {user_name},
    
    Segue em anexo o seu relatório financeiro do período {month:02d}/{year}.
    
    Atenciosamente,
    Sistema de Gestão Financeira
    """
    
    message.attach(MIMEText(body, "plain"))
    
    pdf_attachment = MIMEApplication(pdf_buffer, _subtype="pdf")
    pdf_attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"relatorio_{month}_{year}.pdf"
    )
    message.attach(pdf_attachment)
    
    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True
    )
