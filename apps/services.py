import random
from datetime import timedelta

from fastapi import HTTPException, status
from pydantic import UUID4

from apps.config import ACCESS_TOKEN_EXPIRE_MINUTES
from apps.models import User, authenticate_user, create_access_token, get_password_hash, UserForgotPassword
from apps.database import new_session
from apps.schemas import UserGetSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserForgotPasswordScheme

from sqlalchemy import select, or_


class UserService:
    @classmethod
    async def get_user_by_id(cls, user_id: UUID4):
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
    async def get_users(cls) -> list:
        async with new_session() as session:
            query = select(User)
            result = await session.execute(query)
            users_models = result.scalars().all()
            user_schemas = [UserGetSchema.model_validate(user_model) for user_model in users_models]
            return user_schemas

    @classmethod
    async def create_user(cls, data: UserCreateSchema) -> dict:
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
            user.hashed_password = get_password_hash(password)
            session.add(user)
            await session.commit()
            return {'message': 'user is created successfully'}

    @classmethod
    async def update_user(cls, user_id: UUID4, data: UserUpdateSchema) -> dict:
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
            return {'message': 'user updated successfully!'}

    @classmethod
    async def delete_user(cls, user_id: UUID4) -> dict:
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
            return {'message': 'User deleted successfully'}

    @classmethod
    async def user_login(cls, data: UserLoginSchema) -> dict:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(User).filter(User.username == data_dict['username'])
            result = await session.execute(query)
            user = result.scalars().first()
            authenticated_user = authenticate_user(user, data_dict['password'])

            if not authenticated_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Incorrect username or password',
                    headers={'WWW-Authenticate': 'Bearer'}
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
            return {'access_token': access_token, 'token_type': 'bearer'}

    @classmethod
    async def user_forgot_password(cls, username: UserForgotPasswordScheme) -> dict:
        async with new_session() as session:
            query = select(User).filter(User.username == username)
            result = await session.execute(query)
            user = result.scalars().all()
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
                forgot_pw = UserForgotPassword(username=username, code=generated_code, user_id=user.id)
            session.add(forgot_pw)
            await session.commit()
            return {'code': generated_code}
