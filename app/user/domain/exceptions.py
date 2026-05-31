class PasswordMissingUppercaseError(Exception):

    def __init__(self) -> None:
        super().__init__(
            "Password must contain at least one uppercase letter."
        )


class PasswordMissingLowercaseError(Exception):

    def __init__(self) -> None:
        super().__init__(
            "Password must contain at least one lowercase letter."
        )


class PasswordMissingDigitError(Exception):

    def __init__(self) -> None:
        super().__init__(
            "Password must contain at least one digit."
        )


class PasswordMissingSpecialCharError(Exception):

    def __init__(self) -> None:
        super().__init__(
            "Password must contain at least one special character."
        )


class PasswordContainsNameError(Exception):

    def __init__(self) -> None:
        super().__init__(
            "Password must not contain your first or last name."
        )