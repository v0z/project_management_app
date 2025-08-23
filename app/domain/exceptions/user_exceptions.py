class UserAlreadyExistsError(Exception):
    """Raised when a user with the same username already exists."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User with username: {self.username} already exists")


class UserWithEmailAlreadyExistsError(Exception):
    """Raised when a user with the same email already exists."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email: {self.email} already exists")
