from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("Name must contain at least 2 non-space characters")
        return normalized


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )