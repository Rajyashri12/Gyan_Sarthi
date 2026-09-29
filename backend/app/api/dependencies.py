from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db),
):

    token = credentials.credentials

    print("\n========== AUTH DEBUG ==========")
    print("TOKEN RECEIVED:", token[:30] + "...")
    
    try:

        payload = decode_access_token(token)

        print("JWT PAYLOAD:", payload)

        user_id = payload.get("sub")

        print("USER ID:", user_id)

        if not user_id:

            raise HTTPException(
                status_code=401,
                detail="Token does not contain user ID.",
            )

    except Exception as e:

        print("JWT ERROR:", repr(e))

        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive.",
        )

    print("AUTH SUCCESS:", user.email)
    print("================================\n")

    return user