from uuid import UUID


class ProjectNotFoundError(Exception):
    """Raised when a Project is not found"""

    def __init__(self, project_id: UUID):
        self.project_id = project_id
        super().__init__(f"Project with id: {self.project_id} is not found")


class ProjectPermissionError(Exception):
    """Raised when a Project does not belong to user."""

    def __init__(self):
        super().__init__("User do not have permission to view or modify this project")


class ProjectUpdateError(Exception):
    """Raised when a Project update went sideways"""

    def __init__(self, message: str):
        super().__init__(f"Project update failed: {message}")
        self.message = message


class ProjectCreateError(Exception):
    """Raised when Project creation failed"""

    def __init__(self, message: str):
        super().__init__(f"Project creation failed: {message}")
        self.message = message


class ProjectRetrieveError(Exception):
    """Raised when couldn't return Projects"""

    def __init__(self, message: str):
        super().__init__(f"Project retrieval failed: {message}")
        self.message = message


class ProjectDeleteError(Exception):
    """Raised when couldn't delete a Project"""

    def __init__(self, message: str):
        super().__init__(f"Could not delete the project: {message}")
        self.message = message
