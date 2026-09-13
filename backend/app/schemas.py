from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=6)
    phone: str | None = None
    
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str | None = None
    
    
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None