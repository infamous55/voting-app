from pydantic import BaseModel, EmailStr


# TODO: validate the name
class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str


class Credentials(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
