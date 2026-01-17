"""
Authentication Routes
Handles user registration, login, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger

from app.config import settings
from app.models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.learner_profile import LearnerProfile


router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme - auto_error=False allows optional auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for optional auth)"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user = await User.get(user_id)
        return user
    except JWTError:
        return None


# Pre-computed bcrypt hash for "guest123" to avoid bcrypt compatibility issues
GUEST_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGj1vt/v3Aq"


async def get_or_create_guest_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get authenticated user or create/get a guest user for development"""
    if token:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("sub")
            if user_id:
                user = await User.get(user_id)
                if user:
                    return user
        except JWTError:
            pass
    
    # Get or create guest user for development
    guest_email = "guest@edusynapse.dev"
    guest_user = await User.find_one(User.email == guest_email)
    
    if not guest_user:
        guest_user = User(
            email=guest_email,
            username="guest",
            hashed_password=GUEST_PASSWORD_HASH,  # Pre-computed hash
            full_name="Guest User",
            is_active=True,
        )
        await guest_user.insert()
        
        # Create learner profile for guest
        profile = LearnerProfile(user_id=str(guest_user.id))
        await profile.insert()
        guest_user.learner_profile_id = str(profile.id)
        await guest_user.save()
        
        logger.info("Created guest user for development")
    
    return guest_user


def user_to_response(user: User) -> UserResponse:
    """Convert User document to UserResponse"""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        preferences=user.preferences,
        created_at=user.created_at,
        total_sessions=user.total_sessions,
        total_questions_answered=user.total_questions_answered,
        total_study_time_minutes=user.total_study_time_minutes,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    
    # Check if email already exists
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await User.find_one(User.username == user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    await user.insert()
    
    # Create learner profile
    profile = LearnerProfile(user_id=str(user.id))
    await profile.insert()
    
    # Update user with profile reference
    user.learner_profile_id = str(profile.id)
    await user.save()
    
    logger.info(f"New user registered: {user.email}")
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    
    # Find user by email
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    logger.info(f"User logged in: {user.email}")
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_or_create_guest_user)):
    """Get current user profile (returns guest user if not authenticated)"""
    return user_to_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    
    if full_name is not None:
        current_user.full_name = full_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return user_to_response(current_user)


@router.put("/preferences")
async def update_preferences(
    preferred_modality: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    daily_goal_minutes: Optional[int] = None,
    notification_enabled: Optional[bool] = None,
    theme: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    
    if preferred_modality is not None:
        current_user.preferences.preferred_modality = preferred_modality
    if preferred_difficulty is not None:
        current_user.preferences.preferred_difficulty = preferred_difficulty
    if daily_goal_minutes is not None:
        current_user.preferences.daily_goal_minutes = daily_goal_minutes
    if notification_enabled is not None:
        current_user.preferences.notification_enabled = notification_enabled
    if theme is not None:
        current_user.preferences.theme = theme
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return {"success": True, "preferences": current_user.preferences}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user (client should discard token)"""
    logger.info(f"User logged out: {current_user.email}")
    return {"success": True, "message": "Successfully logged out"}
