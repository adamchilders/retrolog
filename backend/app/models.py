# backend/app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import enum

Base = declarative_base()


class GoalCategory(enum.Enum):
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    HABITS = "habits"
    PERSONAL_DEVELOPMENT = "personal_development"
    RELATIONSHIPS = "relationships"
    CAREER = "career"
    FINANCE = "finance"
    OTHER = "other"


class GoalStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    entries = relationship("JournalEntry", back_populates="owner")
    goals = relationship("Goal", back_populates="owner")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    time_block = Column(String(255)) # Morning, Lunch, Evening

    owner = relationship("User", back_populates="entries")
    answers = relationship("Answer", back_populates="entry")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    question = Column(String(255))
    content = Column(String(2048)) # Increased length for content

    entry = relationship("JournalEntry", back_populates="answers")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(Enum(GoalCategory), default=GoalCategory.OTHER)
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    target_frequency = Column(String(50))  # daily, weekly, monthly
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="goals")
    progress_entries = relationship("GoalProgress", back_populates="goal")


class GoalProgress(Base):
    __tablename__ = "goal_progress"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"))
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    progress_note = Column(Text)
    rating = Column(Integer)  # 1-5 scale for how well they did on this goal

    goal = relationship("Goal", back_populates="progress_entries")
    journal_entry = relationship("JournalEntry")
