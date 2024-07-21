from fastapi import APIRouter, Depends, status
from typing import Annotated, List

from pydantic import UUID4
from starlette.responses import JSONResponse

from apps.rabbit import Rabbit
from apps.schemas import UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserForgotPasswordSchema, \
    UserPasswordResetSchema, UserGetSchema, UserForgotPWSGetSchema, MessageSchema
from apps.services import UserService, UserForgotPWService

user_router = APIRouter(prefix='/users', tags=['users'])
user_forgot_pw_router = APIRouter(prefix='/users_forgot_pw', tags=['users_forgot_passwords'])


@user_router.get('', response_model=List[UserGetSchema], status_code=status.HTTP_200_OK)
async def get_all_users():
    users = await UserService.get_users()
    return users


@user_router.get('/{user_id}', response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: UUID4) -> UserGetSchema:
    user = await UserService.get_user_by_id(user_id)
    return user


@user_router.post('')
async def create_user(user: Annotated[UserCreateSchema, Depends()]) -> JSONResponse:
    await UserService.create_user(user)
    response = JSONResponse(content={'message': 'user is created successfully'},
                            status_code=status.HTTP_201_CREATED)
    return response


@user_router.put('/{user_id}')
async def update_user(user_id: UUID4, user: Annotated[UserUpdateSchema, Depends()]) -> JSONResponse:
    await UserService.update_user(user_id, user)
    response = JSONResponse(content={'message': 'user updated successfully!'},
                            status_code=status.HTTP_200_OK)
    return response


@user_router.delete('/{user_id}')
async def delete_user(user_id: UUID4) -> JSONResponse:
    await UserService.delete_user(user_id)
    response = JSONResponse(content={'message': 'User deleted successfully'},
                            status_code=status.HTTP_204_NO_CONTENT)
    return response


@user_router.post('/login')
async def user_login(user_data: Annotated[UserLoginSchema, Depends()]):
    access_token = await UserService.user_login(user_data)
    response = JSONResponse(content={'message': 'login successful'}, status_code=status.HTTP_200_OK)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return response


@user_router.post('/forgot_password')
async def user_forgot_password(username: Annotated[UserForgotPasswordSchema, Depends()]) -> JSONResponse:
    code = await UserService.user_forgot_password(username)
    response = JSONResponse(content={'code': code}, status_code=status.HTTP_201_CREATED)
    return response


@user_router.post('/reset_password')
async def reset_password(data: Annotated[UserPasswordResetSchema, Depends()]) -> JSONResponse:
    await UserService.password_reset(data)
    response = JSONResponse(content={'message': 'password is changed successfully'},
                            status_code=status.HTTP_200_OK)
    return response


@user_forgot_pw_router.get('', response_model=List[UserForgotPWSGetSchema])
async def get_all_users_forgot_pw() -> List[UserForgotPWSGetSchema]:
    forgot_pw_users = await UserForgotPWService.user_forgot_pw_get_all()
    return forgot_pw_users


@user_router.post('/send_message')
async def send_message(message: Annotated[MessageSchema, Depends()]) -> JSONResponse:
    await Rabbit.send_message(message)
    response = JSONResponse(content={'message': 'message is sanded'}, status_code=status.HTTP_200_OK)
    return response
