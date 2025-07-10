# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import datetime
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_journal_entry(db: Session, entry: schemas.JournalEntryCreate, user_id: int):
    db_entry = models.JournalEntry(time_block=entry.time_block, owner_id=user_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    for answer_data in entry.answers:
        db_answer = models.Answer(**answer_data.dict(), entry_id=db_entry.id)
        db.add(db_answer)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def get_journal_entries_by_user(db: Session, user_id: int):
    return db.query(models.JournalEntry).filter(models.JournalEntry.owner_id == user_id).all()

def get_journal_entry(db: Session, entry_id: int):
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def get_journal_entries_by_user_and_time_range(db: Session, user_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    return db.query(models.JournalEntry).filter(
        models.JournalEntry.owner_id == user_id,
        models.JournalEntry.timestamp >= start_date,
        models.JournalEntry.timestamp <= end_date
    ).order_by(models.JournalEntry.timestamp).all()

def update_journal_entry(db: Session, db_entry: models.JournalEntry, entry: schemas.JournalEntryCreate):
    db_entry.time_block = entry.time_block
    db_entry.timestamp = datetime.datetime.utcnow() # Update timestamp on modification

    # Delete old answers
    db.query(models.Answer).filter(models.Answer.entry_id == db_entry.id).delete()
    db.commit()

    # Add new answers
    for answer_data in entry.answers:
        db_answer = models.Answer(**answer_data.dict(), entry_id=db_entry.id)
        db.add(db_answer)
    db.commit()
    db.refresh(db_entry)
    return db_entry


# Goal CRUD operations
def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int):
    db_goal = models.Goal(**goal.dict(), owner_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goals_by_user(db: Session, user_id: int, include_inactive: bool = False):
    query = db.query(models.Goal).filter(models.Goal.owner_id == user_id)
    if not include_inactive:
        query = query.filter(models.Goal.is_active == True)
    return query.order_by(models.Goal.created_at.desc()).all()


def get_goal(db: Session, goal_id: int):
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()


def update_goal(db: Session, db_goal: models.Goal, goal: schemas.GoalUpdate):
    update_data = goal.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    db_goal.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, db_goal: models.Goal):
    db_goal.is_active = False
    db_goal.status = models.GoalStatus.ARCHIVED
    db_goal.updated_at = datetime.datetime.utcnow()
    db.commit()
    return db_goal


def get_active_goals_by_user(db: Session, user_id: int):
    return db.query(models.Goal).filter(
        models.Goal.owner_id == user_id,
        models.Goal.is_active == True,
        models.Goal.status == models.GoalStatus.ACTIVE
    ).all()


# Goal Progress CRUD operations
def create_goal_progress(db: Session, progress: schemas.GoalProgressCreate, journal_entry_id: Optional[int] = None):
    db_progress = models.GoalProgress(**progress.dict(), journal_entry_id=journal_entry_id)
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


def get_goal_progress_by_goal(db: Session, goal_id: int, limit: int = 30):
    return db.query(models.GoalProgress).filter(
        models.GoalProgress.goal_id == goal_id
    ).order_by(models.GoalProgress.date.desc()).limit(limit).all()
