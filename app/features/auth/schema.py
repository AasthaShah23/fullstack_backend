from pydantic import BaseModel, EmailStr, Field


# Request schemas
class SignUpRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Jane Doe"],
        description="Full display name of the user.",
    )
    email: EmailStr = Field(
        ...,
        examples=["jane@example.com"],
        description="Unique email address used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["Str0ng!Pass"],
        description="Plain-text password (will be hashed before storage).",
    )


# Response schemas
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}

# Response schema for the signup route
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
