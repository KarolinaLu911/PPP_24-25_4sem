from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    age: int

class UserOut(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        orm_mode = True
