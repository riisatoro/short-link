from pydantic import BaseModel


class ReadUser(BaseModel):
    id: int
    username: str
    email: str


class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    repeat_password: str
