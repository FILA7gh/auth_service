from pydantic import BaseModel, ConfigDict


class UserGetSchema(BaseModel):
    user_id: int
    username: str
    fullname: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserGetSchema):
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str
