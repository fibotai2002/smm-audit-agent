from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AuditBase(BaseModel):
    user_id: int
    instagram_url: Optional[str] = None
    telegram_url: Optional[str] = None

class AuditCreate(AuditBase):
    pass

class AuditResponse(AuditBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ScrapeResult(BaseModel):
    source: str # instagram or telegram
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
