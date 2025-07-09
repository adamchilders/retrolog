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
    past_entries: list[schemas.JournalEntry],
    time_block: str,
    current_user: schemas.User = Depends(get_current_user),
):
    questions = services.generate_adaptive_questions(past_entries, time_block)
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
