
import os
from pydantic import BaseModel, Field
from typing import Optional, List

class Settings(BaseModel):
    DATA_SOURCE: str = Field(default=os.getenv('DATA_SOURCE','file'))
    FILE_SALES_PATH: str = Field(default=os.getenv('FILE_SALES_PATH','data/sales.json'))
    FILE_MARKETING_PATH: str = Field(default=os.getenv('FILE_MARKETING_PATH','data/marketing.json'))
    HTTP_BASE_URL: str = Field(default=os.getenv('HTTP_BASE_URL','http://127.0.0.1:8000'))
    REPORT_TIMEZONE: str = Field(default=os.getenv('REPORT_TIMEZONE','Asia/Kolkata'))
    SMTP_HOST: Optional[str] = Field(default=os.getenv('SMTP_HOST'))
    SMTP_PORT: Optional[int] = Field(default=int(os.getenv('SMTP_PORT')) if os.getenv('SMTP_PORT') else None)
    SMTP_USER: Optional[str] = Field(default=os.getenv('SMTP_USER'))
    SMTP_PASS: Optional[str] = Field(default=os.getenv('SMTP_PASS'))
    EMAIL_FROM: str = Field(default=os.getenv('EMAIL_FROM','bot@example.com'))
    EMAIL_TO: List[str] = Field(default_factory=lambda: [s.strip() for s in os.getenv('EMAIL_TO','you@example.com').split(',') if s.strip()])
    OUTBOX_DIR: str = Field(default=os.getenv('OUTBOX_DIR','outbox'))
    STATE_PATH: str = Field(default=os.getenv('STATE_PATH','.state/report_state.json'))
    HISTORY_PATH: str = Field(default=os.getenv('HISTORY_PATH','.state/history.json'))
    ENABLE_CHART: bool = Field(default=os.getenv('ENABLE_CHART','1') not in ('0','false','False'))

SETTINGS=Settings()
