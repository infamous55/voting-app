from pydantic import BaseModel, EmailStr


class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str
