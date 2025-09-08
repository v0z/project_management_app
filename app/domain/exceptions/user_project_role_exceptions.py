from uuid import UUID


class ProjectRoleCreateError(Exception):
    """Raised when an exception occurs while adding a role."""

    def __init__(self, project_id: UUID, role: str):
        self.project_id = project_id
        self.role = role
        super().__init__(f"Could not add role: {self.role} to project {self.project_id}")


class ProjectRoleReadError(Exception):
    """Raised when an exception occurs while getting a role."""

    def __init__(self, user_id: UUID, project_id: UUID):
        self.user_id = user_id
        self.project_id = project_id
        super().__init__(f"Could not read role for user_id '{self.user_id}' on project {self.project_id}")


class ProjectRoleNotAParticipantError(Exception):
    """Raised when an user has no role assigned to a given project."""

    def __init__(self, user_id: UUID, project_id: UUID):
        self.user_id = user_id
        self.project_id = project_id
        super().__init__(f"User with user_id '{self.user_id}' is not a participant of the project {self.project_id}")


class ProjectRoleAddByUsernameError(Exception):
    """Raised when username is not in db, so role cannot be set"""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Could not add role. User with username '{self.username}' is not found")


class ProjectRoleAddNotAuthorizedError(Exception):
    """Raised when username is trying assign a role, but doesn't have the rights"""

    def __init__(self, username: str):
        self.username = username
        super().__init__(
            f"Could not add role. User with username '{self.username}' doesn't have rights to invite participants to this project"
        )


class ProjectRoleAlreadyAssignedError(Exception):
    """Raised when user already has a role on the project"""

    def __init__(self, username: str):
        self.username = username
        super().__init__(
            f"Could not add role. User with username '{self.username}' has already been assigned a role on this project"
        )
