from fastapi import APIRouter, Depends
from typing import Annotated

from apps.schemas import UserCreateSchema, UserLoginSchema
from apps.services import UserService

user_router = APIRouter(prefix='/users', tags=['users'])


@user_router.get('')
async def get_all_users():
    users = await UserService.get_users()
    return users


@user_router.post('')
async def create_user(user: Annotated[UserCreateSchema, Depends()]):
    user = await UserService.create_user(user)
    return user


@user_router.post('/login')
async def user_login(user_data: Annotated[UserLoginSchema, Depends()]):
    result = await UserService.user_login(user_data)
    return result
