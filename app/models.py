from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    balance = Column(Integer, default=30) # Default free tokens
    tier = Column(String, default="free") # free, pro, agency
    subscription_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audits = relationship("Audit", back_populates="user")

class Audit(Base):
    __tablename__ = "audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    instagram_url = Column(String, nullable=True)
    telegram_url = Column(String, nullable=True)
    audit_type = Column(String, default="standard") # standard, deep
    status = Column(String, default="pending") 
    collected_data_json = Column(SQLiteJSON, nullable=True)
    report_json = Column(SQLiteJSON, nullable=True)
    error_message = Column(Text, nullable=True)
    cost = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="audits")
