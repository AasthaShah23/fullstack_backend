from pydantic import BaseModel, Field

from app.features.auth.schema import UserResponse


class UserListResponse(BaseModel):
    total: int = Field(..., description="Total count of users in database.")
    users: list[UserResponse] = Field(..., description="List of user profiles.")

