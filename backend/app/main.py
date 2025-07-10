# backend/app/main.py
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas, services
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000", # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security
SECRET_KEY = "a_very_secret_key" # In a real app, this should be in a .env file
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post("/journal-entries/", response_model=schemas.JournalEntry)
def create_journal_entry(
    entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.create_journal_entry(db=db, entry=entry, user_id=current_user.id)


@app.get("/journal-entries/", response_model=list[schemas.JournalEntry])
def read_journal_entries(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    return crud.get_journal_entries_by_user(db=db, user_id=current_user.id)


@app.get("/journal-entries/{entry_id}", response_model=schemas.JournalEntry)
def read_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_entry = crud.get_journal_entry(db=db, entry_id=entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if db_entry.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this entry")
    return db_entry

@app.get("/journal-entries/{entry_id}/insights")
def get_journal_entry_insights(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_entry = crud.get_journal_entry(db=db, entry_id=entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if db_entry.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this entry")
    
    insights = services.get_insights_from_gemini(db_entry)
    return {"insights": insights}

@app.post("/generate-questions/")
def generate_questions(
    request: schemas.QuestionRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    # Get user's active goals
    user_goals = crud.get_active_goals_by_user(db, user_id=current_user.id)
    questions = services.generate_adaptive_questions(request.past_entries, request.time_block, user_goals)
    return {"questions": questions}

@app.get("/journal-entries/insights/summary")
def get_journal_summary_insights(
    time_range: str = "weekly", # daily, weekly, monthly
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    if time_range not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid time_range. Must be daily, weekly, or monthly.")
    
    summary_insights = services.get_summary_insights(db, current_user.id, time_range)
    return {"summary_insights": summary_insights}


# Goals endpoints
@app.post("/goals/", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_goal(db=db, goal=goal, user_id=current_user.id)


@app.get("/goals/", response_model=List[schemas.Goal])
def read_goals(include_inactive: bool = False, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goals = crud.get_goals_by_user(db, user_id=current_user.id, include_inactive=include_inactive)
    return goals


@app.get("/goals/analytics", response_model=dict)
def get_goals_analytics(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get analytics for user's goals including progress trends and insights."""
    goals = crud.get_active_goals_by_user(db, user_id=current_user.id)

    analytics = {
        "total_goals": len(goals),
        "goals_by_category": {},
        "goals_by_frequency": {},
        "recent_progress": []
    }

    # Count goals by category and frequency
    for goal in goals:
        category = goal.category.value
        frequency = goal.target_frequency

        analytics["goals_by_category"][category] = analytics["goals_by_category"].get(category, 0) + 1
        analytics["goals_by_frequency"][frequency] = analytics["goals_by_frequency"].get(frequency, 0) + 1

        # Get recent progress for each goal
        recent_progress = crud.get_goal_progress_by_goal(db, goal_id=goal.id, limit=7)
        if recent_progress:
            avg_rating = sum(p.rating for p in recent_progress if p.rating) / len([p for p in recent_progress if p.rating])
            analytics["recent_progress"].append({
                "goal_id": goal.id,
                "goal_title": goal.title,
                "entries_count": len(recent_progress),
                "average_rating": round(avg_rating, 2) if recent_progress else 0
            })

    return analytics


@app.get("/goals/{goal_id}", response_model=schemas.Goal)
def read_goal(goal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    goal = crud.get_goal(db, goal_id=goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return goal


@app.put("/goals/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: int, goal: schemas.GoalUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    if db_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_goal(db=db, db_goal=db_goal, goal=goal)


@app.delete("/goals/{goal_id}", response_model=schemas.Goal)
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    if db_goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.delete_goal(db=db, db_goal=db_goal)


@app.post("/goals/{goal_id}/progress", response_model=schemas.GoalProgress)
def create_goal_progress(goal_id: int, progress: schemas.GoalProgressBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify goal ownership
    goal = crud.get_goal(db, goal_id=goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    progress_create = schemas.GoalProgressCreate(**progress.dict(), goal_id=goal_id)
    return crud.create_goal_progress(db=db, progress=progress_create)


@app.get("/goals/{goal_id}/progress", response_model=List[schemas.GoalProgress])
def read_goal_progress(goal_id: int, limit: int = 30, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify goal ownership
    goal = crud.get_goal(db, goal_id=goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return crud.get_goal_progress_by_goal(db=db, goal_id=goal_id, limit=limit)


@app.post("/journal-entries/{entry_id}/goal-progress")
def link_goal_progress_to_entry(
    entry_id: int,
    goal_progress_data: List[schemas.GoalProgressCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Link goal progress to a journal entry."""
    # Verify entry ownership
    entry = crud.get_journal_entry(db, entry_id=entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    progress_entries = []
    for progress_data in goal_progress_data:
        # Verify goal ownership
        goal = crud.get_goal(db, goal_id=progress_data.goal_id)
        if goal is None or goal.owner_id != current_user.id:
            continue  # Skip invalid goals

        progress = crud.create_goal_progress(db=db, progress=progress_data, journal_entry_id=entry_id)
        progress_entries.append(progress)

    return {"created_progress_entries": len(progress_entries), "entries": progress_entries}

@app.put("/journal-entries/{entry_id}", response_model=schemas.JournalEntry)
def update_journal_entry(
    entry_id: int,
    entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    db_entry = crud.get_journal_entry(db=db, entry_id=entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if db_entry.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this entry")
    return crud.update_journal_entry(db=db, db_entry=db_entry, entry=entry)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
