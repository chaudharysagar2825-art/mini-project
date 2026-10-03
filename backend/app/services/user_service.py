from sqlalchemy.orm import Session

from app.models.user import User
from app.security.hashing import hash_password


def create_user(
    db: Session,
    username: str,
    password: str,
    role: str,
) -> User:

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user is not None:
        raise ValueError("Username already exists")

    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: int,
) -> User | None:

    return db.get(User, user_id)


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def deactivate_user(
    db: Session,
    user_id: int,
) -> User:

    user = db.get(User, user_id)

    if user is None:
        raise ValueError("User not found")

    user.is_active = False

    db.commit()
    db.refresh(user)

    return user