from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
