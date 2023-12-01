from pydantic import BaseModel, EmailStr


# TODO: validate the name
class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str


class Credentials(BaseModel):
    email: EmailStr
    password: str


class Profile(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class UserUpdateInput(BaseModel):
    name: str | None
    email: EmailStr | None
    password: str | None


class OptionResponse(BaseModel):
    id: int
    title: str
    description: str
    votes_count: int


class PollResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    options: list[OptionResponse]

class VoteResponse(BaseModel):
    id: int
    user_id: int
    poll_id: int
    option_id: int

class OptionCreateInput(BaseModel):
    title: str
    description: str


class PollCreateInput(BaseModel):
    title: str
    description: str
    options: list[OptionCreateInput]


class OptionUpdateInput(BaseModel):
    title: str | None
    description: str | None


class PollUpdateInput(BaseModel):
    title: str | None
    description: str | None
