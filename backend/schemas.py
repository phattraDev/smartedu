"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# --- Classes ---
class ClassCreate(BaseModel):
    name: str
    code: str


class ClassOut(BaseModel):
    id: int
    name: str
    code: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Homework ---
class HomeworkCreate(BaseModel):
    class_code: str
    subject: str
    description: str
    due_date: str
    submitted_by: str


class HomeworkOut(BaseModel):
    id: int
    subject: str
    description: str
    due_date: str
    submitted_by: str
    file_name: Optional[str]
    file_url: Optional[str]   # full download URL, built by the API
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Holidays ---
class HolidayCreate(BaseModel):
    title: str
    start_date: str
    end_date: str
    reason: Optional[str] = None


class HolidayOut(BaseModel):
    id: int
    title: str
    start_date: str
    end_date: str
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Subscribers ---
class SubscriberUpsert(BaseModel):
    telegram_id: str
    first_name: Optional[str] = None
    username: Optional[str] = None
    class_code: Optional[str] = None


class SubscriberOut(BaseModel):
    id: int
    telegram_id: str
    first_name: Optional[str]
    username: Optional[str]
    is_active: bool
    class_code: Optional[str]
    language: str = "en"
    subscribed_at: datetime

    model_config = {"from_attributes": True}


class SubscriberSetClass(BaseModel):
    telegram_id: str
    class_code: str


class SubscriberSetLanguage(BaseModel):
    language: str  # "en" or "km"


# --- Broadcast ---
class BroadcastRequest(BaseModel):
    message: str


class BroadcastResult(BaseModel):
    sent_to: int
    message: str
