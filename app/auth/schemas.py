from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=72)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
