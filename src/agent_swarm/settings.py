from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATA_SOURCE: str = "http"
    HTTP_BASE_URL: str = "http://127.0.0.1:8001"
    REPORT_TIMEZONE: str = "Asia/Kolkata"

    # Email – hardcoded for Gmail
    EMAIL_TO: str   = "reach.harshdeepsingh@gmail.com"
    EMAIL_FROM: str = "reach.harshdeepsingh@gmail.com"
    SMTP_HOST: str  = "smtp.gmail.com"
    SMTP_PORT: int  = 587
    SMTP_USER: str  = "reach.harshdeepsingh@gmail.com"
    SMTP_PASS: str  = "dgdmxwpbgpocedgx"   # 🔑 your 16-char App Password here
SETTINGS = Settings()
