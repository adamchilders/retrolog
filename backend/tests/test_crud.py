import pytest
from datetime import datetime, timedelta
from app import crud, models, schemas
from app.database import SessionLocal


class TestCRUDOperations:
    """Test database CRUD operations."""

    def test_create_user(self, db_session):
        """Test user creation."""
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        assert user.username == "testuser"
        assert user.id is not None
        assert user.hashed_password != "testpass"  # Should be hashed

    def test_get_user_by_username(self, db_session):
        """Test getting user by username."""
        # Create user first
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        created_user = crud.create_user(db=db_session, user=user_data)
        
        # Get user by username
        retrieved_user = crud.get_user_by_username(db=db_session, username="testuser")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_by_username_not_found(self, db_session):
        """Test getting non-existent user."""
        user = crud.get_user_by_username(db=db_session, username="nonexistent")
        assert user is None

    def test_create_journal_entry(self, db_session):
        """Test journal entry creation."""
        # Create user first
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        # Create journal entry
        entry_data = schemas.JournalEntryCreate(
            time_block="Morning",
            answers=[
                schemas.AnswerCreate(question="How are you?", content="Good"),
                schemas.AnswerCreate(question="What's your goal?", content="Learn")
            ]
        )
        
        entry = crud.create_journal_entry(db=db_session, entry=entry_data, user_id=user.id)
        
        assert entry.time_block == "Morning"
        assert entry.owner_id == user.id
        assert entry.timestamp is not None
        assert len(entry.answers) == 2
        assert entry.answers[0].question == "How are you?"
        assert entry.answers[0].content == "Good"

    def test_get_journal_entries_by_user(self, db_session):
        """Test getting journal entries for a user."""
        # Create user
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        # Create multiple entries
        for i in range(3):
            entry_data = schemas.JournalEntryCreate(
                time_block=f"Block{i}",
                answers=[schemas.AnswerCreate(question=f"Q{i}", content=f"A{i}")]
            )
            crud.create_journal_entry(db=db_session, entry=entry_data, user_id=user.id)
        
        # Get entries
        entries = crud.get_journal_entries_by_user(db=db_session, user_id=user.id)
        
        assert len(entries) == 3
        assert all(entry.owner_id == user.id for entry in entries)

    def test_get_journal_entry(self, db_session):
        """Test getting a specific journal entry."""
        # Create user and entry
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        entry_data = schemas.JournalEntryCreate(
            time_block="Morning",
            answers=[schemas.AnswerCreate(question="Test", content="Answer")]
        )
        created_entry = crud.create_journal_entry(db=db_session, entry=entry_data, user_id=user.id)
        
        # Get entry
        retrieved_entry = crud.get_journal_entry(db=db_session, entry_id=created_entry.id)
        
        assert retrieved_entry is not None
        assert retrieved_entry.id == created_entry.id
        assert retrieved_entry.time_block == "Morning"

    def test_get_journal_entry_not_found(self, db_session):
        """Test getting non-existent journal entry."""
        entry = crud.get_journal_entry(db=db_session, entry_id=999)
        assert entry is None

    def test_get_journal_entries_by_user_and_time_range(self, db_session):
        """Test getting journal entries within a time range."""
        # Create user
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        # Create entries with different timestamps
        now = datetime.utcnow()
        old_entry_data = schemas.JournalEntryCreate(
            time_block="Old",
            answers=[schemas.AnswerCreate(question="Old", content="Old")]
        )
        recent_entry_data = schemas.JournalEntryCreate(
            time_block="Recent",
            answers=[schemas.AnswerCreate(question="Recent", content="Recent")]
        )
        
        # Create old entry (manually set timestamp)
        old_entry = crud.create_journal_entry(db=db_session, entry=old_entry_data, user_id=user.id)
        old_entry.timestamp = now - timedelta(days=10)
        db_session.commit()
        
        # Create recent entry
        recent_entry = crud.create_journal_entry(db=db_session, entry=recent_entry_data, user_id=user.id)
        
        # Get entries from last week
        start_date = now - timedelta(days=7)
        end_date = now + timedelta(days=1)
        
        entries = crud.get_journal_entries_by_user_and_time_range(
            db=db_session, user_id=user.id, start_date=start_date, end_date=end_date
        )
        
        assert len(entries) == 1
        assert entries[0].time_block == "Recent"

    def test_update_journal_entry(self, db_session):
        """Test updating a journal entry."""
        # Create user and entry
        user_data = schemas.UserCreate(username="testuser", password="testpass")
        user = crud.create_user(db=db_session, user=user_data)
        
        original_entry_data = schemas.JournalEntryCreate(
            time_block="Morning",
            answers=[schemas.AnswerCreate(question="Original", content="Original")]
        )
        entry = crud.create_journal_entry(db=db_session, entry=original_entry_data, user_id=user.id)
        original_timestamp = entry.timestamp
        
        # Update entry
        updated_entry_data = schemas.JournalEntryCreate(
            time_block="Evening",
            answers=[
                schemas.AnswerCreate(question="Updated", content="Updated"),
                schemas.AnswerCreate(question="New", content="New")
            ]
        )
        
        updated_entry = crud.update_journal_entry(
            db=db_session, db_entry=entry, entry=updated_entry_data
        )
        
        assert updated_entry.time_block == "Evening"
        assert updated_entry.timestamp > original_timestamp  # Should be updated
        assert len(updated_entry.answers) == 2
        assert updated_entry.answers[0].question == "Updated"
        assert updated_entry.answers[1].question == "New"

    def test_user_entry_isolation(self, db_session):
        """Test that users can only access their own entries."""
        # Create two users
        user1_data = schemas.UserCreate(username="user1", password="pass1")
        user2_data = schemas.UserCreate(username="user2", password="pass2")
        user1 = crud.create_user(db=db_session, user=user1_data)
        user2 = crud.create_user(db=db_session, user=user2_data)
        
        # Create entries for each user
        entry1_data = schemas.JournalEntryCreate(
            time_block="User1Entry",
            answers=[schemas.AnswerCreate(question="Q1", content="A1")]
        )
        entry2_data = schemas.JournalEntryCreate(
            time_block="User2Entry",
            answers=[schemas.AnswerCreate(question="Q2", content="A2")]
        )
        
        crud.create_journal_entry(db=db_session, entry=entry1_data, user_id=user1.id)
        crud.create_journal_entry(db=db_session, entry=entry2_data, user_id=user2.id)
        
        # Each user should only see their own entries
        user1_entries = crud.get_journal_entries_by_user(db=db_session, user_id=user1.id)
        user2_entries = crud.get_journal_entries_by_user(db=db_session, user_id=user2.id)
        
        assert len(user1_entries) == 1
        assert len(user2_entries) == 1
        assert user1_entries[0].time_block == "User1Entry"
        assert user2_entries[0].time_block == "User2Entry"
