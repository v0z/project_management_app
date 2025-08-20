from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class Document:
	pass


@dataclass
class Project:
	"""Project entity"""

	id: UUID
	name: str
	description: str
	owner: UUID
	created_at: datetime

	def is_owned_by(self, user_id: UUID):
		return self.owner == user_id
