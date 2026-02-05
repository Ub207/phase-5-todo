# routers/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from auth_utils import hash_password, verify_password, create_access_token, get_db
from schemas import UserCreate, UserLogin, AuthResponse, UserResponse
from models import User
from exceptions import ConflictException, UnauthorizedException

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ConflictException(detail="Email already registered")

    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    token = create_access_token(data={"sub": new_user.id, "email": new_user.email})

    return AuthResponse(
        user=UserResponse.from_orm(new_user),
        token=token
    )


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise UnauthorizedException(detail="Invalid email or password")

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException(detail="Invalid email or password")

    # Create access token
    token = create_access_token(data={"sub": user.id, "email": user.email})

    return AuthResponse(
        user=UserResponse.from_orm(user),
        token=token
    )
