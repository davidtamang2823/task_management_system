from pydantic import Field
from common.models import CommonBaseModel
from user.domain.models import User, UserCredentials, UserVerificationToken, UserEmail

class CreateUserCommand(User):
    hashed_password: str | None = None 

class AuthenticateUserCommand(CommonBaseModel):
    email: str
    password: str