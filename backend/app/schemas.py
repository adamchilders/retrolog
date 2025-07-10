# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
import datetime
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AnswerBase(BaseModel):
    question: str
    content: str

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int

    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    time_block: str

class JournalEntryCreate(JournalEntryBase):
    answers: List[AnswerCreate]

class JournalEntry(JournalEntryBase):
    id: int
    timestamp: datetime.datetime
    owner_id: int
    answers: List[Answer] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    entries: List[JournalEntry] = []
    goals: List["Goal"] = []

    class Config:
        from_attributes = True


# Goal Schemas
class GoalCategoryEnum(str, Enum):
    HEALTH = "health"
    PRODUCTIVITY = "productivity"
    HABITS = "habits"
    PERSONAL_DEVELOPMENT = "personal_development"
    RELATIONSHIPS = "relationships"
    CAREER = "career"
    FINANCE = "finance"
    OTHER = "other"


class GoalStatusEnum(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: GoalCategoryEnum = GoalCategoryEnum.OTHER
    target_frequency: Optional[str] = "daily"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[GoalCategoryEnum] = None
    status: Optional[GoalStatusEnum] = None
    target_frequency: Optional[str] = None
    is_active: Optional[bool] = None


class Goal(GoalBase):
    id: int
    owner_id: int
    status: GoalStatusEnum
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_active: bool
    progress_entries: List["GoalProgress"] = []

    class Config:
        from_attributes = True


# Goal Progress Schemas
class GoalProgressBase(BaseModel):
    progress_note: Optional[str] = None
    rating: Optional[int] = None


class GoalProgressCreate(GoalProgressBase):
    goal_id: int


class GoalProgress(GoalProgressBase):
    id: int
    goal_id: int
    journal_entry_id: Optional[int] = None
    date: datetime.datetime

    class Config:
        from_attributes = True


# Question generation request schema
class QuestionRequest(BaseModel):
    past_entries: List[JournalEntry]
    time_block: str


# Update User schema to include goals
User.model_rebuild()
Goal.model_rebuild()
