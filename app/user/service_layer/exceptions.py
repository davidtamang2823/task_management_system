class UserAlreadyExistsError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "User with this email already exists."
        )

class UserNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "User with this email does not exist."
        )

class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Invalid email or password."
        )