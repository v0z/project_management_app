from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from app.domain.enities.user import User


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
