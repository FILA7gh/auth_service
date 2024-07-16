from fastapi import APIRouter, Depends
from typing import Annotated

from pydantic import UUID4

from apps.schemas import UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserForgotPasswordScheme
from apps.services import UserService

user_router = APIRouter(prefix='/users', tags=['users'])


@user_router.get('')
async def get_all_users():
    users = await UserService.get_users()
    return users


@user_router.get('/<uuid:user_id>')
async def get_user_by_id(user_id: UUID4):
    user = await UserService.get_user_by_id(user_id)
    return user


@user_router.post('')
async def create_user(user: Annotated[UserCreateSchema, Depends()]):
    user = await UserService.create_user(user)
    return user


@user_router.put('/<uuid:user_id>')
async def update_user(user_id: UUID4, user: Annotated[UserUpdateSchema, Depends()]):
    updated_user = await UserService.update_user(user_id, user)
    return updated_user


@user_router.delete('/<uuid:user_id>')
async def delete_user(user_id: UUID4):
    deleted_user = await UserService.delete_user(user_id)
    return deleted_user


@user_router.post('/login')
async def user_login(user_data: Annotated[UserLoginSchema, Depends()]):
    result = await UserService.user_login(user_data)
    return result


@user_router.post('/forgot_password')
async def user_forgot_password(username: Annotated[UserForgotPasswordScheme, Depends()]):
    code = await UserService.user_forgot_password(username)
    return code
