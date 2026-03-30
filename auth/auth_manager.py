from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from argon2 import PasswordHasher
import logging

# Secret key for JWT
SECRET_KEY = "super_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize Argon2 password hasher
ph = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Initialize logger
logger = logging.getLogger("auth_manager")
logging.basicConfig(level=logging.DEBUG)

# Configure logging to file
file_handler = logging.FileHandler("auth_debug.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Utility functions for password hashing and verification
def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except Exception:
        return False

# Generate JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decode and verify JWT token
def decode_access_token(token: str):
    try:
        logger.debug(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token payload missing 'sub'")
            raise HTTPException(status_code=401, detail="Invalid token")
        logger.debug(f"Token decoded successfully: {payload}")
        return username
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.debug(f"Extracted token: {token}")
    username = decode_access_token(token)
    logger.debug(f"Decoded username: {username}")
    return username