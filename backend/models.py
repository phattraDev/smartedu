from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Class(Base):
    """A school class/grade, e.g. 'Grade 5A'."""
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g. "5A"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    homework = relationship("Homework", back_populates="class_", cascade="all, delete-orphan")


class Homework(Base):
    """Homework entry submitted by a teacher for a specific class."""
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(String(50), nullable=False)
    submitted_by = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=True)   # original filename e.g. "worksheet.pdf"
    file_path = Column(String(500), nullable=True)   # path on disk
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    class_ = relationship("Class", back_populates="homework")


class Holiday(Base):
    """School holiday or closure entry."""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    start_date = Column(String(50), nullable=False)   # e.g. "2026-06-01"
    end_date = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Subscriber(Base):
    """Telegram users (parents) who have started the bot."""
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    class_code = Column(String(20), nullable=True)   # child's registered class
    language = Column(String(5), default="en", nullable=False)  # "en" or "km"
    subscribed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BroadcastLog(Base):
    """Log of broadcast messages sent by admins."""
    __tablename__ = "broadcast_logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    sent_by = Column(String(100), nullable=False)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    recipient_count = Column(Integer, default=0)
