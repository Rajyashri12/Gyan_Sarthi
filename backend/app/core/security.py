from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: int,
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[ALGORITHM],
    )