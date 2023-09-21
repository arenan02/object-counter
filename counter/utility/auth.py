from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional

# Define JWT settings
SECRET_KEY = '202e5982c62f359a23c71f6cf9c0c5adcf25917cc7c77216ffb1ebe7a50e8dbf'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create a PasswordContext for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the User model
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Define the Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Define OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a fake user for demonstration purposes
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "$2b$12$cy9djSvKBgjbTKFv3QfCSOxCTHhBCaSQ.Pu5PEBKL5KthCHdCWiM2",
        "email": "test@example.com",
        "full_name": "Test User",
        "disabled": False,
    }
}

# Create access token function
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# Authenticate and generate a token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

    
