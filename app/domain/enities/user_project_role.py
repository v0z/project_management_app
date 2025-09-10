from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID


class RoleEnum(str, Enum):
    """Two main roles for project members"""

    OWNER = "owner"
    PARTICIPANT = "participant"


@dataclass
class UserProjectRole:
    """A project role describes the role a user has in a given project"""

    user_id: UUID
    project_id: UUID
    role: RoleEnum
    created_at = datetime.now(UTC)
    username: str | None = ""
