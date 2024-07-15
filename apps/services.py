from apps.models import User
from apps.database import new_session
from apps.schemas import UserGetSchema, UserCreateSchema, UserLoginSchema

from sqlalchemy import select


class UserService:
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
            user = User(**data_dict)
            session.add(user)
            await session.commit()
            return {'messages': 'ok'}

    @classmethod
    async def user_login(cls, data: UserLoginSchema) -> dict:
        async with new_session() as session:
            data_dict = data.model_dump()
            query = select(User).filter(User.username == data_dict['username'],
                                        User.password == data_dict['password'])
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                return {'message': 'ok'}
            return {'message': 'user not found!'}