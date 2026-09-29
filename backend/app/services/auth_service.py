from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:

    @staticmethod
    def register(
        db: Session,
        name: str,
        email: str,
        password: str,
    ):

        existing_user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if existing_user:

            raise ValueError(
                "Email already registered."
            )

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(
                password
            ),
            role="student",
            is_active=True,
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        token = create_access_token(
            user.id
        )

        return user, token

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):

        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if not user:

            raise ValueError(
                "Invalid email or password."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):

            raise ValueError(
                "Invalid email or password."
            )

        if not user.is_active:

            raise ValueError(
                "User account is inactive."
            )

        token = create_access_token(
            user.id
        )

        return user, token