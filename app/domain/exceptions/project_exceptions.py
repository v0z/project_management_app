from uuid import UUID


class ProjectNotFoundError(Exception):
	"""Raised when a Project is not found"""

	def __init__(self, project_id: UUID):
		self.project_id = project_id
		super().__init__(f"Project with id: {self.project_id} is not found")


class ProjectPermissionError(Exception):
	"""Raised when a Project does not belong to user."""

	def __init__(self):
		super().__init__("You do not have permission to modify this project")


class ProjectUpdateFailed(Exception):
	"""Raised when a Project update went sideways"""

	def __init__(self):
		super().__init__("Project update failed")
