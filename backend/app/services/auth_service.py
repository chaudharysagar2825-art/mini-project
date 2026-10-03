from sqlalchemy.orm import Session

from app.models.user import User
from app.security.hashing import verify_password
from app.security.tokens import create_access_token


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def login_user(
    db: Session,
    username: str,
    password: str,
) -> str | None:

    user = authenticate_user(
        db=db,
        username=username,
        password=password,
    )

    if user is None:
        return None

    return create_access_token(
        subject=str(user.id),
        role=user.role,
    )