from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str