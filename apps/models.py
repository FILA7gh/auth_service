import uuid

from datetime import timedelta, datetime
from typing import Optional

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import Column, String, UUID, Integer, ForeignKey
from sqlalchemy.orm import relationship

from apps.config import SECRET_KEY, ALGORITHM
from apps.database import Base

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(user, password):
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
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    username = Column(String)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    forgot_password = relationship('UserForgotPassword', uselist=False, back_populates='user')


class UserForgotPassword(Base):
    __tablename__ = 'users_forgot_password'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    username = Column(String)
    code = Column(Integer)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship('User', back_populates='forgot_password')
