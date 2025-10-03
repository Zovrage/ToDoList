import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Пример простой функции отправки email через SMTP

def send_email(to_email: str, subject: str, body: str, smtp_server: str, smtp_port: int, smtp_user: str, smtp_password: str):
    print(f"[send_email] Попытка отправить письмо на {to_email} через {smtp_server}:{smtp_port} от {smtp_user}")
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("[send_email] Письмо успешно отправлено!")
    except Exception as e:
        print(f"[send_email] Ошибка отправки: {e}")
        raise
