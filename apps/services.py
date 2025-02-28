import random
from datetime import timedelta
from typing import List

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4

from apps.config import ACCESS_TOKEN_EXPIRE_MINUTES
from apps.models import User, UserForgotPassword
from apps.database import new_session
from apps.schemas import UserGetSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserForgotPasswordSchema, \
    UserForgotPWSGetSchema, UserPasswordResetSchema

from sqlalchemy import select, or_


class UserService:
    @classmethod
    async def get_user_by_id(cls, user_id: UUID4) -> UserGetSchema:
        async with new_session() as session:
            query = select(User).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            user_schema = UserGetSchema.model_validate(user)
            return user_schema

    @classmethod
    async def get_users(cls) -> List[UserGetSchema]:
        async with new_session() as session:
            query = select(User)
            result = await session.execute(query)
            users_models = result.scalars().all()
            user_schemas = [UserGetSchema.model_validate(user_model) for user_model in users_models]
            return user_schemas

    @classmethod
    async def create_user(cls, data: UserCreateSchema) -> None:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(User).filter(or_(User.username == data_dict['username'], User.email == data_dict['email']))
            existed_user = await session.execute(query)
            if existed_user.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Username or email is exist!'
                )
            password = data_dict.pop('password')
            user = User(**data_dict)
            user.hashed_password = user.get_password_hash(password)
            session.add(user)
            await session.commit()
            return None

    @classmethod
    async def update_user(cls, user_id: UUID4, data: UserUpdateSchema) -> None:
        async with new_session() as session:
            query = select(User).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            data_dict = data.model_dump()
            query = select(User).filter(or_(
                User.username == data_dict['username'], User.email == data_dict['email']
            ), User.id != user_id)

            existed_user = await session.execute(query)
            if existed_user.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Username or email is exist!'
                )
            for field, value in data_dict.items():
                setattr(user, field, value)

            session.add(user)
            await session.commit()
            return None

    @classmethod
    async def delete_user(cls, user_id: UUID4) -> None:
        async with new_session() as session:
            query = select(User).filter(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            await session.delete(user)
            await session.commit()
            return None

    @classmethod
    async def user_login(cls, data: UserLoginSchema) -> str:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(User).filter(User.username == data_dict['username'])
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            user_json = jsonable_encoder(user)
            authenticated_user = user.authenticate_user(user, data_dict['password'])

            if not authenticated_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Incorrect username or password',
                    headers={'WWW-Authenticate': 'Bearer'}
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = user.create_access_token(
                data={'sub': user_json['username'], 'user_id': user_json['id']},
                expires_delta=access_token_expires
            )
            return access_token

    @classmethod
    async def user_forgot_password(cls, data: UserForgotPasswordSchema) -> int:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(User).filter(User.username == data_dict['username'])
            result = await session.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            generated_code = random.randint(1000, 10000)
            f_pw_query = select(UserForgotPassword).filter(UserForgotPassword.user_id == user.id)
            result = await session.execute(f_pw_query)
            forgot_pw = result.scalars().first()
            if forgot_pw:
                forgot_pw.code = generated_code
            else:
                forgot_pw = UserForgotPassword(username=data_dict['username'], code=generated_code, user_id=user.id)
            session.add(forgot_pw)
            await session.commit()
            return generated_code

    @classmethod
    async def password_reset(cls, data: UserPasswordResetSchema) -> None:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(UserForgotPassword).filter(UserForgotPassword.username == data_dict['username'],
                                                      UserForgotPassword.code == data_dict['code'])
            result = await session.execute(query)
            user_f_pw = result.scalars().first()
            if not user_f_pw:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found!'
                )
            if data_dict['password'] != data_dict['repeated_password']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Passwords is not similar!'
                )
            user_query = select(User).filter(User.id == user_f_pw.user_id)
            result = await session.execute(user_query)
            user = result.scalars().first()
            user.hashed_password = user.get_password_hash(data_dict['password'])
            session.add(user)
            await session.commit()
            return None


class UserForgotPWService:
    @classmethod
    async def user_forgot_pw_get_all(cls) -> List[UserForgotPWSGetSchema]:
        async with new_session() as session:
            query = select(UserForgotPassword)
            result = await session.execute(query)
            users_forgotten = result.scalars().all()
            users_forgotten_schemes = [
                UserForgotPWSGetSchema.model_validate(user_forgot) for user_forgot in users_forgotten
            ]
            return users_forgotten_schemes
