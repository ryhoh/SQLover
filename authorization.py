from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")
SECRET_KEY = '53cea8056df0ac6aacae06321bac67b36f1402a8eca5b8b9310b158ec8c76df5'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_user(username: str) -> Optional[UserInDB]:
    try:
        hashed_password = db.read_passwd_by_name_from_user(username)
    except ValueError:
        return None
    return UserInDB(**{'username': username, 'hashed_password': hashed_password})


def get_password_hash(password: str) -> str:
    hashed: str = pwd_context.hash(password)
    return hashed


def verify_password(plain_password: Union[str, bytes], hashed_password: Union[str, bytes]) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
