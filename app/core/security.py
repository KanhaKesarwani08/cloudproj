from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings # To get SECRET_KEY, ALGORITHM, EXPIRE_MINUTES

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT Token Handling
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

if not SECRET_KEY:
    # This is a critical configuration. Application should not run without it for JWT.
    print("CRITICAL ERROR: JWT SECRET_KEY is not set in settings.")
    # raise ValueError("JWT SECRET_KEY must be set for token generation.") # Or handle as appropriate

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Ensure SECRET_KEY is available before encoding
    if not SECRET_KEY:
        raise ValueError("Cannot create access token: JWT SECRET_KEY is not configured.")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception: Exception) -> Optional[dict]:
    """Verifies a JWT token and returns the payload (claims) or raises credentials_exception."""
    try:
        if not SECRET_KEY:
            print("Error verifying token: JWT SECRET_KEY is not configured.")
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # You can add more validation here, e.g., checking if email/user_id exists in payload
        email: Optional[str] = payload.get("sub") # Assuming "sub" (subject) claim stores the email
        if email is None:
            print("Token verification failed: Subject (sub) claim missing.")
            raise credentials_exception
        # You could also return a Pydantic model like TokenData here
        return payload
    except JWTError as e:
        print(f"JWTError during token verification: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error during token verification: {e}")
        raise credentials_exception 