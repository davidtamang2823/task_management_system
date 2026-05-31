import re
from pydantic import EmailStr, Field, field_validator, model_validator

from common.models import CommonBaseModel
from user.domain.exceptions import (
    PasswordContainsNameError,
    PasswordMissingDigitError,
    PasswordMissingLowercaseError,
    PasswordMissingSpecialCharError,
    PasswordMissingUppercaseError,
)

class UserEmail(CommonBaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

class UserVerificationToken(CommonBaseModel):
    token: str = Field(..., min_length=1, max_length=255)

class UserCredentials(UserEmail):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise PasswordMissingUppercaseError()
        if not re.search(r"[a-z]", v):
            raise PasswordMissingLowercaseError()
        if not re.search(r"\d", v):
            raise PasswordMissingDigitError()
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise PasswordMissingSpecialCharError()
        return v

class User(UserCredentials):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role_id: int | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_and_capitalize(cls, v: str) -> str:
        return v.strip().capitalize()