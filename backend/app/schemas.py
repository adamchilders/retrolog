# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
import datetime

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

    class Config:
        from_attributes = True
