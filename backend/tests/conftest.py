"""Test configuration for Manas Setu backend.

Configures an isolated temporary file-based SQLite database for tests.
Ensures clean session management, dependency overrides, and per-test isolation
without touching development or production databases.
"""

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Dedicated temporary SQLite database file for testing
TEST_DB_PATH = Path(tempfile.gettempdir()) / f"manas_setu_test_{os.getpid()}.sqlite"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH.as_posix()}"
TEST_JWT_SECRET = "test-secret-key-for-testing-purposes-min-32-chars-long"

os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Explicitly override settings values to guarantee isolation
settings.database_url = TEST_DB_URL
settings.jwt_secret_key = TEST_JWT_SECRET

from app.database import Base, get_db
from app.main import app
from app.models import Consent, User, VictimCase
from app.security.hashing import hash_password
from app.security.tokens import create_access_token

TEST_ENGINE = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(TEST_ENGINE, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(
    bind=TEST_ENGINE,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables at session start and clean up the database file at session end."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    TEST_ENGINE.dispose()
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except OSError:
            pass


@pytest.fixture(autouse=True)
def clean_database():
    """Ensure every test starts with an empty database."""
    with TEST_ENGINE.begin() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")
    yield


@pytest.fixture()
def db():
    """Provide a test database session for setting up test data."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_db():
    """Override FastAPI get_db dependency to use the isolated test database."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    """Provide a test HTTP client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def victim_user(db):
    """Create and return a test victim user."""
    user = User(
        username="testvictim",
        password_hash=hash_password("TestPass123!"),
        role="victim",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def admin_user(db):
    """Create and return a test admin user."""
    user = User(
        username="testadmin",
        password_hash=hash_password("AdminPass123!"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def other_victim_user(db):
    """Create and return a second victim user for cross-user access tests."""
    user = User(
        username="othervictim",
        password_hash=hash_password("OtherPass123!"),
        role="victim",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def victim_case(db, victim_user):
    """Create and return a test case belonging to victim_user."""
    case = VictimCase(
        case_code="CASE-TEST001",
        user_id=victim_user.id,
        status="active",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@pytest.fixture()
def other_victim_case(db, other_victim_user):
    """Create and return a test case belonging to other_victim_user."""
    case = VictimCase(
        case_code="CASE-OTHER001",
        user_id=other_victim_user.id,
        status="active",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@pytest.fixture()
def active_consent(db, victim_case):
    """Create active consent for victim_case so check-ins can be submitted."""
    consent = Consent(
        case_id=victim_case.id,
        status="granted",
        version="1.0",
        scope="mental_health_checkins",
        channel="web",
        consented_at=datetime.now(timezone.utc),
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


@pytest.fixture()
def victim_token(victim_user):
    """Generate a JWT token for victim_user."""
    return create_access_token(
        subject=str(victim_user.id),
        role=victim_user.role,
    )


@pytest.fixture()
def admin_token(admin_user):
    """Generate a JWT token for admin_user."""
    return create_access_token(
        subject=str(admin_user.id),
        role=admin_user.role,
    )


@pytest.fixture()
def other_victim_token(other_victim_user):
    """Generate a JWT token for other_victim_user."""
    return create_access_token(
        subject=str(other_victim_user.id),
        role=other_victim_user.role,
    )


@pytest.fixture()
def caseworker_user(db):
    """Create and return a test caseworker user."""
    user = User(
        username="testcaseworker",
        password_hash=hash_password("CaseworkerPass123!"),
        role="caseworker",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def caseworker_token(caseworker_user):
    """Generate a JWT token for caseworker_user."""
    return create_access_token(
        subject=str(caseworker_user.id),
        role=caseworker_user.role,
    )


def auth_header(token: str) -> dict:
    """Build an Authorization header dictionary."""
    return {"Authorization": f"Bearer {token}"}

