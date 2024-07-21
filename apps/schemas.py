from pydantic import BaseModel, ConfigDict, UUID4


class UserCreateSchema(BaseModel):
    username: str
    fullname: str
    email: str
    password: str


class UserGetSchema(BaseModel):
    id: UUID4
    username: str
    fullname: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: str
    fullname: str
    email: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserForgotPasswordSchema(BaseModel):
    username: str


class UserPasswordResetSchema(BaseModel):
    username: str
    code: int
    password: str
    repeated_password: str


class UserForgotPWSGetSchema(BaseModel):
    id: UUID4
    username: str
    code: int
    user_id: UUID4

    model_config = ConfigDict(from_attributes=True)


class MessageSchema(BaseModel):
    text: str
