from fastapi import APIRouter, Depends, status
from typing import Annotated, List

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from starlette.responses import JSONResponse

from apps.schemas import UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserForgotPasswordScheme, \
    UserPasswordReset, UserGetSchema
from apps.services import UserService, UserForgotPWService

user_router = APIRouter(prefix='/users', tags=['users'])
user_forgot_pw_router = APIRouter(prefix='/users_forgot_pw', tags=['users_forgot_passwords'])


@user_router.get('', response_model=List[UserGetSchema])
async def get_all_users() -> JSONResponse:
    users = await UserService.get_users()
    users_json = jsonable_encoder(users)
    response = JSONResponse(content={'data': users_json}, status_code=status.HTTP_200_OK)
    return response


@user_router.get('/{user_id}', response_model=UserGetSchema)
async def get_user_by_id(user_id: UUID4) -> JSONResponse:
    user = await UserService.get_user_by_id(user_id)
    user_json = jsonable_encoder(user)
    response = JSONResponse(content={'data': user_json}, status_code=status.HTTP_200_OK)
    return response


@user_router.post('', response_model=dict)
async def create_user(user: Annotated[UserCreateSchema, Depends()]) -> JSONResponse:
    await UserService.create_user(user)
    response = JSONResponse(content={'message': 'user is created successfully'},
                            status_code=status.HTTP_201_CREATED)
    return response


@user_router.put('/{user_id}', response_model=dict)
async def update_user(user_id: UUID4, user: Annotated[UserUpdateSchema, Depends()]) -> JSONResponse:
    await UserService.update_user(user_id, user)
    response = JSONResponse(content={'message': 'user updated successfully!'}, status_code=status.HTTP_200_OK)
    return response


@user_router.delete('/{user_id}', response_model=dict)
async def delete_user(user_id: UUID4) -> JSONResponse:
    await UserService.delete_user(user_id)
    response = JSONResponse(content={'message': 'User deleted successfully'},
                            status_code=status.HTTP_204_NO_CONTENT)
    return response


@user_router.post('/login', response_model=dict)
async def user_login(user_data: Annotated[UserLoginSchema, Depends()]):
    access_token = await UserService.user_login(user_data)
    response = JSONResponse(content={'message': 'login successful'}, status_code=status.HTTP_200_OK)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return response


@user_router.post('/forgot_password', response_model=dict)
async def user_forgot_password(username: Annotated[UserForgotPasswordScheme, Depends()]) -> JSONResponse:
    code = await UserService.user_forgot_password(username)
    response = JSONResponse(content={'code': code}, status_code=status.HTTP_201_CREATED)
    return response


@user_router.post('/reset_password', response_model=List[UserForgotPasswordScheme])
async def reset_password(data: Annotated[UserPasswordReset, Depends()]) -> JSONResponse:
    await UserService.password_reset(data)
    response = JSONResponse(content={'message': 'password is changed successfully'},
                            status_code=status.HTTP_200_OK)
    return response


@user_forgot_pw_router.get('', response_model=UserForgotPasswordScheme)
async def get_all_users_forgot_pw() -> JSONResponse:
    forgot_pw_users = await UserForgotPWService.user_forgot_pw_get_all()
    forgot_pw_users_dict = jsonable_encoder(forgot_pw_users)
    response = JSONResponse(content={'data': forgot_pw_users_dict}, status_code=status.HTTP_200_OK)
    return response
