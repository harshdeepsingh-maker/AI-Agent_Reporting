from __future__ import annotations
import os, smtplib, ssl
from typing import List, Optional, Dict, Tuple, Union
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate, make_msgid

# --- Hard-coded Gmail SMTP (as requested) ---
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "reach.harshdeepsingh@gmail.com"
SMTP_PASS = "dgdm xwpb gpoc edgx"  # 16-char Gmail App Password (spaces allowed)
EMAIL_FROM = "reach.harshdeepsingh@gmail.com"
EMAIL_TO   = "reach.harshdeepsingh@gmail.com"

AttachmentItem = Union[Dict, Tuple[str, str], Tuple[str, str, str]]

def _normalize_attachment(att: AttachmentItem):
    """
    Accept:
      - dict: {"path": ..., "cid": ..., "name": ...}
      - 3-tuple: (path, cid, name)
      - 2-tuple: (path, cid)  -> name = basename(path)
    Returns (path, cid, name) or None if invalid.
    """
    if isinstance(att, dict):
        path = att.get("path")
        cid  = att.get("cid")
        name = att.get("name") or (os.path.basename(path) if path else None)
        if path and cid:
            return path, cid, name
        return None

    if isinstance(att, (tuple, list)):
        if len(att) == 3:
            path, cid, name = att
            return path, cid, name
        elif len(att) == 2:
            path, cid = att
            return path, cid, os.path.basename(path)
        else:
            return None

    return None

def send_email(subject: str, html: str, attachments: Optional[List[AttachmentItem]] = None):
    """
    Sends an HTML email via Gmail SMTP with inline image attachments referenced by cid.
    If SMTP fails, writes an .eml to outbox/ as a fallback.
    """
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alt)

    for att in (attachments or []):
        norm = _normalize_attachment(att)
        if not norm:
            continue
        path, cid, name = norm
        if not path or not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            if cid:
                img.add_header("Content-ID", f"<{cid}>")
            img.add_header("Content-Disposition", "inline", filename=name)
            msg.attach(img)

    # Try SMTP; on failure, fall back to .eml
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception:
        out_dir = os.path.join("outbox")
        os.makedirs(out_dir, exist_ok=True)
        safe_subj = "".join(ch if ch not in '<>:"/\\|?*' else "_" for ch in subject)
        eml_path = os.path.join(out_dir, f"{safe_subj}.eml")
        with open(eml_path, "wb") as f:
            f.write(msg.as_bytes())
        return False
