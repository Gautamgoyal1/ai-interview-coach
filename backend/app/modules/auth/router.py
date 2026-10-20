from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from fastapi import Request
from app.core.rate_limit import (
    check_login_rate_limit,
    clear_login_attempts,
    record_failed_login,
)
from app.db.models.user import User
from app.db.session import get_db
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    existing_user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    password = request.password.get_secret_value()

    user = User(
        email=request.email,
        password_hash=hash_password(password),
    )
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        # Also handles concurrent registrations for the same email.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from None

    return UserResponse.model_validate(user)



@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    client_ip = (
        http_request.client.host
        if http_request.client is not None
        else "unknown"
    )

    check_login_rate_limit(client_ip)

    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    password = request.password.get_secret_value()

    if user is None or not verify_password(
        password,
        user.password_hash,
    ):
        record_failed_login(client_ip)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clear_login_attempts(client_ip)

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)



@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)