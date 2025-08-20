from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.enities.project import Project


class ProjectRepository(ABC):
	"""An abstract ProjectRepository interface"""

	@abstractmethod
	def list_by_user(self, user_id: UUID) -> List[Project]:
		pass

	@abstractmethod
	def add(self, project: Project) -> Project:
		pass

	@abstractmethod
	def get_by_id(self, project_id: UUID) -> Optional[Project]:
		pass

	@abstractmethod
	def update(self, project_id: UUID, data) -> Optional[Project]:
		pass

	@abstractmethod
	def delete(self, project_id: UUID) -> bool:
		pass
