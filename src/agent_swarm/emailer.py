
import pathlib, re, smtplib, contextlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from .config import SETTINGS
from .logging_utils import info
def send_email(subject:str, html:str, text:str, to_addrs:List[str]):
    if SETTINGS.SMTP_HOST and SETTINGS.SMTP_PORT:
        msg=MIMEMultipart('alternative'); msg['Subject']=subject; msg['From']=SETTINGS.EMAIL_FROM; msg['To']=', '.join(to_addrs)
        msg.attach(MIMEText(text,'plain','utf-8')); msg.attach(MIMEText(html,'html','utf-8'))
        with smtplib.SMTP(SETTINGS.SMTP_HOST, SETTINGS.SMTP_PORT) as s:
            with contextlib.suppress(Exception): s.starttls()
            if SETTINGS.SMTP_USER and SETTINGS.SMTP_PASS: s.login(SETTINGS.SMTP_USER, SETTINGS.SMTP_PASS)
            s.sendmail(SETTINGS.EMAIL_FROM, to_addrs, msg.as_string())
        info('email_sent', to=to_addrs, subject=subject)
    else:
        out=pathlib.Path(SETTINGS.OUTBOX_DIR); out.mkdir(parents=True,exist_ok=True)
        safe=re.sub(r'[^A-Za-z0-9_.-]+','_',subject); (out/f'{safe}.eml').write_text(f'Subject: {subject}\nTo: {", ".join(to_addrs)}\n\n{text}\n\n---- HTML ----\n\n{html}',encoding='utf-8')
        info('email_written_to_outbox', path=str(out/f'{safe}.eml'))
