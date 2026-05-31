from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from user.common.dependencies import get_user_service
from user.domain.commands import CreateUserCommand, AuthenticateUserCommand
from user.service_layer.services import AbstractUserService
from user.domain import exceptions as user_domain_exceptions
from user.service_layer import exceptions as user_service_layer_exceptions
from pydantic_core import ValidationError

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.get("/")
async def list_users(request: Request, user_service: AbstractUserService = Depends(get_user_service)):
    response_data = await user_service.list_users(
        current_user_id=request.state.user_id,
        current_user_role_id=request.state.role_id,
        filter={}
    )
    return response_data


@user_router.post("/register")
async def register_user(request: Request, user_service: AbstractUserService = Depends(get_user_service)):
    try:
        request_data = await request.json()
        create_command = CreateUserCommand(**request_data)
        return await user_service.create_user(create_command)
    except (
        user_service_layer_exceptions.UserAlreadyExistsError,
        user_domain_exceptions.PasswordMissingUppercaseError,
        user_domain_exceptions.PasswordMissingLowercaseError,
        user_domain_exceptions.PasswordMissingDigitError,
        user_domain_exceptions.PasswordMissingSpecialCharError,
        user_domain_exceptions.PasswordContainsNameError,
        ValidationError
    )as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= str(e))

@user_router.post("/login")
async def login_user(request: Request, user_service: AbstractUserService = Depends(get_user_service)):
    try:
        request_data = await request.json()
        authenticate_command = AuthenticateUserCommand(**request_data)
        return await user_service.authenticate_user(authenticate_command)
    except (
        user_service_layer_exceptions.UserNotFoundError, 
        user_service_layer_exceptions.InvalidCredentialsError,
        ValidationError
    ) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,  detail=str(e))

