from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from apps.database import Base

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password):
    return pwd_context.hash(password)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
